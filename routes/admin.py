"""
Admin Routes - Administrative user and system management
Demonstrates extending fasthtml-auth with admin functionality
"""

from fasthtml.common import *
from monsterui.all import *
from datetime import datetime

def register_admin_routes(app, auth, todo_db):
    """Register admin-only routes with role protection"""
    
    @app.route("/admin")
    @auth.require_admin()
    def admin_dashboard(req):
        """Admin dashboard with system overview"""
        user = req.scope['user']
        system_stats = todo_db.get_system_stats()
        recent_todos = todo_db.get_all_todos_admin(limit=10)
        
        return render_admin_dashboard(user, system_stats, recent_todos)
    
    @app.route("/admin/users")
    @auth.require_admin()
    def user_management(req):
        """User management page"""
        user = req.scope['user']
        users = auth.user_repo.list_all()
        
        success = req.query_params.get('success')
        error = req.query_params.get('error')
        
        return render_user_management(user, users, success, error)
    
    @app.route("/admin/users/{user_id:int}/role", methods=["POST"])
    @auth.require_admin()
    async def change_user_role(req, user_id: int):
        """Change user role"""
        current_user = req.scope['user']
        form = await req.form()
        new_role = form.get('role')
        
        if new_role not in ['user', 'manager', 'admin']:
            return RedirectResponse('/admin/users?error=invalid_role', status_code=303)
        
        # Prevent admin from demoting themselves
        if user_id == current_user.id and new_role != 'admin':
            return RedirectResponse('/admin/users?error=cannot_demote_self', status_code=303)
        
        success = auth.user_repo.update(user_id, role=new_role)
        
        if success:
            return RedirectResponse('/admin/users?success=role_updated', status_code=303)
        else:
            return RedirectResponse('/admin/users?error=role_update_failed', status_code=303)
    
    @app.route("/admin/users/{user_id:int}/toggle", methods=["POST"])
    @auth.require_admin()
    def toggle_user_status(req, user_id: int):
        """Toggle user active status"""
        current_user = req.scope['user']
        
        # Prevent admin from deactivating themselves
        if user_id == current_user.id:
            return RedirectResponse('/admin/users?error=cannot_deactivate_self', status_code=303)
        
        target_user = auth.user_repo.get_by_id(user_id)
        if not target_user:
            return RedirectResponse('/admin/users?error=user_not_found', status_code=303)
        
        new_status = not target_user.active
        success = auth.user_repo.update(user_id, active=new_status)
        
        if success:
            action = 'activated' if new_status else 'deactivated'
            return RedirectResponse(f'/admin/users?success=user_{action}', status_code=303)
        else:
            return RedirectResponse('/admin/users?error=status_update_failed', status_code=303)
    
    @app.route("/admin/users/{user_id:int}/delete", methods=["POST"])
    @auth.require_admin()
    def delete_user(req, user_id: int):
        """Delete user and all their todos"""
        current_user = req.scope['user']
        
        # Prevent admin from deleting themselves
        if user_id == current_user.id:
            return RedirectResponse('/admin/users?error=cannot_delete_self', status_code=303)
        
        target_user = auth.user_repo.get_by_id(user_id)
        if not target_user:
            return RedirectResponse('/admin/users?error=user_not_found', status_code=303)
        
        try:
            # Delete user's todos first
            todo_db.delete_user_todos(user_id)
            
            # Delete user from auth database
            # Note: This functionality should be added to fasthtml-auth library
            auth.user_repo.db.t.user.delete(user_id)
            
            return RedirectResponse('/admin/users?success=user_deleted', status_code=303)
        except Exception as e:
            print(f"Error deleting user: {e}")
            return RedirectResponse('/admin/users?error=delete_failed', status_code=303)
    
    @app.route("/admin/todos")
    @auth.require_admin()
    def all_todos_management(req):
        """View and manage all todos across users"""
        user = req.scope['user']
        all_todos = todo_db.get_all_todos_admin(limit=50)
        
        return render_todos_management(user, all_todos)
    
    @app.route("/admin/system")
    @auth.require_admin()
    def system_info(req):
        """System information and statistics"""
        user = req.scope['user']
        system_stats = todo_db.get_system_stats()
        users = auth.user_repo.list_all()
        
        return render_system_info(user, system_stats, users)

def render_admin_dashboard(user, system_stats, recent_todos):
    """Render admin dashboard"""
    return Title("Admin Dashboard"), \
        AdminNav(user), \
        Container(
            H1("Admin Dashboard", cls="text-3xl font-bold mb-8"),
            
            # System Stats Overview
            Grid(
                AdminStatsCard("Total Users", sum(system_stats.get('user_stats', {}).values()), "👥"),
                AdminStatsCard("Active Users", system_stats.get('active_users', 0), "🟢"),
                AdminStatsCard("Total Todos", sum(system_stats.get('todo_stats', {}).values()), "📝"),
                AdminStatsCard("Completed", system_stats.get('todo_stats', {}).get('completed', 0), "✅"),
                cols=2, cols_md=4, cls="gap-4 mb-8"
            ),
            
            # Quick Actions
            Card(
                CardHeader(H2("Quick Actions")),
                CardBody(
                    Grid(
                        A("Manage Users", href="/admin/users", cls=(ButtonT.primary, "w-full")),
                        A("View All Todos", href="/admin/todos", cls=(ButtonT.secondary, "w-full")),
                        A("System Info", href="/admin/system", cls=(ButtonT.secondary, "w-full")),
                        A("Back to Dashboard", href="/dashboard", cls=(ButtonT.outline, "w-full")),
                        cols=2, cols_md=4, cls="gap-4"
                    )
                ),
                cls="mb-8"
            ),
            
            # Recent Activity
            Card(
                CardHeader(H2("Recent Todos (All Users)")),
                CardBody(
                    recent_todos_table(recent_todos) if recent_todos else 
                    P("No todos found.", cls="text-muted-foreground text-center py-8")
                )
            ),
            
            cls=ContainerT.xl
        )

def render_user_management(user, users, success=None, error=None):
    """Render user management page"""
    # Success/error messages
    messages = {
        'role_updated': 'User role updated successfully',
        'user_activated': 'User activated successfully', 
        'user_deactivated': 'User deactivated successfully',
        'user_deleted': 'User deleted successfully',
        'invalid_role': 'Invalid role specified',
        'cannot_demote_self': 'You cannot change your own role',
        'cannot_deactivate_self': 'You cannot deactivate your own account',
        'cannot_delete_self': 'You cannot delete your own account',
        'user_not_found': 'User not found',
        'role_update_failed': 'Failed to update user role',
        'status_update_failed': 'Failed to update user status',
        'delete_failed': 'Failed to delete user'
    }
    
    return Title("User Management - Admin"), \
        AdminNav(user), \
        Container(
            DivFullySpaced(
                H1("User Management", cls="text-3xl font-bold"),
                A("← Back to Admin", href="/admin", cls=ButtonT.secondary)
            ),
            
            Alert(messages.get(success), cls=AlertT.success) if success else None,
            Alert(messages.get(error), cls=AlertT.error) if error else None,
            
            Card(
                CardHeader(
                    DivFullySpaced(
                        H2("All Users"),
                        P(f"{len(users)} total users", cls="text-muted-foreground")
                    )
                ),
                CardBody(
                    users_table(users, current_user=user)
                ),
                cls="mt-6"
            ),
            
            cls=ContainerT.xl
        )

def render_todos_management(user, all_todos):
    """Render todos management page"""
    return Title("All Todos - Admin"), \
        AdminNav(user), \
        Container(
            DivFullySpaced(
                H1("All Todos", cls="text-3xl font-bold"),
                A("← Back to Admin", href="/admin", cls=ButtonT.secondary)
            ),
            
            Card(
                CardHeader(
                    DivFullySpaced(
                        H2("System-wide Todo Overview"),
                        P(f"{len(all_todos)} recent todos", cls="text-muted-foreground")
                    )
                ),
                CardBody(
                    admin_todos_table(all_todos) if all_todos else
                    P("No todos found.", cls="text-muted-foreground text-center py-8")
                ),
                cls="mt-6"
            ),
            
            cls=ContainerT.xl
        )

def render_system_info(user, system_stats, users):
    """Render system information page"""
    user_stats = system_stats.get('user_stats', {})
    todo_stats = system_stats.get('todo_stats', {})
    
    return Title("System Information - Admin"), \
        AdminNav(user), \
        Container(
            DivFullySpaced(
                H1("System Information", cls="text-3xl font-bold"),
                A("← Back to Admin", href="/admin", cls=ButtonT.secondary)
            ),
            
            Grid(
                # User Statistics
                Card(
                    CardHeader(H2("User Statistics")),
                    CardBody(
                        Grid(
                            StatRow("Total Users", sum(user_stats.values())),
                            StatRow("Admins", user_stats.get('admin', 0)),
                            StatRow("Managers", user_stats.get('manager', 0)),
                            StatRow("Users", user_stats.get('user', 0)),
                            StatRow("Active Users", system_stats.get('active_users', 0)),
                            cols=1, cls="gap-2"
                        )
                    )
                ),
                
                # Todo Statistics  
                Card(
                    CardHeader(H2("Todo Statistics")),
                    CardBody(
                        Grid(
                            StatRow("Total Todos", sum(todo_stats.values())),
                            StatRow("Completed", todo_stats.get('completed', 0)),
                            StatRow("Pending", todo_stats.get('pending', 0)),
                            StatRow("Completion Rate", 
                                   f"{(todo_stats.get('completed', 0) / sum(todo_stats.values()) * 100) if sum(todo_stats.values()) > 0 else 0:.1f}%"),
                            cols=1, cls="gap-2"
                        )
                    )
                ),
                
                cols=1, cols_md=2, cls="gap-8 mt-6"
            ),
            
            # Recent User Activity
            Card(
                CardHeader(H2("User Activity")),
                CardBody(
                    user_activity_table(users)
                ),
                cls="mt-8"
            ),
            
            cls=ContainerT.xl
        )

def users_table(users, current_user):
    """Render users management table"""
    return Div(
        Table(
            Thead(
                Tr(
                    Th("Username"),
                    Th("Email"), 
                    Th("Role"),
                    Th("Status"),
                    Th("Created"),
                    Th("Actions")
                )
            ),
            Tbody(
                *[user_row(user, current_user) for user in users]
            ),
            cls="w-full"
        ),
        cls="overflow-x-auto"
    )

def user_row(user, current_user):
    """Render individual user row"""
    is_current_user = user.id == current_user.id
    
    status_badge = Span(
        "Active" if user.active else "Inactive",
        cls=f"text-xs px-2 py-1 rounded {'text-green-700 bg-green-100' if user.active else 'text-red-700 bg-red-100'}"
    )
    
    role_colors = {
        'admin': 'text-purple-700 bg-purple-100',
        'manager': 'text-blue-700 bg-blue-100', 
        'user': 'text-gray-700 bg-gray-100'
    }
    
    role_badge = Span(
        user.role.title(),
        cls=f"text-xs px-2 py-1 rounded {role_colors.get(user.role, role_colors['user'])}"
    )
    
    return Tr(
        Td(user.username + (" (You)" if is_current_user else "")),
        Td(user.email),
        Td(role_badge),
        Td(status_badge),
        Td(user.created_at[:10] if user.created_at else "Unknown"),
        Td(
            user_actions(user, is_current_user) if not is_current_user else 
            Span("Current User", cls="text-muted-foreground text-sm")
        )
    )

def user_actions(user, is_current_user):
    """User action buttons"""
    if is_current_user:
        return Span("Current User", cls="text-muted-foreground")
    
    return Div(
        # Role change dropdown
        Form(
            Select(
                Option("User", value="user", selected=(user.role=="user")),
                Option("Manager", value="manager", selected=(user.role=="manager")), 
                Option("Admin", value="admin", selected=(user.role=="admin")),
                name="role",
                onchange="this.form.submit()",
                cls="text-xs mr-2"
            ),
            method="post",
            action=f"/admin/users/{user.id}/role",
            style="display: inline"
        ),
        
        # Toggle active status
        Form(
            Button(
                "Deactivate" if user.active else "Activate",
                type="submit",
                cls=(ButtonT.warning if user.active else ButtonT.success, "text-xs mr-2")
            ),
            method="post",
            action=f"/admin/users/{user.id}/toggle",
            style="display: inline"
        ),
        
        # Delete user
        Form(
            Button(
                "Delete",
                type="submit", 
                cls=(ButtonT.danger, "text-xs"),
                onclick="return confirm('Delete this user and all their todos?')"
            ),
            method="post",
            action=f"/admin/users/{user.id}/delete",
            style="display: inline"
        ),
        
        cls="flex items-center gap-2"
    )

def recent_todos_table(todos):
    """Recent todos table for admin dashboard"""
    return Table(
        Thead(
            Tr(Th("Todo"), Th("User"), Th("Status"), Th("Priority"), Th("Created"))
        ),
        Tbody(
            *[Tr(
                Td(todo[1][:50] + "..." if len(todo[1]) > 50 else todo[1]),
                Td(todo[6]),  # username
                Td(Span("Done" if todo[3] else "Pending", 
                        cls=f"text-xs px-2 py-1 rounded {'text-green-700 bg-green-100' if todo[3] else 'text-yellow-700 bg-yellow-100'}")),
                Td(todo[4].title()),
                Td(todo[5][:10])  # created_at
            ) for todo in todos]
        ),
        cls="w-full text-sm"
    )

def admin_todos_table(todos):
    """All todos table for admin todos page"""
    return Div(
        Table(
            Thead(
                Tr(
                    Th("Title"),
                    Th("User"), 
                    Th("Email"),
                    Th("Status"),
                    Th("Priority"),
                    Th("Created")
                )
            ),
            Tbody(
                *[Tr(
                    Td(todo[1][:40] + "..." if len(todo[1]) > 40 else todo[1]),
                    Td(todo[6]),  # username
                    Td(todo[7]),  # email
                    Td(Span("Done" if todo[3] else "Pending",
                            cls=f"text-xs px-2 py-1 rounded {'text-green-700 bg-green-100' if todo[3] else 'text-yellow-700 bg-yellow-100'}")),
                    Td(todo[4].title()),
                    Td(todo[5][:10])
                ) for todo in todos]
            ),
            cls="w-full text-sm"
        ),
        cls="overflow-x-auto"
    )

def user_activity_table(users):
    """User activity overview table"""
    return Table(
        Thead(
            Tr(Th("User"), Th("Role"), Th("Status"), Th("Last Login"))
        ),
        Tbody(
            *[Tr(
                Td(user.username),
                Td(user.role.title()),
                Td(Span("Active" if user.active else "Inactive",
                        cls=f"text-xs px-2 py-1 rounded {'text-green-700 bg-green-100' if user.active else 'text-red-700 bg-red-100'}")),
                Td(user.last_login[:10] if user.last_login else "Never")
            ) for user in users[-10:]]  # Last 10 users
        ),
        cls="w-full text-sm"
    )

def AdminNav(user):
    """Admin navigation"""
    return NavBar(
        A("Dashboard", href="/dashboard"),
        A("Users", href="/admin/users"),
        A("Todos", href="/admin/todos"),
        A("System", href="/admin/system"),
        A("Profile", href="/auth/profile"),
        A("Logout", href="/auth/logout", cls=ButtonT.secondary),
        brand=A("🔧 Admin Panel", href="/admin")
    )

def AdminStatsCard(title, value, icon):
    """Admin statistics card"""
    return Card(
        CardBody(
            DivCentered(
                Div(
                    Div(icon, cls="text-3xl mb-2"),
                    P(title, cls="text-sm text-muted-foreground"),
                    P(str(value), cls="text-2xl font-bold"),
                    cls="text-center"
                )
            )
        )
    )

def StatRow(label, value):
    """Statistics row component"""
    return DivFullySpaced(
        Span(label, cls="text-muted-foreground"),
        Span(str(value), cls="font-medium")
    )