# Python Generators - 0x00

## Project Overview

This project focuses on mastering Python generators to efficiently handle large datasets, process data in batches, and simulate real-world scenarios involving live updates and memory-efficient computations.

## Learning Objectives

- Master Python Generators for iterative data processing
- Handle Large Datasets with batch processing and lazy loading
- Simulate Real-world Scenarios with live data updates
- Optimize Performance using generators for aggregate functions
- Apply SQL Knowledge for dynamic data fetching

## Requirements

- Python 3.x
- SQLite (included with Python)
- Understanding of yield and generator functions
- Familiarity with SQL and database operations

## Installation

No additional installation required! SQLite comes pre-installed with Python.

If you want to use MySQL instead:
```bash
# For Ubuntu/Debian
sudo apt install mysql-server

# For macOS
brew install mysql

# Install Python MySQL connector
pip install mysql-connector-python
```

## Project Structure

```
python-generators-0x00/
├── seed.py           # Database seeding script
├── README.md         # This file
├── user_data.csv     # Sample user data
└── ALX_prodev.db     # SQLite database file (created automatically)
```

## Task 0: Getting Started with Python Generators

### Objective
Create a generator that streams rows from an SQL database one by one.

### Files
- `seed.py`: Python script that sets up the database and seeds it with data

### Functions in seed.py

1. **connect_db()**: Connects to the database server
2. **create_database(connection)**: Creates the database ALX_prodev if it does not exist
3. **connect_to_prodev()**: Connects to the ALX_prodev database
4. **create_table(connection)**: Creates the user_data table if it does not exist
5. **insert_data(connection, data)**: Inserts data from CSV file into the database

### Database Schema

**Database**: ALX_prodev  
**Table**: user_data

| Column    | Type         | Constraints              |
|-----------|--------------|--------------------------|
| user_id   | TEXT/CHAR(36)| Primary Key, Indexed     |
| name      | TEXT/VARCHAR | NOT NULL                 |
| email     | TEXT/VARCHAR | NOT NULL                 |
| age       | INTEGER/DECIMAL | NOT NULL              |

### Usage

1. **Ensure you have the user_data.csv file** in the same directory

2. **Make the test script executable and run it:**
```bash
chmod +x 0-main.py
./0-main.py
```

Or run directly with Python:
```bash
python3 0-main.py
```

### Expected Output

```
connection successful
Table user_data created successfully
Database ALX_prodev is present 
[('00234e50-34eb-4ce2-94ec-26e3fa749796', 'Dan Altenwerth Jr.', 'Molly59@gmail.com', 67), ...]
```

## Implementation Notes

### SQLite Version (Default)
- Uses SQLite for simplicity and portability
- Database stored as `ALX_prodev.db` file
- No server setup required
- Ideal for development and testing

### MySQL Version
If your project requires MySQL specifically:
1. Install MySQL server
2. Update connection parameters in `seed.py`:
   - host: localhost
   - user: root
   - password: your_mysql_password
3. Replace SQLite code with MySQL connector code

## Troubleshooting

### CSV File Not Found
Ensure `user_data.csv` is in the same directory as `seed.py`

### Permission Denied
Make sure the script is executable:
```bash
chmod +x 0-main.py
chmod +x seed.py
```

### Database Already Exists
The script checks for existing data and won't duplicate entries. To reset:
```bash
rm ALX_prodev.db  # For SQLite
```

## Submission Checklist

- [ ] `seed.py` file created with all required functions
- [ ] `README.md` file documenting the project
- [ ] `user_data.csv` file present in directory
- [ ] Code tested and working correctly
- [ ] All files committed to Git
- [ ] Pushed to GitHub repository: `alx-backend-python`
- [ ] Project in directory: `python-generators-0x00`
- [ ] Manual QA review requested

## Git Commands for Submission

```bash
# Navigate to your project directory
cd alx-backend-python/python-generators-0x00

# Add your files
git add seed.py README.md

# Commit your changes
git commit -m "Add seed.py and README.md for Python Generators task 0"

# Push to GitHub
git push origin main
```

## Author

ALX Backend Python Project

## License

This project is part of the ALX Software Engineering Program.
