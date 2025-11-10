import sqlite3
import functools

#### decorator to log SQL queries

def log_queries(func):
    """
    Decorator that logs SQL queries before executing them.
    
    Args:
        func: The function to be decorated
        
    Returns:
        The wrapped function that logs queries before execution
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract the query from arguments
        # Check if 'query' is in kwargs
        if 'query' in kwargs:
            query = kwargs['query']
        # Otherwise, assume it's the first positional argument
        elif args:
            query = args[0]
        else:
            query = None
        
        # Log the query if found
        if query:
            print(f"Executing query: {query}")
        
        # Execute the original function
        return func(*args, **kwargs)
    
    return wrapper


@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results


#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")