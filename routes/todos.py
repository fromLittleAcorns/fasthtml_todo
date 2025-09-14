"""
Todo Routes - Protected routes for todo management
SECURITY HARDENED - Fixed critical user ownership verification
Updated to use built-in admin navigation
"""

from fasthtml.common import *
from monsterui.all import *
from datetime import datetime

def register_todo_routes(app, auth, todo_db):
    """Register protected todo routes with enhanced security"""
    
    @app.route("/dashboard")
    def dashboard(req):
        """Main user dashboard with todos - SECURITY HARDENED"""
        user = req.scope['user']
        filter_type = req.query_params.get('filter', 'all')
        
        # DEBUG: Log dashboard access
        print(f"DEBUG: Dashboard accessed by user_id={user.id}, username={user.username}, role={user.role}")
        
        # Get todos based on filter - SECURITY: Only user's own todos
        if filter_type == 'completed':
            todos = todo_db.get_todos_by_user(user.id, completed=True)
        elif filter_type == 'pending':  
            todos = todo_db.get_todos_by_user(user.id, completed=False)
        else:
            todos = todo_db.get_todos_by_user(user.id)
        
        # DEBUG: Log todo retrieval
        print(f"DEBUG: User {user.id} retrieved {len(todos)} todos (filter={filter_type})")
        
        # SECURITY AUDIT: Verify all todos belong to current user
        security_violations = []
        for todo in todos:
            if todo.user_id != user.id:
                security_violations.append(f"Todo {todo.id} owned by {todo.user_id}")
        
        if security_violations:
            print(f"🚨 CRITICAL SECURITY VIOLATIONS: {security_violations}")
            # In production, you might want to log this to security logs and potentially block the request
        
        # Get user statistics
        stats = todo_db.get_user_stats(user.id)
        
        return render_dashboard(user, todos, stats, filter_type)
    
    @app.route("/todos/new", methods=["GET"])
    def new_todo_form(req):
        """Show new todo form"""
        user = req.scope['user']
        return render_todo_form(user)
    
    @app.route("/todos/new", methods=["POST"])
    async def create_todo(req):
        """Create a new todo - SECURITY: Uses current user's ID"""
        user = req.scope['user']
        form = await req.form()
        
        title = form.get('title', '').strip()
        description = form.get('description', '').strip()
        priority = form.get('priority', 'medium')
        due_date = form.get('due_date', '') or None
        
        if not title:
            return render_todo_form(user, error="Title is required")
        
        # SECURITY: Always create todo with current user's ID
        todo = todo_db.create_todo(
            user_id=user.id,  # CRITICAL: Use authenticated user's ID
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        
        if todo:
            print(f"DEBUG: User {user.id} created todo {todo.id}: '{title[:30]}...'")
            return RedirectResponse('/dashboard?success=created', status_code=303)
        else:
            return render_todo_form(user, error="Failed to create todo")
    
    @app.route("/todos/{todo_id:int}/edit", methods=["GET"])
    def edit_todo_form(req, todo_id: int):
        """Show edit todo form - SECURITY HARDENED"""
        user = req.scope['user']
        # SECURITY: get_todo_by_id verifies user ownership
        todo = todo_db.get_todo_by_id(todo_id, user.id)
        
        if not todo:
            print(f"SECURITY: User {user.id} blocked from editing todo {todo_id} (not found or not owned)")
            return RedirectResponse('/dashboard?error=not_found', status_code=303)
        
        return render_todo_form(user, todo=todo)
    
    @app.route("/todos/{todo_id:int}/edit", methods=["POST"])
    async def update_todo(req, todo_id: int):
        """Update an existing todo - SECURITY HARDENED"""
        user = req.scope['user']
        # SECURITY: Verify ownership before allowing edit
        todo = todo_db.get_todo_by_id(todo_id, user.id)
        
        if not todo:
            print(f"SECURITY: User {user.id} blocked from updating todo {todo_id} (not found or not owned)")
            return RedirectResponse('/dashboard?error=not_found', status_code=303)
        
        form = await req.form()
        title = form.get('title', '').strip()
        description = form.get('description', '').strip()
        priority = form.get('priority', 'medium')
        due_date = form.get('due_date', '') or None
        
        if not title:
            return render_todo_form(user, todo=todo, error="Title is required")
        
        # SECURITY: update_todo now requires user_id verification
        success = todo_db.update_todo_secure(
            todo_id,
            user.id,  # ADDED: User ID verification
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )
        
        if success:
            print(f"DEBUG: User {user.id} updated todo {todo_id}")
            return RedirectResponse('/dashboard?success=updated', status_code=303)
        else:
            return render_todo_form(user, todo=todo, error="Failed to update todo")
    
    @app.route("/todos/{todo_id:int}/toggle", methods=["POST"])
    def toggle_todo(req, todo_id: int):
        """Toggle todo completion status - SECURITY HARDENED"""
        user = req.scope['user']
        # SECURITY: toggle_todo_completion verifies user ownership
        success = todo_db.toggle_todo_completion(todo_id, user.id)
        
        if success:
            print(f"DEBUG: User {user.id} toggled todo {todo_id}")
            return RedirectResponse('/dashboard?success=toggled', status_code=303)
        else:
            print(f"SECURITY: User {user.id} blocked from toggling todo {todo_id}")
            return RedirectResponse('/dashboard?error=toggle_failed', status_code=303)
    
    @app.route("/todos/{todo_id:int}/delete", methods=["POST"])
    def delete_todo(req, todo_id: int):
        """Delete a todo - SECURITY HARDENED"""
        user = req.scope['user']
        # SECURITY: delete_todo has multi-layer ownership verification
        success = todo_db.delete_todo(todo_id, user.id)
        
        if success:
            print(f"DEBUG: User {user.id} deleted todo {todo_id}")
            return RedirectResponse('/dashboard?success=deleted', status_code=303)
        else:
            print(f"SECURITY: User {user.id} blocked from deleting todo {todo_id}")
            return RedirectResponse('/dashboard?error=delete_failed', status_code=303)
    
    # DEBUG ROUTE - Remove in production
    @app.route("/debug/security")
    @auth.require_admin()
    def debug_security(req):
        """Debug route to check security status"""
        user = req.scope['user']
        
        # Get security audit for current user
        audit = todo_db.security_audit_todos(user.id)
        
        # Get all todos debug info
        all_todos = todo_db.debug_all_todos()
        
        debug_html = f"""
        <h1>Security Audit Debug</h1>
        <h2>Current User: {user.username} (ID: {user.id}, Role: {user.role})</h2>
        
        <h3>Security Audit Results:</h3>
        <pre>{audit}</pre>
        
        <h3>All Todos in System:</h3>
        <table border="1">
        <tr><th>Todo ID</th><th>Title</th><th>Owner ID</th><th>Owner Name</th><th>Owner Role</th></tr>
        """
        
        for todo in all_todos:
            debug_html += f"""
            <tr>
                <td>{todo['todo_id']}</td>
                <td>{todo['title'][:30]}...</td>
                <td>{todo['owner_id']}</td>
                <td>{todo['owner_name']}</td>
                <td>{todo['owner_role']}</td>
            </tr>
            """
        
        debug_html += "</table>"
        
        return debug_html

def render_dashboard(user, todos, stats, filter_type='all'):
    """Render the main dashboard - SECURITY: Only shows user's todos"""
    return Title("Dashboard - My Todos"), \
        DashboardNav(user), \
        Container(
            # Dashboard Header
            DivFullySpaced(
                Div(
                    H1(f"Welcome back, {user.username}!", cls="text-3xl font-bold"),
                    P(f"You have {stats['pending']} pending todos", cls="text-muted-foreground")
                ),
                A("New Todo", href="/todos/new", cls=(ButtonT.primary, "mb-4", "text-l px-5 py-2"))
            ),
            
            # Statistics Cards
            Grid(
                StatsCard("Total Todos", stats['total'], "📝"),
                StatsCard("Completed", stats['completed'], "✅"),
                StatsCard("Pending", stats['pending'], "⏳"),
                StatsCard("Completion Rate", f"{stats['completion_rate']:.0%}", "📊"),
                cols=2, cols_md=4, cls="gap-4 mb-4"
            ),
            
            # Filter Tabs
            TabsContainer(
                Tab("All", f"/dashboard?filter=all", active=(filter_type=='all')),
                Tab("Pending", f"/dashboard?filter=pending", active=(filter_type=='pending')),
                Tab("Completed", f"/dashboard?filter=completed", active=(filter_type=='completed'))
            ),
            
            # Todos List
            todos_section(todos) if todos else empty_state(filter_type),
            
            cls=ContainerT.xl
        )

def todos_section(todos):
    """Render todos list section"""
    return Card(
        CardHeader(
            H2("Your Todos", cls="text-xl font-semibold")
        ),
        CardBody(
            Div(
                *[todo_item(todo) for todo in todos],
                cls="space-y-1"
            )
        ),
        cls="mt-1"
    )

def todo_item(todo):
    """Render individual todo item - SECURITY: Only shows if ownership verified"""
    priority_colors = {
        'high': 'text-red-600 bg-red-50',
        'medium': 'text-yellow-600 bg-yellow-50', 
        'low': 'text-green-600 bg-green-50'
    }
    
    priority_class = priority_colors.get(todo.priority, 'text-gray-600 bg-gray-50')
    
    return Card(
        CardBody(
            DivFullySpaced(
                Div(
                    # Todo content
                    DivFullySpaced(
                        Div(
                            H3(
                                todo.title, 
                                cls=f"text-lg font-medium {'line-through text-muted-foreground' if todo.completed else ''}"
                            ),
                            P(todo.description, cls="text-sm text-muted-foreground") if todo.description else None,
                            Div(
                                Span(todo.priority.title(), cls=f"text-xs px-2 py-1 rounded {priority_class}"),
                                Span(f"Due: {todo.due_date}", cls="text-xs text-muted-foreground") if todo.due_date else None,
                                cls="flex items-center gap-2 mt-1"
                            )
                        ),
                        
                        # Actions - Only show for user's own todos
                        Div(
                            Form(
                                Button(
                                    "✓" if not todo.completed else "↶", 
                                    type="submit", 
                                    cls=(ButtonT.secondary if not todo.completed else ButtonT.primary,  "w-16 h-8"),
                                    title="Toggle completion"
                                ),
                                method="post",
                                action=f"/todos/{todo.id}/toggle"
                            ),
                            A("Edit", href=f"/todos/{todo.id}/edit", cls=(ButtonT.secondary, "w-16 h-8 inline-flex items-center justify-center")),
                            Form(
                                Button("Delete", type="submit", cls=(ButtonT.destructive, "w-16 h-8"),
                                      onclick="return confirm('Delete this todo?')"),
                                method="post",
                                action=f"/todos/{todo.id}/delete",
                                style="display: inline"
                            ),
                            cls="flex items-center gap-2"
                        ),
                        cls="flex justify-between items-start"
                    )
                )
            )
        ),
        cls=f"{'opacity-60' if todo.completed else ''}"
    )

def empty_state(filter_type):
    """Render empty state when no todos"""
    messages = {
        'all': "You haven't created any todos yet.",
        'completed': "No completed todos found.",
        'pending': "No pending todos found."
    }
    
    return Card(
        CardBody(
            DivCentered(
                Div(
                    H3("📝", cls="text-6xl mb-4"),
                    H3("No Todos Found", cls="text-xl font-semibold mb-2"),
                    P(messages.get(filter_type, messages['all']), cls="text-muted-foreground mb-4"),
                    A("Create Your First Todo", href="/todos/new", cls=ButtonT.primary) if filter_type == 'all' else None,
                    cls="text-center py-12"
                )
            )
        ),
        cls="mt-6"
    )

def render_todo_form(user, todo=None, error=None):
    """Render todo create/edit form"""
    is_edit = todo is not None
    action = f"/todos/{todo.id}/edit" if is_edit else "/todos/new"
    
    return Title(f"{'Edit' if is_edit else 'New'} Todo"), \
        DashboardNav(user), \
        Container(
            Card(
                CardHeader(
                    DivFullySpaced(
                        H1(f"{'Edit' if is_edit else 'Create'} Todo", cls="text-2xl font-bold"),
                        A("← Back to Dashboard", href="/dashboard", cls=ButtonT.secondary)
                    )
                ),
                CardBody(
                    Alert(error, cls=AlertT.error) if error else None,
                    
                    Form(
                        LabelInput(
                            "Title",
                            name="title",
                            value=todo.title if is_edit else "",
                            placeholder="What needs to be done?",
                            required=True,
                            autofocus=True
                        ),
                        Div(
                            Label(
                                "Description", cls="block text-sm font-medium mb-1"),
                            Textarea(
                                todo.description if is_edit else "",
                                name="description", 
                                placeholder="Add more details (optional)",
                                rows=3,
                                cls="w-full block ml-2"
                            )
                        ),
                        Grid(
                            Label(
                                "Priority",
                                Select(
                                    Option("Low", value="low", selected=(is_edit and todo.priority=="low")),
                                    Option("Medium", value="medium", selected=(is_edit and todo.priority=="medium")),
                                    Option("High", value="high", selected=(is_edit and todo.priority=="high")),
                                    name="priority",
                                    cls="ml-2 w-full",
                                ),
                                cls="text-sm font-medium mb-1"
                            ),
                            LabelInput(
                                "Due Date",
                                name="due_date",
                                type="date",
                                value=todo.due_date if is_edit and todo.due_date else ""
                            ),
                            cols=1, cols_md=2, cls="gap-4"
                        ),
                        
                        DivRAligned(
                            Button(f"{'Update' if is_edit else 'Create'} Todo", type="submit", cls=ButtonT.primary),
                            cls="mt-6"
                        ),
                        
                        method="post",
                        action=action
                    )
                ),
                cls="max-w-2xl mx-auto mt-8"
            ),
            cls=ContainerT.xl
        )

def DashboardNav(user):
    """Navigation bar for dashboard - Updated to use built-in admin"""
    nav_items = [
        A("Dashboard", href="/dashboard"),
        A("Profile", href="/auth/profile"),
    ]
    
    # Add admin link for admin users - now points to built-in admin
    if user.role == 'admin':
        nav_items.append(A("Admin", href="/auth/admin"))  # Updated to built-in admin
    
    nav_items.append(A("Logout", href="/auth/logout", cls=ButtonT.secondary))
    
    return NavBar(
        *nav_items,
        brand=A(f"📝 Welcome, {user.username}", href="/dashboard")
    )

def StatsCard(title, value, icon):
    """Statistics card component"""
    return Card(
        CardBody(
            DivCentered(
                Div(
                    Div(icon, cls="text-2xl mb-2"),
                    P(title, cls="text-sm text-muted-foreground"),
                    P(str(value), cls="text-2xl font-bold"),
                    cls="text-center"
                )
            )
        )
    )

def TabsContainer(*tabs):
    """Tab container for filtering"""
    return Div(
        *tabs,
        cls="flex border-b border-border mb-6"
    )

def Tab(label, href, active=False):
    """Tab component"""
    return A(
        label,
        href=href,
        cls=f"px-4 py-2 border-b-2 font-medium transition-colors {'border-primary text-primary' if active else 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'}"
    )