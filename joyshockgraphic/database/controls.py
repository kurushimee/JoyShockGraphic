import sqlite3


# This class handles interaction with the database
class DbControls:
    def __init__(self):
        # Initialise database
        self.con = sqlite3.connect("joyshockgraphic/resources/data.db")
        self.cur = self.con.cursor()

    # This function handles select operations
    def select(self, field: str, table: str, condition=""):
        # Select entries from the database
        if condition != "":
            condition = " WHERE " + condition
        return self.cur.execute(
            f'SELECT {field} FROM "{table}"{condition}'
        ).fetchall()

    # This function handles insert operations
    def insert(self, table: str, values: tuple, fields=()):
        # Insert new entry to the database
        f = "" if fields == () else ",".join([f'"{x}"' for x in fields])
        v = list()
        for x in values:
            if x is None:
                v.append("NULL")
            else:
                v.append(f'"{x}"')
        v = ",".join(v)
        self.cur.execute(f'INSERT INTO "{table}"{f} VALUES({v})')
        self.con.commit()

    # This function handles update operations
    def update(self, table: str, field: str, value: str, condition=""):
        # Update an entry in the database if it exists
        if condition != "":
            condition = "WHERE " + condition
        value = f'"{value}"' if value is not None else "NULL"
        self.cur.execute(
            f"""UPDATE "{table}"
                SET {field} = {value}
                {condition}"""
        )
        self.con.commit()

    # This function handles delete operations
    def delete(self, table, condition):
        # Delete an entry in the database
        self.cur.execute(f'DELETE FROM "{table}" WHERE {condition}')
        self.con.commit()

    # This function is used to close connection with the db on program exit
    def close(self):
        self.con.close()
