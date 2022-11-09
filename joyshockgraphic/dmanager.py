import sqlite3


class DManager:
    def __init__(self):
        # Initialise database
        self.con = sqlite3.connect("joyshockgraphic/resources/data.db")
        self.cur = self.con.cursor()

    def create_profile(self, display_name: str, file_name: str):
        # Create a new profile entry in the profiles table
        self.insert(
            "profiles",
            (display_name, file_name),
        )
        # Create a new table for the profile
        self.cur.execute(
            f"""CREATE TABLE "{file_name}" (
                                command  STRING,
                                chord    STRING,
                                [action] STRING,
                                bind     STRING,
                                event    STRING
                             );"""
        )
        self.con.commit()

    # Change the display name in the profiles list
    # and file name of a profile in the database
    def edit_profile(self, old_data: tuple, new_data: tuple):
        self.update(
            "profiles",
            "display_name",
            new_data[0],
            f"display_name={old_data[0]}",
        )
        self.update(
            "profiles",
            "file_name",
            new_data[1],
            f"file_name={old_data[1]}",
        )

    # Select entries from the database
    def select(self, field: str, table: str, condition=""):
        return self.cur.execute(
            f"SELECT {field} FROM {table} WHERE {condition}"
        ).fetchall()

    # Insert new entry to the database
    def insert(self, table: str, values: tuple, fields=()):
        f = "" if fields == () else ",".join([f'"{x}"' for x in fields])
        v = ",".join([f'"{x}"' for x in values])
        self.cur.execute(f"INSERT INTO {table}{f} VALUES({v})")
        self.con.commit()

    # Update an entry in the database
    def update(self, table: str, field: str, value: str, condition=""):
        self.cur.execute(
            f"""UPDATE {table}
                             SET {field} = {value}
                             WHERE {condition}"""
        )
        self.con.commit()

    # Delete an entry in the database
    def delete(self, table, condition):
        self.cur.execute(f"DELETE FROM {table} WHERE {condition}")
        self.con.commit()

    def close(self):
        self.con.close()
