#!/usr/bin/env python3
"""
FastHTML Todo App - Complete Integration Example
Demonstrates fasthtml-auth integration with built-in admin interface
"""

from fasthtml.common import *
from monsterui.all import *
from fasthtml_auth import AuthManager
import os
from pathlib import Path

# Local imports
from models import TodoDatabase, Todo
from routes.public import register_public_routes
from routes.todos import register_todo_routes  
from routes.admin import register_todo_admin_routes

# Configuration
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

APP_CONFIG = {
    'db_path': str(DATA_DIR / "todo_app.db"),
    'secret_key': os.getenv('SECRET_KEY', 'todo-app-demo-key-change-in-production'),
    'debug': True,
    'port': 5001
}

def create_app():
    """Create and configure the FastHTML application"""
    
    # Initialize Authentication System with built-in admin
    auth_config = {
        'allow_registration': True,
        'public_paths': [
            '/about',      # About page
            '/features',   # Features page
        ]
    }
    
    auth = AuthManager(
        db_path=APP_CONFIG['db_path'], 
        config=auth_config
    )
    
    # Initialize databases
    print("🔧 Initializing authentication system...")
    auth_db = auth.initialize()
    
    print("🔧 Initializing todo database...")
    todo_db = TodoDatabase(APP_CONFIG['db_path'])
    todo_db.initialize_todo_tables()
    
    # Create middleware
    beforeware = auth.create_beforeware()
    
    # Create FastHTML app with MonsterUI styling
    app = FastHTML(
        before=beforeware,
        secret_key=APP_CONFIG['secret_key'],
        hdrs=Theme.blue.headers()  # MonsterUI Blue Theme
    )
    
    # Register authentication routes with built-in admin interface
    print("🔧 Registering authentication routes with built-in admin...")
    auth.register_routes(app, prefix="/auth", include_admin=True)
    
    # Register application routes  
    print("🔧 Registering application routes...")
    register_public_routes(app)
    register_todo_routes(app, auth, todo_db)
    register_todo_admin_routes(app, auth, todo_db)  # Only todo-specific admin features
    
    print("✅ Application initialized successfully!")
    print("📋 Built-in admin interface enabled at /auth/admin")
    return app, auth, todo_db

# Module-level app variable for uvicorn
app, auth, todo_db = create_app()

def main():
    """Main application entry point"""
    print("🚀 Starting FastHTML Todo App with Built-in Authentication Admin")
    print("=" * 60)
    
    try:
        
        print(f"""
🌐 Application ready!
   • Login: http://localhost:{APP_CONFIG['port']}/auth/login
   • Register: http://localhost:{APP_CONFIG['port']}/auth/register  
   • Dashboard: http://localhost:{APP_CONFIG['port']}/dashboard
   
🔧 Admin Interfaces:
   • Built-in Admin: http://localhost:{APP_CONFIG['port']}/auth/admin
   • User Management: http://localhost:{APP_CONFIG['port']}/auth/admin/users
   • Todo Admin: http://localhost:{APP_CONFIG['port']}/admin/todos
   
🔑 Default Admin Account:
   • Username: admin
   • Password: admin123
   • Role: admin
   
👥 Demo Users (created automatically):
   • Username: demo_user / Password: demo123 (role: user)
   • Username: demo_manager / Password: demo123 (role: manager)
        """)
        
        # Create demo data
        create_demo_data(auth, todo_db)
        
        serve(port=APP_CONFIG['port'])
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()

def create_demo_data(auth, todo_db):
    """Create demo users and todos for testing"""
    try:
        # Create demo users
        demo_users = [
            ('demo_user', 'demo@example.com', 'demo123', 'user'),
            ('demo_manager', 'manager@example.com', 'demo123', 'manager'),
        ]
        
        for username, email, password, role in demo_users:
            if not auth.get_user(username):
                user = auth.user_repo.create(username, email, password, role)
                print(f"👤 Created demo user: {username} ({role})")
                
                # Add sample todos for demo users
                if role == 'user':
                    sample_todos = [
                        "Learn FastHTML framework",
                        "Integrate authentication system", 
                        "Build todo application",
                        "Deploy to production"
                    ]
                    for i, title in enumerate(sample_todos):
                        todo_db.create_todo(
                            user_id=user.id,
                            title=title,
                            description=f"Demo todo #{i+1} for user {username}",
                            completed=(i % 3 == 0)  # Some completed
                        )
                        
    except Exception as e:
        print(f"⚠️ Demo data creation failed: {e}")

if __name__ == "__main__":
    main()