from mysql import connector
import os

class Database:
    def __init__(self):
        self.connection = connector.connect(
            host=os.getenv('HOST'),
            user=os.getenv('USER'),
            password=os.getenv('PASSWORD'),
            database=os.getenv('DATABASE')
        )
        self.cursor = self.connection.cursor()

    def __enter__(self):
        self.connection.start_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.connection.rollback()
            print(f"Error: {exc_val}")
        else:
            self.connection.commit()
        self.cursor.close()
        self.connection.close()

    def create(self, table, data):
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        values = tuple(data.values())
        self.cursor.execute(query, values)
        print("Record created successfully!")
        # Retrieve the auto-incremented ID
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        last_insert_id = self.cursor.fetchone()[0]
        return last_insert_id

    def read(self, table, condition=None):
        query = f"SELECT * FROM {table}"
        if condition:
            query += f" WHERE {condition}"
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def readTrips(self, trip_name, chat_id):
        query = f"SELECT * FROM users INNER JOIN principal ON users.user_id = principal.user_id \
            INNER JOIN trips ON principal.trip_id = trips.trip_id \
                WHERE users.chat_id = {chat_id} AND trips.trip_name = '{trip_name}'"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update(self, table, data, condition):
        columns = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {columns} WHERE {condition}"
        values = tuple(data.values())
        self.cursor.execute(query, values)
        print("Record updated successfully!")
        # Retrieve the auto-incremented ID
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        last_insert_id = self.cursor.fetchone()[0]
        return last_insert_id

    def delete(self, table, condition):
        query = f"DELETE FROM {table} WHERE {condition}"
        self.cursor.execute(query)
        print("Record deleted successfully!")
        # Retrieve the auto-incremented ID
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        last_insert_id = self.cursor.fetchone()[0]
        return last_insert_id
    
