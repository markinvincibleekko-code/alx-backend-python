#!/usr/bin/python3
"""
Module for batch processing large data from database using generators
"""
import sqlite3


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows from user_data table in batches
    
    Args:
        batch_size (int): Number of rows to fetch per batch
        
    Yields:
        list: A list of dictionaries containing user data for each batch
    """
    connection = sqlite3.connect('ALX_prodev.db')
    cursor = connection.cursor()
    
    # Execute query to fetch all users
    cursor.execute("SELECT user_id, name, email, age FROM user_data")
    
    # Fetch and yield rows in batches
    while True:
        batch = cursor.fetchmany(batch_size)
        
        if not batch:
            break
            
        # Convert batch rows to list of dictionaries
        yield [
            {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            for row in batch
        ]
    
    # Clean up
    cursor.close()
    connection.close()


def batch_processing(batch_size):
    """
    Processes batches of users and filters those over the age of 25
    
    Args:
        batch_size (int): Number of rows to process per batch
    """
    # Loop 1: Iterate over batches from the generator
    for batch in stream_users_in_batches(batch_size):
        # Loop 2: Iterate over users in each batch
        for user in batch:
            # Filter users over age 25
            if user['age'] > 25:
                print(user)