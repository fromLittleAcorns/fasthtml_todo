"""
Database Models and Extensions - SECURITY HARDENED
Fixed critical security issue where users could access/delete other users' todos
"""

from fastlite import Database
from fasthtml.common import *
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any

@dataclass
class Todo:
    id: int
    user_id: int  
    title: str
    description: Optional[str] = None
    completed: bool = False
    priority: str = "medium"  # low, medium, high
    due_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    pk = "id"

class TodoDatabase:
    """
    Extended database functionality for todo management
    Integrates with fasthtml-auth database
    SECURITY HARDENED - Strict user ownership enforcement
    """
    
    def __init__(self, db_path: str):
        """Initialize database connection (reuses auth database)"""
        self.db = Database(db_path)
        
    def initialize_todo_tables(self):
        """Create todo-related tables in the auth database"""
        try:
            # Create todos table with foreign key to auth user table
            self.todos = self.db.create(Todo, 
                pk=Todo.pk, 
                foreign_keys=[("user_id", "user", "id")]
            )
            print("✅ Todo tables initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize todo tables: {e}")
            raise
    
    def create_todo(self, user_id: int, title: str, description: str = "", 
                   priority: str = "medium", due_date: str = None) -> Optional[Todo]:
        """Create a new todo for a user"""
        try:
            now = datetime.now().isoformat()
            todo = self.todos.insert(
                user_id=user_id,
                title=title.strip(),
                description=description.strip() if description else "",
                priority=priority,
                due_date=due_date,
                completed=False,
                created_at=now,
                updated_at=now
            )
            print(f"DEBUG: Created todo {todo.id} for user {user_id}: '{title[:30]}...'")
            return todo
            
        except Exception as e:
            print(f"Error creating todo: {e}")
            return None
    
    def get_todos_by_user(self, user_id: int, completed: Optional[bool] = None) -> List[Todo]:
        """Get todos for a specific user ONLY - SECURITY CRITICAL"""
        try:
            if completed is not None:
                # Ensure we ONLY get todos for this specific user
                todos = list(self.todos(where="user_id = ? AND completed = ?", where_args=(user_id, int(completed))))
            else:
                # Ensure we ONLY get todos for this specific user
                todos = list(self.todos(where="user_id = ?", where_args=(user_id,)))
            
            # SECURITY: Double-check that all returned todos belong to the requesting user
            filtered_todos = []
            for todo in todos:
                if todo.user_id == user_id:
                    filtered_todos.append(todo)
                else:
                    print(f"🚨 SECURITY VIOLATION PREVENTED: Todo {todo.id} (owner:{todo.user_id}) filtered out for user {user_id}")
            
            print(f"DEBUG: User {user_id} fetched {len(filtered_todos)} todos (completed={completed})")
            return filtered_todos
                
        except Exception as e:
            print(f"Error fetching user todos: {e}")
            return []
    
    def get_todo_by_id(self, todo_id: int, user_id: int) -> Optional[Todo]:
        """Get a specific todo by ID, ensuring user ownership - SECURITY CRITICAL"""
        try:
            todo = self.todos.get(todo_id)
            if not todo:
                print(f"DEBUG: Todo {todo_id} not found")
                return None
                
            # CRITICAL SECURITY CHECK: Verify ownership
            if todo.user_id != user_id:
                print(f"🚨 SECURITY VIOLATION BLOCKED: User {user_id} attempted to access todo {todo_id} owned by {todo.user_id}")
                return None
                
            return todo
            
        except Exception as e:
            print(f"Error fetching todo: {e}")
            return None
    
    def update_todo(self, todo_id: int, user_id: int, title=None, description=None, completed=None, priority=None, due_date=None) -> bool:
        """Update a todo using Todo dataclass instance - PYTHONIC FASTLITE VERSION"""
        try:
            now = datetime.now().isoformat()
            
            # Get current todo to preserve existing values
            current_todo = self.todos.get(todo_id)
            if not current_todo:
                print(f"DEBUG: Todo {todo_id} not found in database")
                return False
            
            # Create updated Todo instance with new values or preserve existing ones
            updated_todo = Todo(
                id=todo_id,
                user_id=current_todo.user_id,  # Always preserve user_id
                title=title if title is not None else current_todo.title,
                description=description if description is not None else current_todo.description,
                completed=completed if completed is not None else current_todo.completed,
                priority=priority if priority is not None else current_todo.priority,
                due_date=due_date if due_date is not None else current_todo.due_date,
                created_at=current_todo.created_at,  # Preserve original creation time
                updated_at=now
            )
            
            print(f"DEBUG: Updating todo {todo_id}: title='{updated_todo.title}', completed={updated_todo.completed}")
            
            # Use fastlite update with Todo instance
            self.todos.update(updated_todo)
            
            print(f"DEBUG: Successfully updated todo {todo_id}")
            return True
            
        except Exception as e:
            print(f"Error updating todo: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    def update_todo_secure(self, todo_id: int, user_id: int, title=None, description=None, completed=None, priority=None, due_date=None) -> bool:
        """Update a todo with user ownership verification - SECURE VERSION"""
        try:
            # SECURITY: First verify ownership
            todo = self.get_todo_by_id(todo_id, user_id)
            if not todo:
                print(f"🚨 SECURITY: User {user_id} blocked from updating todo {todo_id} (not found or not owned)")
                return False
            
            # Use the clean update method with explicit parameters
            return self.update_todo(todo_id, user_id, title=title, description=description, completed=completed, priority=priority, due_date=due_date)
            
        except Exception as e:
            print(f"Error updating todo securely: {e}")
            return False
    
    def toggle_todo_completion(self, todo_id: int, user_id: int) -> bool:
        """Toggle completion status of a todo - CLEAN VERSION"""
        try:
            # SECURITY: Verify ownership before toggling
            todo = self.get_todo_by_id(todo_id, user_id)
            if not todo:
                print(f"🚨 SECURITY: User {user_id} blocked from toggling todo {todo_id} (not found or not owned)")
                return False
                
            new_status = not todo.completed
            print(f"DEBUG: Toggling todo {todo_id} from {todo.completed} to {new_status}")
            
            # Use explicit parameter instead of **kwargs
            return self.update_todo_secure(todo_id, user_id, completed=new_status)
            
        except Exception as e:
            print(f"Error toggling todo: {e}")
            return False
    
    def delete_todo(self, todo_id: int, user_id: int) -> bool:
        """Delete a todo, ensuring user ownership - SECURITY CRITICAL"""
        try:
            # SECURITY: Multiple ownership verification layers
            
            # First check: Get todo and verify it exists
            todo = self.todos.get(todo_id)
            if not todo:
                print(f"DEBUG: Todo {todo_id} not found for deletion")
                return False
                
            # Second check: Verify ownership
            if todo.user_id != user_id:
                print(f"🚨 SECURITY VIOLATION BLOCKED: User {user_id} tried to delete todo {todo_id} owned by {todo.user_id}")
                return False
                
            # Third check: Use our secure get method as final verification
            verified_todo = self.get_todo_by_id(todo_id, user_id)
            if not verified_todo:
                print(f"🚨 SECURITY: Final ownership verification failed for todo {todo_id}")
                return False
                
            # Safe to delete
            self.todos.delete(todo_id)
            print(f"DEBUG: User {user_id} successfully deleted todo {todo_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting todo: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get todo statistics for a specific user - SECURITY: Only their todos"""
        try:
            # Use our secure method to get only user's todos
            todos = self.get_todos_by_user(user_id)
            total = len(todos)
            completed = sum(1 for todo in todos if todo.completed)
            pending = total - completed
            
            return {
                'total': total,
                'completed': completed, 
                'pending': pending,
                'completion_rate': completed / total if total > 0 else 0
            }
            
        except Exception as e:
            print(f"Error calculating user stats: {e}")
            return {'total': 0, 'completed': 0, 'pending': 0, 'completion_rate': 0}
    
    # Admin-specific methods for built-in admin integration
    
    def get_all_todos_admin(self, completed: Optional[bool] = None, limit: int = 50) -> List[tuple]:
        """
        Get todos across all users for admin view
        Returns tuples with user information joined
        ADMIN ONLY - bypasses user ownership checks
        """
        try:
            if completed is not None:
                query = """
                SELECT t.id, t.title, t.description, t.completed, t.priority, 
                       t.created_at, u.username, u.email, t.user_id
                FROM todo t
                JOIN user u ON t.user_id = u.id  
                WHERE t.completed = ?
                ORDER BY t.created_at DESC
                LIMIT ?
                """
                return self.db.q(query, (completed, limit))
            else:
                query = """
                SELECT t.id, t.title, t.description, t.completed, t.priority,
                       t.created_at, u.username, u.email, t.user_id
                FROM todo t
                JOIN user u ON t.user_id = u.id
                ORDER BY t.created_at DESC
                LIMIT ?
                """
                return self.db.q(query, (limit,))
                
        except Exception as e:
            print(f"Error fetching admin todos: {e}")
            return []
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system-wide statistics for admin dashboard"""
        try:
            # Todo statistics
            todo_stats = {}
            total_todos = len(list(self.todos()))
            completed_todos = len(list(self.todos(where="completed = 1")))
            pending_todos = total_todos - completed_todos
            
            todo_stats = {
                'total': total_todos,
                'completed': completed_todos,
                'pending': pending_todos
            }
            
            # Priority statistics
            priority_stats = {}
            for priority in ['low', 'medium', 'high']:
                count = len(list(self.todos(where="priority = ?", where_args=(priority,))))
                if count > 0:
                    priority_stats[priority] = count
            
            # User statistics (basic count - detailed stats handled by built-in admin)
            user_count_query = "SELECT COUNT(*) as count FROM user"
            user_result = self.db.q(user_count_query)
            user_count = user_result[0][0] if user_result else 0
            
            active_user_query = "SELECT COUNT(*) as count FROM user WHERE active = 1"
            active_result = self.db.q(active_user_query)  
            active_users = active_result[0][0] if active_result else 0
            
            # Recent activity (simplified)
            recent_activity = self._get_recent_activity(limit=10)
            
            return {
                'todo_stats': todo_stats,
                'priority_stats': priority_stats, 
                'user_count': user_count,
                'active_users': active_users,
                'recent_activity': recent_activity
            }
            
        except Exception as e:
            print(f"Error calculating system stats: {e}")
            return {
                'todo_stats': {'total': 0, 'completed': 0, 'pending': 0},
                'priority_stats': {},
                'user_count': 0,
                'active_users': 0, 
                'recent_activity': []
            }
    
    def admin_delete_todo(self, todo_id: int) -> bool:
        """Admin can delete any todo (bypasses user ownership check) - ADMIN ONLY"""
        try:
            todo = self.todos.get(todo_id)
            if not todo:
                print(f"ADMIN: Todo {todo_id} not found for deletion")
                return False
                
            self.todos.delete(todo_id)
            print(f"ADMIN: Successfully deleted todo {todo_id} (was owned by user {todo.user_id})")
            return True
            
        except Exception as e:
            print(f"Error deleting todo (admin): {e}")
            return False
    
    def delete_user_todos(self, user_id: int) -> bool:
        """Delete all todos for a user (called when user is deleted) - ADMIN ONLY"""
        try:
            # Get all todos for user (using raw query for admin operation)
            user_todos = list(self.todos(where="user_id = ?", where_args=(user_id,)))
            
            # Delete each todo
            deleted_count = 0
            for todo in user_todos:
                self.todos.delete(todo.id)
                deleted_count += 1
                
            print(f"ADMIN: Deleted {deleted_count} todos for user {user_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting user todos: {e}")
            return False
    
    def _get_recent_activity(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent todo activity for admin dashboard"""
        try:
            query = """
            SELECT 'Todo created' as action, u.username, t.created_at as timestamp
            FROM todo t
            JOIN user u ON t.user_id = u.id
            ORDER BY t.created_at DESC
            LIMIT ?
            """
            
            results = self.db.q(query, (limit,))
            
            return [
                {
                    'action': row[0],
                    'username': row[1], 
                    'timestamp': row[2]
                }
                for row in results
            ]
            
        except Exception as e:
            print(f"Error fetching recent activity: {e}")
            return []
    
    def get_todo_counts_by_user(self) -> List[tuple]:
        """Get todo counts grouped by user (for admin reporting)"""
        try:
            query = """
            SELECT u.username, u.email, 
                   COUNT(t.id) as total_todos,
                   SUM(CASE WHEN t.completed = 1 THEN 1 ELSE 0 END) as completed_todos
            FROM user u
            LEFT JOIN todo t ON u.id = t.user_id
            GROUP BY u.id, u.username, u.email
            ORDER BY total_todos DESC
            """
            
            return self.db.q(query)
            
        except Exception as e:
            print(f"Error getting todo counts by user: {e}")
            return []
    
    # DEBUG AND SECURITY AUDIT METHODS
    
    def debug_all_todos(self) -> List[Dict[str, Any]]:
        """DEBUG: Get all todos with ownership info"""
        try:
            query = """
            SELECT t.id, t.title, t.user_id, u.username, u.role, t.created_at
            FROM todo t
            JOIN user u ON t.user_id = u.id
            ORDER BY t.created_at DESC
            """
            
            results = self.db.q(query)
            return [
                {
                    'todo_id': row[0],
                    'title': row[1],
                    'owner_id': row[2],
                    'owner_name': row[3],
                    'owner_role': row[4],
                    'created_at': row[5]
                }
                for row in results
            ]
            
        except Exception as e:
            print(f"Error in debug query: {e}")
            return []
    
    def security_audit_todos(self, requesting_user_id: int) -> Dict[str, Any]:
        """SECURITY AUDIT: Check for any todos accessible by wrong users"""
        try:
            # Get what this user should see
            user_todos = self.get_todos_by_user(requesting_user_id)
            user_todo_ids = [todo.id for todo in user_todos]
            
            # Get all todos in system
            all_todos = self.debug_all_todos()
            
            # Check for violations
            violations = []
            for todo in all_todos:
                if todo['todo_id'] in user_todo_ids and todo['owner_id'] != requesting_user_id:
                    violations.append(todo)
            
            return {
                'requesting_user': requesting_user_id,
                'user_todos_count': len(user_todos),
                'total_todos_count': len(all_todos),
                'violations': violations,
                'security_status': 'VIOLATED' if violations else 'SECURE'
            }
            
        except Exception as e:
            print(f"Security audit failed: {e}")
            return {'security_status': 'AUDIT_FAILED', 'error': str(e)}
    
    # Utility methods
    
    def cleanup_database(self):
        """Clean up orphaned records and optimize database"""
        try:
            # Remove todos for non-existent users (should not happen with foreign keys)
            orphan_query = """
            DELETE FROM todo 
            WHERE user_id NOT IN (SELECT id FROM user)
            """
            result = self.db.execute(orphan_query)
            print(f"Cleaned up {result.rowcount if hasattr(result, 'rowcount') else 'some'} orphaned todos")
            
            # Vacuum database to optimize
            self.db.execute("VACUUM")
            
            print("✅ Database cleanup completed")
            
        except Exception as e:
            print(f"❌ Database cleanup failed: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information for system admin"""
        try:
            # Get table information
            tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
            tables = [row[0] for row in self.db.q(tables_query)]
            
            # Get database size (approximate)
            size_query = "SELECT COUNT(*) FROM sqlite_master"
            schema_objects = self.db.q(size_query)[0][0]
            
            return {
                'tables': tables,
                'schema_objects': schema_objects,
                'db_path': str(self.db.db)
            }
            
        except Exception as e:
            print(f"Error getting database info: {e}")
            return {'tables': [], 'schema_objects': 0, 'db_path': 'unknown'}