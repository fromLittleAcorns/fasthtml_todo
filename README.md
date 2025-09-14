# FastHTML Todo App - Built-in Admin Integration Example

A comprehensive todo application demonstrating **fasthtml-auth v0.2.0** integration with built-in admin interface, advanced user management, and role-based access control.

![FastHTML Todo Demo](https://via.placeholder.com/800x400/2563eb/ffffff?text=FastHTML+Todo+Demo+v2.0)

## 🌟 What This Demonstrates

This application showcases real-world integration patterns for the `fasthtml-auth` package with **built-in admin capabilities**:

- ✅ **Built-in Admin Interface** - Complete user management via fasthtml-auth v0.2.0  
- ✅ **Simplified Architecture** - Reduced codebase by leveraging library features
- ✅ **Complete Authentication Flow** - Registration, login, logout, profiles
- ✅ **Database Extension Patterns** - Adding user-owned data (todos) 
- ✅ **Role-Based Access Control** - User, Manager, Admin permissions
- ✅ **Custom Admin Extensions** - Todo-specific admin features
- ✅ **Modular Architecture** - Scalable project organization
- ✅ **Beautiful UI Integration** - MonsterUI components and forms

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip package manager

### Installation & Setup

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd fasthtml-todo-example
   pip install fasthtml-auth python-fasthtml monsterui
   ```

2. **Run the application:**
   ```bash
   python app.py
   ```

3. **Open your browser:**
   - App: http://localhost:5001
   - Login: http://localhost:5001/auth/login
   - **Built-in Admin**: http://localhost:5001/auth/admin

### Demo Accounts

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| `admin` | `admin123` | Admin | Full system access + built-in admin |
| `demo_user` | `demo123` | User | Basic todo management |
| `demo_manager` | `demo123` | Manager | Extended features |

## 📂 Project Structure

```
fasthtml-todo-example/
├── app.py                 # Main application & built-in admin setup
├── models.py              # Database models & extensions
├── components.py          # Reusable UI components (simplified)
├── routes/
│   ├── public.py         # Public pages (landing, about)
│   ├── todos.py          # Todo CRUD operations
│   └── admin.py          # Todo-specific admin features only
├── data/
│   └── todo_app.db       # SQLite database (auto-created)
└── README.md             # This file
```

## 🎯 Architecture Changes (v2.0)

### What's New with Built-in Admin

**✅ Replaced Custom Code:**
- ~300 lines of user management code removed
- Professional admin interface with search & pagination  
- Safety features (prevent admin self-deletion)
- User CRUD operations with role management
- Admin dashboard with user statistics

**✅ Built-in Admin Routes (Automatic):**
- `/auth/admin` - Main admin dashboard with user stats
- `/auth/admin/users` - Complete user management interface
- `/auth/admin/users/create` - Create users with role selection
- `/auth/admin/users/edit?id={id}` - Edit users, roles, activation
- `/auth/admin/users/delete?id={id}` - Delete users with safety checks

**✅ Custom Admin Routes (Application-specific):**
- `/admin/todos` - Todo management across all users  
- `/admin/system` - Todo-specific system statistics

## 🔧 Key Integration Patterns

### 1. Enable Built-in Admin Interface

```python
from fasthtml_auth import AuthManager

# Initialize authentication with built-in admin
auth = AuthManager(
    db_path="data/app.db",
    config={
        'allow_registration': True,
        'public_paths': ['/about', '/features']
    }
)

# Setup database and middleware
db = auth.initialize()
beforeware = auth.create_beforeware()

# Create app with built-in admin enabled
app = FastHTML(before=beforeware)
auth.register_routes(app, prefix="/auth", include_admin=True)  # 🔑 Key change
```

### 2. Database Extension (Unchanged)

```python
# Extend auth database with app-specific tables
class TodoDatabase:
    def __init__(self, db_path):
        self.db = Database(db_path)  # Reuse auth database
        
    def initialize_todo_tables(self):
        self.todos = self.db.create(Todo, pk=Todo.pk)
```

### 3. Updated Navigation

```python
# Navigation now points to built-in admin
def DashboardNav(user):
    nav_items = [
        A("Dashboard", href="/dashboard"),
        A("Profile", href="/auth/profile"),
    ]
    
    # Admin users get access to built-in admin interface
    if user.role == 'admin':
        nav_items.append(A("Admin", href="/auth/admin"))  # Built-in admin
    
    nav_items.append(A("Logout", href="/auth/logout", cls=ButtonT.secondary))
    return NavBar(*nav_items, brand=A(f"📝 {user.username}", href="/dashboard"))
```

### 4. Todo-Specific Admin Extensions

```python
# Custom admin routes for application-specific features
@app.route("/admin/todos")
@auth.require_admin()  
def all_todos_management(req):
    """View todos across all users - not handled by built-in admin"""
    user = req.scope['user']
    all_todos = todo_db.get_all_todos_admin(limit=100)
    return render_todos_management(user, all_todos)
```

## 🛡️ Admin Features Comparison

### Built-in Admin Features (fasthtml-auth v0.2.0)
- **User Management** - Create, edit, delete users
- **Role Assignment** - Change user roles (user/manager/admin)
- **Account Control** - Activate/deactivate user accounts
- **Search & Filter** - Find users by username, email, role
- **Pagination** - Handle large user databases efficiently
- **Safety Features** - Prevent admin self-deletion, last admin removal
- **Statistics** - User counts by role and status
- **Professional UI** - Consistent MonsterUI design

### Custom Admin Extensions (Application-specific)
- **Todo Overview** - View all todos across users
- **Todo Statistics** - Completion rates, priority breakdown
- **System Information** - Todo-specific metrics and reports  
- **Todo Management** - Delete todos, view user activity

## 📊 Benefits of Built-in Admin

### Code Reduction
- **~300 lines removed** - No more custom user management code
- **~5 routes eliminated** - User CRUD handled automatically
- **Simplified navigation** - Consistent admin experience
- **Reduced maintenance** - Library handles updates and bug fixes

### Feature Improvements  
- **Professional UI** - Polished admin interface with search
- **Advanced Features** - Pagination, filtering, bulk operations
- **Better Security** - Built-in safety checks and validation
- **Consistent Design** - Matches library's MonsterUI styling
- **Future-proof** - Automatic improvements via library updates

### Development Focus
- **Todo Features** - More time for core application functionality
- **Business Logic** - Focus on application-specific requirements
- **Custom Extensions** - Build on top of solid admin foundation

## 🔗 Complete Route Structure

### Authentication Routes (Built-in)
```
/auth/login               # User login
/auth/logout              # User logout  
/auth/register            # User registration
/auth/profile             # User profile management
```

### Built-in Admin Routes (Automatic)
```
/auth/admin               # Admin dashboard with user statistics
/auth/admin/users         # User management with search/filter/pagination
/auth/admin/users/create  # Create new user with role selection
/auth/admin/users/edit    # Edit user details, roles, activation status
/auth/admin/users/delete  # Delete user with safety checks
```

### Application Routes (Custom)
```
/                         # Landing page (redirects if logged in)
/dashboard                # User todo dashboard  
/todos/new                # Create new todo
/todos/{id}/edit          # Edit todo
/about                    # About page
/features                 # Features page
```

### Todo Admin Routes (Custom Extensions)
```
/admin/todos              # View all todos across users
/admin/system             # Todo-specific system information
/admin/todos/{id}/delete  # Admin delete any todo
```

## 🏃‍♂️ Migration from Custom Admin

If updating from a custom admin implementation:

### Step 1: Enable Built-in Admin
```python
# OLD
auth.register_routes(app, prefix="/auth")

# NEW - Enable built-in admin interface
auth.register_routes(app, prefix="/auth", include_admin=True)
```

### Step 2: Update Navigation
```python
# Update admin links to point to built-in routes
A("Admin", href="/auth/admin")  # Instead of /admin  
A("Users", href="/auth/admin/users")  # Instead of custom user management
```

### Step 3: Remove Custom User Management
- Delete custom user CRUD routes
- Remove user management UI components  
- Keep only application-specific admin features

## 🔒 Security Features

### Authentication (Built-in)
- ✅ Bcrypt password hashing
- ✅ Session-based authentication
- ✅ Route protection middleware
- ✅ User ownership validation

### Built-in Admin Security
- ✅ Admin self-protection (can't delete/demote self)
- ✅ Last admin protection (can't remove all admins)  
- ✅ Role-based access control
- ✅ Input validation and sanitization
- ✅ Safe user deletion with confirmations

### Application Security
- ✅ User data isolation (todos belong to users)
- ✅ Admin can view/manage all todos
- ✅ Proper error handling and validation

## 📈 Features by Role

### User Role
- Create, edit, delete personal todos
- Mark todos as complete/incomplete  
- View personal statistics and filters
- Update profile and password

### Manager Role  
- All user features
- *Ready for extension (reporting, team features)*

### Admin Role
- All user/manager features
- **Built-in User Management** - via `/auth/admin/users`
  - Create users with role assignment
  - Edit user details, roles, activation status
  - Delete users with safety checks
  - Search and filter users
- **Todo Administration** - via `/admin/todos`
  - View todos across all users
  - Delete any todo
  - System-wide todo statistics

## 🚀 Development Workflow

### Local Development
```bash
# Start with clean database
rm -f data/todo_app.db
python app.py  # Will recreate with demo data

# Access admin interfaces
# Built-in admin: http://localhost:5001/auth/admin
# Todo admin: http://localhost:5001/admin/todos
```

### Testing Admin Features
1. **Built-in Admin Testing**
   - Login as admin (`admin` / `admin123`)
   - Navigate to `/auth/admin` 
   - Test user creation, role changes, account management
   - Verify search, pagination, safety features

2. **Custom Admin Testing**  
   - Navigate to `/admin/todos` from built-in admin
   - Test todo viewing, filtering, deletion
   - Verify integration between user and todo management

### Database Exploration
```bash
# Monitor database changes
sqlite3 data/todo_app.db ".tables"
sqlite3 data/todo_app.db "SELECT * FROM user LIMIT 5;"
sqlite3 data/todo_app.db "SELECT * FROM todo LIMIT 5;"
```

## 📝 Configuration Options

### Authentication Configuration
```python
auth_config = {
    'allow_registration': True,          # Enable user registration
    'public_paths': ['/about', '/features'],  # Routes that skip auth
    'login_path': '/auth/login',         # Custom login URL (optional)
}

auth = AuthManager(db_path="data/app.db", config=auth_config)
```

### Built-in Admin Customization
The built-in admin interface is automatically styled with MonsterUI and includes:
- Professional form layouts and validation
- Search and filtering capabilities  
- Pagination for large user lists
- Consistent navigation and branding
- Safety confirmations for destructive actions

## 🤝 Contributing

### Areas for Contribution
- **Password Reset** - Email-based password recovery
- **Two-Factor Authentication** - Enhanced security options
- **OAuth Integration** - Google, GitHub login
- **Email Verification** - Account verification workflow  
- **Bulk Operations** - Mass user management features
- **Advanced Reporting** - Analytics and usage reports

### Feedback Welcome
- Built-in admin interface improvements
- Integration patterns and best practices
- Custom admin extension examples
- UI/UX enhancements

## 📚 Learning Resources

### FastHTML-Auth Documentation
- [GitHub Repository](https://github.com/fromlittleacorns/fasthtml-auth)
- [PyPI Package](https://pypi.org/project/fasthtml-auth/)  
- [Built-in Admin Guide](https://github.com/fromlittleacorns/fasthtml-auth#built-in-admin-interface)

### Related Technologies
- [FastHTML Framework](https://fastht.ml)
- [MonsterUI Components](https://monsterui.dev)
- [FastLite ORM](https://github.com/AnswerDotAI/fastlite)

## 💡 Tips & Best Practices

### Leveraging Built-in Admin
- Use built-in admin for all user management operations
- Extend with application-specific admin features
- Maintain consistent navigation between built-in and custom admin
- Follow library's MonsterUI styling patterns

### Custom Admin Development
- Focus on application-specific functionality
- Integrate smoothly with built-in admin interface
- Use library's route protection decorators
- Follow established patterns for consistency

### Database Integration
- Ensure user deletion properly cleans up related data
- Use foreign key relationships where appropriate
- Consider cascade deletion for data integrity
- Monitor database performance with user growth

## 🔧 Troubleshooting

### Common Issues
- **Import errors** - Ensure `fasthtml-auth>=0.2.0` installed
- **Admin not accessible** - Verify `include_admin=True` in route registration  
- **Navigation broken** - Update admin links to use `/auth/admin/*` routes
- **Database conflicts** - Remove old database file to recreate with new schema

### Getting Help
- [FastHTML-Auth Issues](https://github.com/fromlittleacorns/fasthtml-auth/issues)
- [FastHTML Community](https://discord.gg/fasthtml)

---

**FastHTML Todo Demo v2.0** - Built-in admin integration example  
*Built with ❤️ using FastHTML, fasthtml-auth v0.2.0, and MonsterUI*

**Key Achievement:** Reduced codebase by ~300 lines while improving functionality through built-in admin integration.