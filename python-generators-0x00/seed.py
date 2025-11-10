#!/usr/bin/python3
"""
Module for seeding the ALX_prodev database with user data (SQLite version)
"""
import sqlite3
import csv
import uuid
import os


def connect_db():
    """
    Connects to the SQLite database server
    
    Returns:
        connection object if successful, None otherwise
    """
    try:
        # Connect to SQLite (creates file if doesn't exist)
        connection = sqlite3.connect('ALX_prodev.db')
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to SQLite: {e}")
        return None


def create_database(connection):
    """
    Creates the database ALX_prodev if it does not exist
    For SQLite, this is handled by connect_db()
    
    Args:
        connection: SQLite connection object
    """
    # SQLite creates the database file automatically
    # This function exists for compatibility with the original interface
    pass


def connect_to_prodev():
    """
    Connects to the ALX_prodev database
    
    Returns:
        connection object if successful, None otherwise
    """
    try:
        connection = sqlite3.connect('ALX_prodev.db')
        return connection
    except sqlite3.Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None


def create_table(connection):
    """
    Creates a table user_data if it does not exist with the required fields
    
    Args:
        connection: SQLite connection object
    """
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL
        )
        """
        cursor.execute(create_table_query)
        
        # Create index on user_id
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_id ON user_data(user_id)
        """)
        
        connection.commit()
        print("Table user_data created successfully")
        cursor.close()
    except sqlite3.Error as e:
        print(f"Error creating table: {e}")


def insert_data(connection, csv_file):
    """
    Inserts data into the database if it does not exist
    
    Args:
        connection: SQLite connection object
        csv_file: path to the CSV file containing user data
    """
    try:
        cursor = connection.cursor()
        
        # Check if data already exists
        cursor.execute("SELECT COUNT(*) FROM user_data")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print("Data already exists in user_data table")
            cursor.close()
            return
        
        # Read and insert data from CSV
        if not os.path.exists(csv_file):
            print(f"CSV file {csv_file} not found")
            cursor.close()
            return
            
        with open(csv_file, 'r') as file:
            csv_reader = csv.DictReader(file)
            
            insert_query = """
            INSERT INTO user_data (user_id, name, email, age)
            VALUES (?, ?, ?, ?)
            """
            
            for row in csv_reader:
                # Generate UUID if not present or use existing
                user_id = row.get('user_id', str(uuid.uuid4()))
                name = row['name']
                email = row['email']
                age = int(float(row['age']))  # Convert to int
                
                cursor.execute(insert_query, (user_id, name, email, age))
        
        connection.commit()
        print(f"Data inserted successfully from {csv_file}")
        cursor.close()
        
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found")
    except Exception as e:
        print(f"Error reading CSV file: {e}")