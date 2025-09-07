# FastHTML Todo App - Authentication Integration Example

A comprehensive todo application demonstrating **fasthtml-auth** integration with advanced user management, role-based access control, and administrative features.

![FastHTML Todo Demo](https://via.placeholder.com/800x400/2563eb/ffffff?text=FastHTML+Todo+Demo)

## 🌟 What This Demonstrates

This application showcases real-world integration patterns for the `fasthtml-auth` package:

- ✅ **Complete Authentication Flow** - Registration, login, logout, profiles
- ✅ **Database Extension Patterns** - Adding user-owned data (todos) 
- ✅ **Role-Based Access Control** - User, Manager, Admin permissions
- ✅ **Administrative User Management** - Features missing from base library
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
   - App: http://localhost:5000
   - Login: http://localhost:5000/auth/login

### Demo Accounts

| Username | Password | Role | Purpose |
|----------|----------|------|---------|
| `admin` | `admin123` | Admin | Full system access |
| `demo_user` | `demo123` | User | Basic todo management |
| `demo_manager` | `demo123` | Manager | Extended features |

## 📁 Project Structure

```
fasthtml-todo-example/
├── app.py                 # Main application & setup
├── models.py              # Database models & extensions
├── components.py          # Reusable UI components
├── routes/
│   ├── public.py         # Public pages (landing, about)
│   ├── todos.py          # Todo CRUD operations
│   └── admin.py          # Admin user management
├── data/
│   └── todo_app.db       # SQLite database (auto-created)
└── README.md             # This file
```

## 🔗 Key Integration Patterns

### 1. Authentication Setup

```python
from fasthtml_auth import AuthManager

# Initialize authentication
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

# Create app with auth
app = FastHTML(before=beforeware)
auth.register_routes(app)
```

### 2. Database Extension

```python
# Extend auth database with app-specific tables
class TodoDatabase:
    def __init__(self, db_path):
        self.db = Database(db_path)  # Reuse auth database
        
    def initialize_todo_tables(self):
        self.todos = self.db.create(Todo, pk=Todo.pk)
```

### 3. Route Protection

```python
# Protected routes automatically get user
@app.route("/dashboard")
def dashboard(req):
    user = req.scope['user']  # Available in all protected routes
    todos = get_user_todos(user.id)
    return render_dashboard(user, todos)

# Role-based protection
@app.route("/admin")
@auth.require_admin()
def admin_panel(req):
    return admin_dashboard()
```

### 4. User Context Usage

```python
# Access user information in routes
def dashboard(req):
    user = req.scope['user']
    
    print(f"User ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Role: {user.role}")
    print(f"Email: {user.email}")
    
    # Filter data by user ownership
    todos = todo_db.get_todos_by_user(user.id)
```

## 🛡️ Admin Features (Extensions)

This app demonstrates admin functionality that extends the base `fasthtml-auth` library:

### User Management
- **Role Assignment** - Promote users to manager/admin
- **Account Status** - Activate/deactivate user accounts  
- **User Deletion** - Remove users and their data
- **User Overview** - System-wide user statistics

### System Administration
- **Todo Management** - View all todos across users
- **System Statistics** - User counts, completion rates
- **Activity Monitoring** - User login patterns

### Implementation Example

```python
# Admin-only route with role checking
@app.route("/admin/users/{user_id}/role", methods=["POST"])
@auth.require_admin()
async def change_user_role(req, user_id: int):
    form = await req.form()
    new_role = form.get('role')
    
    # Update user role (extends auth library)
    success = auth.user_repo.update(user_id, role=new_role)
    return RedirectResponse('/admin/users')
```

## 📊 Database Schema

### Extended Tables

```sql
-- Todos table (extends auth database)
CREATE TABLE todo (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES user(id),
    title TEXT NOT NULL,
    description TEXT,
    completed INTEGER DEFAULT 0,
    priority TEXT DEFAULT 'medium',
    due_date TEXT,
    created_at TEXT,
    updated_at TEXT
);
```

### Relationships

- `todo.user_id` → `user.id` (Foreign Key)
- User ownership enforced in application logic
- Cascade deletion for user cleanup

## 🎨 UI Components & Styling

### MonsterUI Integration

```python
from monsterui.all import *

# Consistent component usage
Card(
    CardHeader(H2("My Todos")),
    CardBody(todo_list),
    cls="mt-6"
)

# Form styling
LabelInput("Title", name="title", required=True)
Button("Create Todo", type="submit", cls=ButtonT.primary)
```

### Reusable Components

```python
# Custom component patterns
def StatsCard(title, value, icon):
    return Card(
        CardBody(
            DivCentered(
                Div(icon, cls="text-3xl mb-2"),
                P(title, cls="text-sm text-muted-foreground"),
                P(str(value), cls="text-2xl font-bold")
            )
        )
    )
```

## 🔒 Security Considerations

### Authentication
- ✅ Bcrypt password hashing (via fasthtml-auth)
- ✅ Session-based authentication
- ✅ Route protection middleware
- ✅ User ownership validation

### Authorization  
- ✅ Role-based access control
- ✅ Admin self-protection (can't delete/demote self)
- ✅ User data isolation
- ✅ Input validation and sanitization

### Example Protection

```python
# Ensure user owns data before operations
def get_todo(todo_id, user_id):
    todo = db.get_todo_by_id(todo_id, user_id)  # User constraint
    if not todo:
        return Response("Not Found", status_code=404)
    return todo
```

## 📈 Features by Role

### User Role
- Create, edit, delete personal todos
- Mark todos as complete/incomplete  
- View personal statistics
- Update profile and password

### Manager Role  
- All user features
- *Ready for extension (reporting, team features)*

### Admin Role
- All user/manager features
- **User Management** - roles, activation, deletion
- **System Overview** - stats, monitoring  
- **Todo Administration** - view all user todos

## 🔧 Development Patterns

### Error Handling
```python
try:
    todo = todo_db.create_todo(user_id, title, description)
    return RedirectResponse('/dashboard?success=created')
except Exception as e:
    print(f"Error creating todo: {e}")
    return render_form(error="Creation failed")
```

### Form Processing
```python
@app.route("/todos/new", methods=["POST"])
async def create_todo(req):
    form = await req.form()
    title = form.get('title', '').strip()
    
    if not title:
        return render_form(error="Title required")
        
    # Process form data...
```

### Redirect Patterns
```python
# Success redirects with messages
return RedirectResponse('/dashboard?success=created', status_code=303)

# Error redirects with context
return RedirectResponse('/todos/new?error=validation_failed', status_code=303)
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**
   ```bash
   export SECRET_KEY="your-production-secret-key"
   export DB_PATH="/app/data/production.db"
   ```

2. **Database Backups**
   ```bash
   # Regular SQLite backups
   cp data/todo_app.db backups/todo_app_$(date +%Y%m%d).db
   ```

3. **Security Headers**
   ```python
   app = FastHTML(
       before=beforeware,
       secret_key=os.getenv('SECRET_KEY'),
       # Add security headers for production
   )
   ```

## 🤝 Contributing to fasthtml-auth

This example demonstrates features that could be added to the base library:

### Potential Library Additions
- **User Management Methods** - role changes, deletion, activation
- **Admin Route Decorators** - `@auth.require_role()` variations
- **User Statistics** - login tracking, activity monitoring
- **Bulk Operations** - batch user management

### Integration Feedback
- Database extension patterns
- UI component integration
- Form validation approaches
- Error handling strategies

## 📚 Learning Resources

### FastHTML-Auth Documentation
- [GitHub Repository](https://github.com/fromlittleacorns/fasthtml-auth)
- [PyPI Package](https://pypi.org/project/fasthtml-auth/)
- [Integration Examples](https://github.com/fromlittleacorns/fasthtml-auth#examples)

### Related Technologies
- [FastHTML Framework](https://fastht.ml)
- [MonsterUI Components](https://monsterui.dev)
- [FastLite ORM](https://github.com/AnswerDotAI/fastlite)

## 💡 Usage Tips

### Development Workflow
```bash
# Start with clean database
rm -f data/todo_app.db
python app.py  # Will recreate with demo data

# Monitor database changes
sqlite3 data/todo_app.db ".tables"
sqlite3 data/todo_app.db "SELECT * FROM user;"
```

### Debugging Authentication
```python
# Check user context in routes
def debug_route(req):
    user = req.scope.get('user')
    print(f"User: {user}")
    print(f"Session: {req.scope.get('auth')}")
    return Response("Check console")
```

### Testing Role Changes
1. Login as admin (`admin` / `admin123`)
2. Go to Admin → User Management
3. Change `demo_user` role to `manager`
4. Login as `demo_user` to test new permissions

## 📞 Support & Questions

### Common Issues
- **Database locked** - Close any SQLite browser connections
- **Import errors** - Ensure all packages installed: `pip install fasthtml-auth python-fasthtml monsterui`
- **Port conflicts** - Change port in `app.py`: `serve(port=5001)`

### Getting Help
- [FastHTML-Auth Issues](https://github.com/fromlittleacorns/fasthtml-auth/issues)
- [FastHTML Community](https://discord.gg/fasthtml)

---

**FastHTML Todo Demo** - Complete authentication integration example
*Built with ❤️ using FastHTML, fasthtml-auth, and MonsterUI*