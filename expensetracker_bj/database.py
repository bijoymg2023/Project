import mysql.connector
from mysql.connector import Error

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'expense_tracker'
}

def create_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def execute_query(query, data=None):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute(query, data)
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()
    return None

def fetch_query(query, data=None):
    connection = create_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute(query, data)
            return cursor.fetchall()
        except Error as e:
            print(f"Error: {e}")
        finally:
            cursor.close()
            connection.close()
    return None

