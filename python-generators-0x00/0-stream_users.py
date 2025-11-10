#!/usr/bin/python3
"""
Module for streaming user data from database using generators
"""
import sqlite3


def stream_users():
    """
    Generator function that streams rows from the user_data table one by one
    
    Yields:
        dict: A dictionary containing user data (user_id, name, email, age)
    """
    # Connect to the database
    connection = sqlite3.connect('ALX_prodev.db')
    cursor = connection.cursor()
    
    # Execute query to fetch all users
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    
    # Fetch and yield rows one by one
    for row in cursor:
        yield {
            'user_id': row[0],
            'name': row[1],
            'email': row[2],
            'age': row[3]
        }
    
    # Clean up
    cursor.close()
    connection.close()