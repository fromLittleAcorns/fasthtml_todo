"""
Todo App Models - Database extensions for FastHTML-Auth
Demonstrates how to extend the auth database with application-specific tables
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from fastlite import Database
from pathlib import Path

@dataclass 
class Todo:
    """Todo model with user ownership"""
    id: Optional[int] = None
    user_id: int = 0
    title: str = ""
    description: str = ""
    completed: bool = False
    priority: str = "medium"  # low, medium, high
    due_date: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    
    # Primary key for fastlite
    pk = "id"
    
    def __post_init__(self):
        """Set timestamps if not provided"""
        now = datetime.now().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now

class TodoDatabase:
    """Extended database manager for todo-specific tables"""
    
    def __init__(self, db_path: str):
        """Initialize with existing auth database"""
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db = Database(db_path)
        self.todos = None
        
    def initialize_todo_tables(self):
        """Create todo-related tables"""
        # Create todos table
        self.todos = self.db.create(Todo, pk=Todo.pk)
        
        print("✅ Todo database tables initialized")
        return self.db
    
    def get_todos_by_user(self, user_id: int, completed: Optional[bool] = None) -> List[Todo]:
        """Get all todos for a specific user, optionally filtered by completion status"""
        try:
            if completed is None:
                # Get all todos for user
                todos = list(self.todos("user_id=? ORDER BY created_at DESC", (user_id,)))
            else:
                # Get todos filtered by completion status
                todos = list(self.todos(
                    "user_id=? AND completed=? ORDER BY created_at DESC", 
                    (user_id, completed)
                ))
            
            return [self._ensure_todo_object(todo) for todo in todos]
        except Exception as e:
            print(f"Error getting todos for user {user_id}: {e}")
            return []
    
    def get_todo_by_id(self, todo_id: int, user_id: Optional[int] = None) -> Optional[Todo]:
        """Get a specific todo, optionally ensuring it belongs to user"""
        try:
            if user_id is not None:
                # Ensure todo belongs to user
                todos = list(self.todos("id=? AND user_id=?", (todo_id, user_id)))
            else:
                # Admin access - any todo
                todos = list(self.todos("id=?", (todo_id,)))
                
            if todos:
                return self._ensure_todo_object(todos[0])
            return None
        except Exception as e:
            print(f"Error getting todo {todo_id}: {e}")
            return None
    
    def create_todo(self, user_id: int, title: str, description: str = "", 
                   priority: str = "medium", due_date: Optional[str] = None) -> Optional[Todo]:
        """Create a new todo for a user"""
        try:
            todo = Todo(
                user_id=user_id,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                completed=False
            )
            
            result = self.todos.insert(todo)
            return self._ensure_todo_object(result)
        except Exception as e:
            print(f"Error creating todo: {e}")
            return None
    
    def update_todo(self, todo_id: int, **kwargs) -> bool:
        """Update todo fields"""
        try:
            # Add updated timestamp
            kwargs['updated_at'] = datetime.now().isoformat()
            
            # Update using fastlite syntax
            self.todos.update(id=todo_id, **kwargs)
            return True
        except Exception as e:
            print(f"Error updating todo {todo_id}: {e}")
            return False
    
    def delete_todo(self, todo_id: int, user_id: Optional[int] = None) -> bool:
        """Delete a todo, optionally ensuring it belongs to user"""
        try:
            if user_id is not None:
                # Ensure user owns the todo before deleting
                todo = self.get_todo_by_id(todo_id, user_id)
                if not todo:
                    return False
            
            self.todos.delete(todo_id)
            return True
        except Exception as e:
            print(f"Error deleting todo {todo_id}: {e}")
            return False
    
    def toggle_todo_completion(self, todo_id: int, user_id: Optional[int] = None) -> bool:
        """Toggle todo completion status"""
        try:
            todo = self.get_todo_by_id(todo_id, user_id)
            if not todo:
                return False
                
            return self.update_todo(todo_id, completed=not todo.completed)
        except Exception as e:
            print(f"Error toggling todo {todo_id}: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> dict:
        """Get todo statistics for a user"""
        try:
            all_todos = self.get_todos_by_user(user_id)
            completed = [t for t in all_todos if t.completed]
            pending = [t for t in all_todos if not t.completed]
            
            return {
                'total': len(all_todos),
                'completed': len(completed),
                'pending': len(pending),
                'completion_rate': len(completed) / len(all_todos) if all_todos else 0
            }
        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {'total': 0, 'completed': 0, 'pending': 0, 'completion_rate': 0}
    
    def get_all_todos_admin(self, limit: int = 100) -> List[tuple]:
        """Get all todos with user information for admin panel"""
        try:
            # Join todos with users table for admin view
            query = """
            SELECT t.id, t.title, t.description, t.completed, t.priority, 
                   t.created_at, u.username, u.email, u.role 
            FROM todo t 
            JOIN user u ON t.user_id = u.id 
            ORDER BY t.created_at DESC 
            LIMIT ?
            """
            
            result = self.db.execute(query, (limit,)).fetchall()
            return result
        except Exception as e:
            print(f"Error getting all todos for admin: {e}")
            return []
    
    def get_system_stats(self) -> dict:
        """Get system-wide statistics for admin dashboard"""
        try:
            # Users count by role
            user_stats = self.db.execute("""
                SELECT role, COUNT(*) as count 
                FROM user 
                GROUP BY role
            """).fetchall()
            
            # Todo stats
            todo_stats = self.db.execute("""
                SELECT completed, COUNT(*) as count 
                FROM todo 
                GROUP BY completed
            """).fetchall()
            
            # Active users (users with todos)
            active_users = self.db.execute("""
                SELECT COUNT(DISTINCT user_id) as count 
                FROM todo
            """).fetchone()
            
            return {
                'user_stats': {row[0]: row[1] for row in user_stats},
                'todo_stats': {
                    'completed' if row[0] else 'pending': row[1] 
                    for row in todo_stats
                },
                'active_users': active_users[0] if active_users else 0
            }
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {}
    
    def delete_user_todos(self, user_id: int) -> bool:
        """Delete all todos for a user (for user deletion)"""
        try:
            self.db.execute("DELETE FROM todo WHERE user_id = ?", (user_id,))
            return True
        except Exception as e:
            print(f"Error deleting user todos: {e}")
            return False
    
    def _ensure_todo_object(self, todo_data) -> Todo:
        """Convert dict from database to Todo object if needed"""
        if isinstance(todo_data, Todo):
            return todo_data
        
        # Convert dict to Todo object
        return Todo(
            id=todo_data.get('id'),
            user_id=todo_data.get('user_id'),
            title=todo_data.get('title', ''),
            description=todo_data.get('description', ''),
            completed=bool(todo_data.get('completed', False)),
            priority=todo_data.get('priority', 'medium'),
            due_date=todo_data.get('due_date'),
            created_at=todo_data.get('created_at', ''),
            updated_at=todo_data.get('updated_at', '')
        )