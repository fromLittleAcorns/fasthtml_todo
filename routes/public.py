"""
Public Routes - Accessible without authentication
Landing page, about, features, etc.
"""

from fasthtml.common import *
from monsterui.all import *

def register_public_routes(app):
    """Register public routes that don't require authentication"""
    
    @app.route("/")
    def home(req):
        """Landing page - redirects if logged in, shows welcome if not"""
        user = req.scope.get('user')  # None if not logged in
        
        if user:
            # User is logged in, redirect to dashboard
            return RedirectResponse('/dashboard', status_code=303)
        
        # Show public landing page
        return render_landing_page()
    
    @app.route("/about")
    def about(req):
        """About page"""
        user = req.scope.get('user')
        return render_about_page(user)
    
    @app.route("/features")  
    def features(req):
        """Features page"""
        user = req.scope.get('user')
        return render_features_page(user)

def render_landing_page():
    """Render the public landing page"""
    return Title("FastHTML Todo - Demo App"), \
        NavBar(
            A("Features", href="/features"),
            A("About", href="/about"),
            A("Sign In", href="/auth/login", cls=ButtonT.primary),
            A("Register", href="/auth/register", cls=ButtonT.secondary),
            brand=H3("📝 FastHTML Todo", href="/")
        ), \
        Container(
            # Hero Section
            Section(
                DivCentered(
                    H1("Build Better Todo Apps", cls="text-5xl font-bold text-center mb-6"),
                    Subtitle(
                        "Complete FastHTML authentication integration demo with user management, "
                        "role-based access, and beautiful UI components.",
                        cls="text-xl text-center text-muted-foreground max-w-3xl mx-auto mb-8"
                    ),
                    
                    DivCentered(
                        A("Get Started", href="/auth/register", cls=(ButtonT.primary, "mr-4")),
                        A("View Demo", href="/auth/login", cls=ButtonT.secondary),
                        cls="space-x-4"
                    )
                ),
                cls="py-20 text-center"
            ),
            
            # Features Grid
            Section(
                H2("What's Included", cls="text-3xl font-bold text-center mb-12"),
                Grid(
                    FeatureCard(
                        "🔐", 
                        "Complete Authentication", 
                        "User registration, login, logout, and profile management with secure password hashing."
                    ),
                    FeatureCard(
                        "👥", 
                        "Role-Based Access", 
                        "User, Manager, and Admin roles with decorators for route protection and feature gating."
                    ),
                    FeatureCard(
                        "📝", 
                        "Todo Management", 
                        "Full CRUD operations for todos with user ownership and filtering capabilities."
                    ),
                    FeatureCard(
                        "⚡", 
                        "FastHTML Integration", 
                        "Seamless integration with FastHTML framework and MonsterUI component system."
                    ),
                    FeatureCard(
                        "🛡️", 
                        "Admin Panel", 
                        "User management, role assignments, system stats, and comprehensive admin tools."
                    ),
                    FeatureCard(
                        "🎨", 
                        "Beautiful UI", 
                        "Responsive design with MonsterUI components, forms, and consistent styling."
                    ),
                    cols=1, cols_md=2, cols_lg=3, cls="gap-8"
                ),
                cls="py-16"
            ),
            
            # Getting Started
            Section(
                Card(
                    CardHeader(
                        H2("Quick Start", cls="text-2xl font-bold text-center"),
                        Subtitle("Get up and running in minutes", cls="text-center")
                    ),
                    CardBody(
                        Grid(
                            Div(
                                H3("1. Install FastHTML-Auth", cls="text-lg font-semibold mb-2"),
                                Code("pip install fasthtml-auth", cls="bg-muted p-2 rounded block"),
                                cls="text-center"
                            ),
                            Div(
                                H3("2. Initialize Auth", cls="text-lg font-semibold mb-2"),
                                Code("auth = AuthManager()", cls="bg-muted p-2 rounded block"),
                                cls="text-center"
                            ),
                            Div(
                                H3("3. Register Routes", cls="text-lg font-semibold mb-2"),
                                Code("auth.register_routes(app)", cls="bg-muted p-2 rounded block"),
                                cls="text-center"
                            ),
                            cols=1, cols_md=3, cls="gap-8"
                        ),
                        
                        DivCentered(
                            A("Try Demo Account", href="/auth/login", cls=(ButtonT.primary, "mt-8")),
                            P("Username: admin, Password: admin123", cls="text-sm text-muted-foreground mt-2")
                        )
                    ),
                    cls="max-w-4xl mx-auto"
                ),
                cls="py-16"
            ),
            
            cls=ContainerT.xl
        ), \
        Footer(
            Container(
                DivFullySpaced(
                    P("Built with FastHTML + fasthtml-auth", cls="text-muted-foreground"),
                    Div(
                        A("GitHub", href="https://github.com/fromlittleacorns/fasthtml-auth", cls="text-muted-foreground hover:underline mr-4"),
                        A("PyPI", href="https://pypi.org/project/fasthtml-auth/", cls="text-muted-foreground hover:underline"),
                    )
                ),
                cls="py-8 border-t"
            )
        )

def render_about_page(user=None):
    """Render the about page"""
    nav_items = [
        A("Home", href="/"),
        A("Features", href="/features"),
    ]
    
    if user:
        nav_items.extend([
            A("Dashboard", href="/dashboard"),
            A("Logout", href="/auth/logout", cls=ButtonT.secondary)
        ])
    else:
        nav_items.extend([
            A("Sign In", href="/auth/login", cls=ButtonT.primary),
            A("Register", href="/auth/register", cls=ButtonT.secondary)
        ])
    
    return Title("About - FastHTML Todo"), \
        NavBar(
            A(*nav_items),
            brand=H3("📝 FastHTML Todo", href="/")
        ), \
        Container(
            H1("About This Demo", cls="text-4xl font-bold mb-6"),
            
            Card(
                CardHeader(H2("FastHTML-Auth Integration Demo")),
                CardBody(
                    P("""
                    This todo application demonstrates how to integrate the fasthtml-auth package 
                    into real FastHTML applications. It showcases user authentication, role-based 
                    access control, database extensions, and administrative features.
                    """, cls="mb-4"),
                    
                    P("""
                    The application is built with a modular architecture that developers can use 
                    as a reference for their own projects. It includes user management features 
                    that extend the base fasthtml-auth library capabilities.
                    """, cls="mb-4"),
                    
                    H3("Key Integration Patterns:", cls="text-lg font-semibold mt-6 mb-3"),
                    Ul(
                        Li("Database extension with user-owned data (todos)"),
                        Li("Route protection with authentication middleware"),
                        Li("Role-based access control with decorators"),
                        Li("User context usage in protected routes"),
                        Li("Administrative user management features"),
                        Li("Form integration with MonsterUI components"),
                        cls="list-disc list-inside space-y-1 text-muted-foreground"
                    )
                )
            ),
            
            Card(
                CardHeader(H2("Technology Stack")),
                CardBody(
                    Grid(
                        TechItem("FastHTML", "Modern Python web framework"),
                        TechItem("fasthtml-auth", "Authentication & user management"),
                        TechItem("MonsterUI", "Beautiful UI components"),
                        TechItem("SQLite", "Database with fastlite ORM"),
                        cols=1, cols_md=2, cls="gap-4"
                    )
                ),
                cls="mt-8"
            ),
            
            cls=(ContainerT.xl, "py-12")
        )

def render_features_page(user=None):
    """Render the features page"""
    nav_items = [
        A("Home", href="/"),
        A("About", href="/about"),
    ]
    
    if user:
        nav_items.extend([
            A("Dashboard", href="/dashboard"),
            A("Logout", href="/auth/logout", cls=ButtonT.secondary)
        ])
    else:
        nav_items.extend([
            A("Sign In", href="/auth/login", cls=ButtonT.primary),
            A("Register", href="/auth/register", cls=ButtonT.secondary)
        ])
    
    return Title("Features - FastHTML Todo"), \
        NavBar(
            *nav_items,
            brand=A("📝 FastHTML Todo", href="/")
        ), \
        Container(
            H1("Features & Capabilities", cls="text-4xl font-bold mb-8"),
            
            Grid(
                # Authentication Features
                Card(
                    CardHeader(H2("🔐 Authentication System")),
                    CardBody(
                        Ul(
                            Li("User registration with validation"),
                            Li("Secure login/logout with bcrypt"),
                            Li("Session management"),
                            Li("Password updates and profile editing"),
                            Li("Account activation/deactivation"),
                            cls="list-disc list-inside space-y-2"
                        )
                    )
                ),
                
                # Role Management
                Card(
                    CardHeader(H2("👥 Role-Based Access")),
                    CardBody(
                        Ul(
                            Li("User role: Basic todo management"),
                            Li("Manager role: Extended features"),
                            Li("Admin role: Full system access"),
                            Li("Route protection decorators"),
                            Li("Role-based UI customization"),
                            cls="list-disc list-inside space-y-2"
                        )
                    )
                ),
                
                # Todo Features
                Card(
                    CardHeader(H2("📝 Todo Management")),
                    CardBody(
                        Ul(
                            Li("Create, edit, delete todos"),
                            Li("Mark todos as complete/incomplete"),
                            Li("Priority levels and due dates"),
                            Li("User-specific todo lists"),
                            Li("Filtering and statistics"),
                            cls="list-disc list-inside space-y-2"
                        )
                    )
                ),
                
                # Admin Features  
                Card(
                    CardHeader(H2("⚡ Admin Panel")),
                    CardBody(
                        Ul(
                            Li("User management and role assignment"),
                            Li("System-wide todo overview"),
                            Li("User activation/deactivation"),
                            Li("System statistics dashboard"),
                            Li("Bulk operations and reporting"),
                            cls="list-disc list-inside space-y-2"
                        )
                    )
                ),
                
                cols=1, cols_md=2, cls="gap-8"
            ),
            
            cls=(ContainerT.xl, "py-12")
        )

def FeatureCard(icon, title, description):
    """Reusable feature card component"""
    return Card(
        CardBody(
            DivCentered(
                Div(icon, cls="text-4xl mb-4"),
                H3(title, cls="text-xl font-semibold mb-2"),
                P(description, cls="text-muted-foreground text-center"),
                cls="text-center"
            )
        ),
        cls="h-full"
    )

def TechItem(name, description):
    """Technology stack item"""
    return Div(
        H4(name, cls="font-semibold"),
        P(description, cls="text-sm text-muted-foreground")
    )