"""
Reusable UI Components for FastHTML Todo App
Demonstrates component patterns with MonsterUI integration
User management components removed - now handled by fasthtml-auth built-in admin
"""

from fasthtml.common import *
from monsterui.all import *

class ComponentStyles:
    """Centralized styling constants"""
    
    PRIORITY_COLORS = {
        'high': 'text-red-600 bg-red-50 border-red-200',
        'medium': 'text-yellow-600 bg-yellow-50 border-yellow-200',
        'low': 'text-green-600 bg-green-50 border-green-200'
    }
    
    STATUS_COLORS = {
        'active': 'text-green-700 bg-green-100',
        'inactive': 'text-red-700 bg-red-100',
        'completed': 'text-green-700 bg-green-100',
        'pending': 'text-yellow-700 bg-yellow-100'
    }
    
    ROLE_COLORS = {
        'admin': 'text-purple-700 bg-purple-100',
        'manager': 'text-blue-700 bg-blue-100',
        'user': 'text-gray-700 bg-gray-100'
    }

def AppLayout(title, user=None, nav_type="public", *content, **kwargs):
    """
    Main application layout wrapper
    
    Args:
        title: Page title
        user: Current user object (None for public pages)
        nav_type: "public", "dashboard", or "admin"
        *content: Page content
    """
    nav_component = {
        "public": PublicNav(),
        "dashboard": DashboardNav(user) if user else PublicNav(),
        "admin": AdminNav(user) if user else PublicNav()
    }.get(nav_type, PublicNav())
    
    return Title(title), nav_component, *content

def PublicNav():
    """Navigation for public pages"""
    return NavBar(
        A("Features", href="/features"),
        A("About", href="/about"),
        A("Sign In", href="/auth/login", cls=ButtonT.primary),
        A("Register", href="/auth/register", cls=ButtonT.secondary),
        brand=A("📝 FastHTML Todo", href="/")
    )

def DashboardNav(user):
    """Navigation for user dashboard"""
    nav_items = [
        A("Dashboard", href="/dashboard"),
        A("Profile", href="/auth/profile"),
    ]
    
    if user and user.role == 'admin':
        nav_items.append(A("Admin", href="/auth/admin"))  # Use built-in admin
    
    nav_items.append(A("Logout", href="/auth/logout", cls=ButtonT.secondary))
    
    return NavBar(
        *nav_items,
        brand=A(f"📝 {user.username if user else 'Todo'}", href="/dashboard")
    )

def AdminNav(user):
    """Navigation for admin panel - points to built-in admin"""
    return NavBar(
        A("Dashboard", href="/dashboard"),
        A("Users", href="/auth/admin/users"),    # Built-in user management
        A("Todos", href="/admin/todos"),         # Custom todo admin
        A("System", href="/admin/system"),       # Custom system info
        A("Profile", href="/auth/profile"),
        A("Logout", href="/auth/logout", cls=ButtonT.secondary),
        brand=A("🔧 Admin Panel", href="/auth/admin")  # Built-in admin dashboard
    )

def StatsGrid(*stats_cards, cols=2, cols_md=4):
    """Grid container for statistics cards"""
    return Grid(*stats_cards, cols=cols, cols_md=cols_md, cls="gap-4 mb-8")

def StatsCard(title, value, icon, description=None):
    """
    Statistics card component
    
    Args:
        title: Card title
        value: Main statistic value
        icon: Icon/emoji
        description: Optional description text
    """
    return Card(
        CardBody(
            DivCentered(
                Div(
                    Div(icon, cls="text-3xl mb-2"),
                    P(title, cls="text-sm font-medium text-muted-foreground"),
                    P(str(value), cls="text-2xl font-bold"),
                    P(description, cls="text-xs text-muted-foreground mt-1") if description else None,
                    cls="text-center"
                )
            )
        )
    )

def StatusBadge(status, custom_text=None):
    """
    Status badge component
    
    Args:
        status: 'active', 'inactive', 'completed', 'pending'
        custom_text: Override display text
    """
    text = custom_text or status.title()
    color_class = ComponentStyles.STATUS_COLORS.get(status, ComponentStyles.STATUS_COLORS['pending'])
    
    return Span(text, cls=f"text-xs px-2 py-1 rounded {color_class}")

def PriorityBadge(priority):
    """Priority badge for todos"""
    color_class = ComponentStyles.PRIORITY_COLORS.get(priority, ComponentStyles.PRIORITY_COLORS['medium'])
    return Span(priority.title(), cls=f"text-xs px-2 py-1 rounded border {color_class}")

def RoleBadge(role):
    """Role badge for users"""
    color_class = ComponentStyles.ROLE_COLORS.get(role, ComponentStyles.ROLE_COLORS['user'])
    return Span(role.title(), cls=f"text-xs px-2 py-1 rounded {color_class}")

def TodoCard(todo, user_id=None, show_user=False):
    """
    Todo item card component
    
    Args:
        todo: Todo object
        user_id: Current user ID for ownership check
        show_user: Whether to show username (admin view)
    """
    is_completed = getattr(todo, 'completed', False)
    priority = getattr(todo, 'priority', 'medium')
    
    # Determine if user can edit this todo
    can_edit = user_id is None or getattr(todo, 'user_id', None) == user_id
    
    return Card(
        CardBody(
            DivFullySpaced(
                Div(
                    # Todo header
                    DivFullySpaced(
                        H3(
                            todo.title,
                            cls=f"text-lg font-medium {'line-through text-muted-foreground' if is_completed else ''}"
                        ),
                        PriorityBadge(priority)
                    ),
                    
                    # Todo description
                    P(todo.description, cls="text-sm text-muted-foreground mt-1") if todo.description else None,
                    
                    # Todo metadata
                    Div(
                        Span(f"Due: {todo.due_date}", cls="text-xs text-muted-foreground") if getattr(todo, 'due_date', None) else None,
                        Span(f"By: {getattr(todo, 'username', 'Unknown')}", cls="text-xs text-muted-foreground") if show_user else None,
                        cls="flex items-center gap-4 mt-2"
                    )
                ),
                
                # Actions (only show if user can edit)
                TodoActions(todo) if can_edit else StatusBadge('completed' if is_completed else 'pending'),
                
                cls="flex justify-between items-start gap-4"
            )
        ),
        cls=f"{'opacity-60' if is_completed else ''}"
    )

def TodoActions(todo):
    """Action buttons for todo items"""
    return Div(
        Form(
            Button(
                "✓" if not todo.completed else "↶",
                type="submit",
                cls=(ButtonT.success if not todo.completed else ButtonT.secondary, "mr-2"),
                title="Toggle completion"
            ),
            method="post",
            action=f"/todos/{todo.id}/toggle"
        ),
        A("Edit", href=f"/todos/{todo.id}/edit", cls=(ButtonT.secondary, "mr-2")),
        Form(
            Button(
                "Delete",
                type="submit",
                cls=ButtonT.danger,
                onclick="return confirm('Delete this todo?')"
            ),
            method="post",
            action=f"/todos/{todo.id}/delete",
            style="display: inline"
        ),
        cls="flex items-center"
    )

def FilterTabs(current_filter="all", base_url="/dashboard"):
    """
    Filter tabs component for todo views
    
    Args:
        current_filter: Currently active filter
        base_url: Base URL for filter links
    """
    filters = [
        ("all", "All"),
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

def EmptyState(message, action_text=None, action_href=None, icon="📝"):
    """
    Empty state component
    
    Args:
        message: Empty state message
        action_text: Optional action button text
        action_href: Optional action button href
        icon: Display icon/emoji
    """
    return Card(
        CardBody(
            DivCentered(
                Div(
                    H3(icon, cls="text-6xl mb-4"),
                    H3("Nothing here yet", cls="text-xl font-semibold mb-2"),
                    P(message, cls="text-muted-foreground mb-4"),
                    A(action_text, href=action_href, cls=ButtonT.primary) if action_text and action_href else None,
                    cls="text-center py-12"
                )
            )
        ),
        cls="mt-6"
    )

def DataTable(headers, rows, table_id=None):
    """
    Reusable data table component
    
    Args:
        headers: List of header strings
        rows: List of row data (each row is a list of cells)
        table_id: Optional table ID
    """
    return Div(
        Table(
            Thead(
                Tr(*[Th(header) for header in headers])
            ),
            Tbody(
                *[Tr(*row) if isinstance(row, (list, tuple)) else row for row in rows]
            ),
            id=table_id,
            cls="w-full"
        ),
        cls="overflow-x-auto"
    )

def FormSection(title, *form_elements, description=None):
    """
    Form section wrapper
    
    Args:
        title: Section title
        *form_elements: Form inputs and elements
        description: Optional description text
    """
    return Div(
        H3(title, cls="text-lg font-semibold mb-2"),
        P(description, cls="text-sm text-muted-foreground mb-4") if description else None,
        *form_elements,
        cls="mb-6"
    )

def ActionButtons(*buttons, alignment="right"):
    """
    Button group container
    
    Args:
        *buttons: Button elements
        alignment: 'left', 'right', 'center'
    """
    align_class = {
        'left': 'justify-start',
        'right': 'justify-end', 
        'center': 'justify-center'
    }.get(alignment, 'justify-end')
    
    return Div(
        *buttons,
        cls=f"flex items-center gap-2 {align_class}"
    )

def ConfirmButton(text, action, method="post", confirm_message="Are you sure?", button_style=ButtonT.primary):
    """
    Button with confirmation dialog
    
    Args:
        text: Button text
        action: Form action URL
        method: HTTP method
        confirm_message: Confirmation dialog message
        button_style: Button style class
    """
    return Form(
        Button(
            text,
            type="submit",
            cls=button_style,
            onclick=f"return confirm('{confirm_message}')"
        ),
        method=method,
        action=action,
        style="display: inline"
    )

def InfoRow(label, value, value_class="text-muted-foreground"):
    """
    Information display row
    
    Args:
        label: Label text
        value: Value text
        value_class: CSS class for value
    """
    return DivFullySpaced(
        Span(label, cls="font-medium"),
        Span(str(value), cls=value_class)
    )

def PageHeader(title, subtitle=None, *actions):
    """
    Page header with title and actions
    
    Args:
        title: Page title
        subtitle: Optional subtitle
        *actions: Action buttons or elements
    """
    return DivFullySpaced(
        Div(
            H1(title, cls="text-3xl font-bold"),
            P(subtitle, cls="text-muted-foreground mt-1") if subtitle else None
        ),
        Div(*actions, cls="flex items-center gap-2") if actions else None,
        cls="mb-8"
    )

def LoadingSpinner(text="Loading..."):
    """Simple loading indicator"""
    return DivCentered(
        Div(
            Div(cls="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"),
            P(text, cls="text-muted-foreground mt-2"),
            cls="text-center"
        ),
        cls="py-8"
    )

def AlertMessage(message, type="info", dismissible=False):
    """
    Alert message component
    
    Args:
        message: Alert message text
        type: Alert type ('success', 'error', 'warning', 'info')
        dismissible: Whether alert can be dismissed
    """
    alert_classes = {
        'success': AlertT.success,
        'error': AlertT.error,
        'warning': AlertT.warning,
        'info': AlertT.info
    }
    
    alert_class = alert_classes.get(type, AlertT.info)
    
    if dismissible:
        return Alert(
            DivFullySpaced(
                Span(message),
                Button("×", onclick="this.parentElement.parentElement.remove()", cls="text-lg font-bold")
            ),
            cls=alert_class
        )
    else:
        return Alert(message, cls=alert_class)

# Utility functions for common patterns

def format_date(date_string, format="short"):
    """Format date string for display"""
    if not date_string:
        return "Never"
    
    if format == "short":
        return date_string[:10]  # YYYY-MM-DD
    elif format == "datetime":
        return date_string.replace('T', ' ')[:19]  # YYYY-MM-DD HH:MM:SS
    else:
        return date_string

def format_completion_rate(completed, total):
    """Format completion percentage"""
    if total == 0:
        return "0%"
    return f"{(completed / total * 100):.0f}%"