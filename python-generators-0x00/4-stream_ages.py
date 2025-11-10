#!/usr/bin/python3
"""
Module for memory-efficient aggregation using generators
Calculates average age without loading entire dataset into memory
"""
import sqlite3


def stream_user_ages():
    """
    Generator function that yields user ages one by one from the database
    
    Yields:
        int: Age of each user
    """
    connection = sqlite3.connect('ALX_prodev.db')
    cursor = connection.cursor()
    
    # Execute query to fetch only ages
    cursor.execute("SELECT age FROM user_data")
    
    # Loop 1: Fetch and yield ages one by one
    for row in cursor:
        yield row[0]
    
    # Clean up
    cursor.close()
    connection.close()


def calculate_average_age():
    """
    Calculates the average age of users using the generator
    Memory-efficient as it doesn't load all ages into memory at once
    
    Returns:
        float: Average age of all users
    """
    total_age = 0
    count = 0
    
    # Loop 2: Iterate over ages from generator
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    # Calculate and return average
    average_age = total_age / count if count > 0 else 0
    return average_age


# Main execution
if __name__ == "__main__":
    average_age = calculate_average_age()
    print(f"Average age of users: {average_age:.2f}")