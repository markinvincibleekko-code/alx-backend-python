#!/usr/bin/python3
"""
Module for lazy loading paginated data from database using generators
"""
import sqlite3


def paginate_users(page_size, offset):
    """
    Fetches a page of users from the database
    
    Args:
        page_size (int): Number of users per page
        offset (int): Starting position for the page
        
    Returns:
        list: List of dictionaries containing user data
    """
    connection = sqlite3.connect('ALX_prodev.db')
    connection.row_factory = sqlite3.Row  # Enable dictionary-like access
    cursor = connection.cursor()
    
    cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
    rows = cursor.fetchall()
    
    # Convert Row objects to dictionaries
    result = [dict(row) for row in rows]
    
    connection.close()
    return result


def lazy_pagination(page_size):
    """
    Generator function that lazily loads paginated data
    Fetches the next page only when needed
    
    Args:
        page_size (int): Number of users per page
        
    Yields:
        list: A page (list of dictionaries) of user data
    """
    offset = 0
    
    # Single loop that continues until no more data
    while True:
        page = paginate_users(page_size, offset)
        
        # Stop if no more data
        if not page:
            break
        
        yield page
        offset += page_size