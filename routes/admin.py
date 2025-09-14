"""
Todo-Specific Admin Routes
Demonstrates extending fasthtml-auth built-in admin with application-specific features
User management is now handled by fasthtml-auth built-in admin interface
"""

from fasthtml.common import *
from monsterui.all import *
from datetime import datetime

def register_todo_admin_routes(app, auth, todo_db):
    """Register todo-specific admin routes (user management now built-in)"""
    
    @app.route("/admin/todos")
    @auth.require_admin()
    def all_todos_management(req):
        """View and manage all todos across users"""
        user = req.scope['user']
        filter_type = req.query_params.get('filter', 'all')
        
        # Get todos based on filter
        if filter_type == 'completed':
            all_todos = todo_db.get_all_todos_admin(completed=True, limit=100)
        elif filter_type == 'pending':
            all_todos = todo_db.get_all_todos_admin(completed=False, limit=100)
        else:
            all_todos = todo_db.get_all_todos_admin(limit=100)
        
        success = req.query_params.get('success')
        
        return render_todos_management(user, all_todos, filter_type, success)
    
    @app.route("/admin/system")
    @auth.require_admin()
    def system_info(req):
        """Todo-specific system information and statistics"""
        user = req.scope['user']
        system_stats = todo_db.get_system_stats()
        
        return render_system_info(user, system_stats)
    
    @app.route("/admin/todos/{todo_id:int}/delete", methods=["POST"])
    @auth.require_admin()
    def admin_delete_todo(req, todo_id: int):
        """Admin can delete any todo"""
        success = todo_db.admin_delete_todo(todo_id)
        
        if success:
            return RedirectResponse('/admin/todos?success=todo_deleted', status_code=303)
        else:
            return RedirectResponse('/admin/todos?error=delete_failed', status_code=303)

def render_todos_management(user, all_todos, filter_type='all', success=None):
    """Render todos management page"""
    # Success messages
    messages = {
        'todo_deleted': 'Todo deleted successfully',
    }
    
    return Title("All Todos - Admin"), \
        TodoAdminNav(user), \
        Container(
            DivFullySpaced(
                Div(
                    H1("Todo Management", cls="text-3xl font-bold"),
                    P(f"System-wide todo overview", cls="text-muted-foreground")
                ),
                A("← Back to Built-in Admin", href="/auth/admin", cls=ButtonT.secondary)
            ),
            
            Alert(messages.get(success), cls=AlertT.success) if success else None,
            
            # Filter Tabs
            FilterTabs(filter_type, "/admin/todos"),
            
            Card(
                CardHeader(
                    DivFullySpaced(
                        H2("All User Todos"),
                        P(f"{len(all_todos)} todos found", cls="text-muted-foreground")
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

def render_system_info(user, system_stats):
    """Render system information page"""
    todo_stats = system_stats.get('todo_stats', {})
    
    return Title("System Information - Admin"), \
        TodoAdminNav(user), \
        Container(
            DivFullySpaced(
                H1("Todo System Statistics", cls="text-3xl font-bold"),
                A("← Back to Built-in Admin", href="/auth/admin", cls=ButtonT.secondary)
            ),
            
            # Todo Statistics Overview
            Grid(
                AdminStatsCard("Total Todos", sum(todo_stats.values()), "📝"),
                AdminStatsCard("Completed", todo_stats.get('completed', 0), "✅"),
                AdminStatsCard("Pending", todo_stats.get('pending', 0), "⏳"),
                AdminStatsCard("Completion Rate", 
                             f"{(todo_stats.get('completed', 0) / sum(todo_stats.values()) * 100) if sum(todo_stats.values()) > 0 else 0:.1f}%", 
                             "📊"),
                cols=2, cols_md=4, cls="gap-4 mb-8"
            ),
            
            # Todo Statistics by Priority
            Card(
                CardHeader(H2("Todo Statistics by Priority")),
                CardBody(
                    todo_priority_stats(system_stats.get('priority_stats', {}))
                ),
                cls="mt-8"
            ),
            
            # Recent Activity
            Card(
                CardHeader(H2("Recent Todo Activity")),
                CardBody(
                    recent_todos_activity(system_stats.get('recent_activity', []))
                ),
                cls="mt-8"
            ),
            
            cls=ContainerT.xl
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
                    Th("Created"),
                    Th("Actions")
                )
            ),
            Tbody(
                *[admin_todo_row(todo) for todo in todos]
            ),
            cls="w-full text-sm"
        ),
        cls="overflow-x-auto"
    )

def admin_todo_row(todo):
    """Individual todo row for admin table"""
    status_badge = Span(
        "Done" if todo[3] else "Pending",
        cls=f"text-xs px-2 py-1 rounded {'text-green-700 bg-green-100' if todo[3] else 'text-yellow-700 bg-yellow-100'}"
    )
    
    priority_colors = {
        'high': 'text-red-600 bg-red-50',
        'medium': 'text-yellow-600 bg-yellow-50', 
        'low': 'text-green-600 bg-green-50'
    }
    priority_class = priority_colors.get(todo[4], priority_colors['medium'])
    priority_badge = Span(todo[4].title(), cls=f"text-xs px-2 py-1 rounded {priority_class}")
    
    return Tr(
        Td(todo[1][:50] + "..." if len(todo[1]) > 50 else todo[1]),  # title
        Td(todo[6]),  # username
        Td(todo[7]),  # email
        Td(status_badge),
        Td(priority_badge),
        Td(todo[5][:10]),  # created_at
        Td(
            Form(
                Button(
                    "Delete",
                    type="submit", 
                    cls=(ButtonT.destructive, "text-xs"),
                    onclick="return confirm('Delete this todo?')"
                ),
                method="post",
                action=f"/admin/todos/{todo[0]}/delete",  # todo[0] is id
                style="display: inline"
            )
        )
    )

def FilterTabs(current_filter="all", base_url="/admin/todos"):
    """Filter tabs component for todo views"""
    filters = [
        ("all", "All Todos"),
        ("pending", "Pending"),
        ("completed", "Completed")
    ]
    
    return Div(
        *[
            A(
                label,
                href=f"{base_url}?filter={filter_key}",
                cls=f"px-4 py-2 border-b-2 font-medium transition-colors {'border-primary text-primary' if current_filter == filter_key else 'border-transparent text-muted-foreground hover:text-foreground'}"
            )
            for filter_key, label in filters
        ],
        cls="flex border-b border-border mb-6"
    )

def todo_priority_stats(priority_stats):
    """Display todo statistics by priority"""
    if not priority_stats:
        return P("No priority statistics available.", cls="text-muted-foreground")
    
    return Grid(
        *[StatRow(f"{priority.title()} Priority", count) 
          for priority, count in priority_stats.items()],
        cols=1, cls="gap-2"
    )

def recent_todos_activity(activity):
    """Display recent todo activity"""
    if not activity:
        return P("No recent activity.", cls="text-muted-foreground")
    
    return Div(
        *[ActivityItem(item) for item in activity[:10]],
        cls="space-y-2"
    )

def ActivityItem(item):
    """Individual activity item"""
    return Div(
        DivFullySpaced(
            Div(
                P(item.get('action', 'Unknown action'), cls="font-medium"),
                P(f"User: {item.get('username', 'Unknown')}", cls="text-sm text-muted-foreground")
            ),
            P(item.get('timestamp', '')[:16], cls="text-xs text-muted-foreground")
        ),
        cls="p-3 bg-muted rounded"
    )

def TodoAdminNav(user):
    """Navigation for todo-specific admin areas"""
    return NavBar(
        A("Dashboard", href="/dashboard"),
        A("Users", href="/auth/admin/users"),        # Built-in admin route
        A("Todos", href="/admin/todos"),             # Custom admin route
        A("System", href="/admin/system"),           # Custom admin route
        A("Profile", href="/auth/profile"),
        A("Logout", href="/auth/logout", cls=ButtonT.secondary),
        brand=A("🔧 Todo Admin", href="/auth/admin")  # Link to built-in admin
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