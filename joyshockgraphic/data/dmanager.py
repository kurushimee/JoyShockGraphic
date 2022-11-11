import sqlite3


class DManager:
    def __init__(self):
        # Initialise database
        self.con = sqlite3.connect("joyshockgraphic/resources/data.db")
        self.cur = self.con.cursor()

    def create_profile(self, display_name: str, file_name: str):
        # Create a new table for the profile
        self.cur.execute(
            f"""CREATE TABLE "{file_name}" (
                                command  STRING,
                                chord    STRING,
                                [action] STRING,
                                bind     STRING,
                                event    STRING,
                                name     STRING
                             );"""
        )
        # Create a new profile entry in the profiles table
        self.insert(
            "profiles",
            (display_name, file_name),
        )

    def edit_profile(self, name_old: tuple, name_new: tuple):
        # Rename profile's table
        self.cur.execute(
            f'ALTER TABLE "{name_old[1]}" RENAME TO "{name_new[1]}"'
        )
        # Change the display name
        self.update(
            "profiles",
            "display_name",
            name_new[0],
            f'display_name="{name_old[0]}"',
        )
        # Change the file name
        self.update(
            "profiles",
            "file_name",
            name_new[1],
            f'file_name="{name_old[1]}"',
        )

    def delete_profile(self, display_name: str):
        # Find file name of the profile based on display name
        file_name = self.select(
            "file_name", "profiles", f'display_name = "{display_name}"'
        )[0][0]
        # Delete profile's table
        self.cur.execute(f'DROP TABLE "{file_name}"')
        # Delete profile's entry in the database
        self.delete(
            "profiles",
            f'display_name = "{display_name}" AND file_name = "{file_name}"',
        )

    def export_profile(self, profile):
        with open(f"AutoLoad/{profile}.txt", "w+") as f:
            # Collect commands from the profile
            commands = dict()
            for result in self.select("command", profile):
                if len(result) == 0:
                    continue
                chord = self.select(
                    "chord", profile, f'command = "{result[0]}"'
                )
                chord = chord[0][0] if len(chord) > 0 and chord[0][0] else ""
                command = (
                    ",".join((result[0], chord[0][0]))
                    if len(chord) > 0
                    else result[0]
                )
                if command not in commands:
                    commands[command] = []
                if len(chord) > 0:
                    chord = f'= "{chord}"'
                else:
                    chord = "IS NULL"
                result = self.select(
                    "action, bind, event",
                    profile,
                    f'command = "{result[0]}" AND chord {chord}',
                )
                if len(result) > 0:
                    bind = list()
                    for x in result[0]:
                        if x is not None:
                            bind.append(x)
                    commands[command].append("".join(bind))

            # Generate a profile string
            write = "RESET_MAPPINGS\n"
            for key, value in commands.items():
                value = " ".join(value)
                value = key if len(value) == 0 else f"{key} = {value}"
                write += value + "\n"

            f.write(write)

    def select(self, field: str, table: str, condition=""):
        # Select entries from the database
        if condition != "":
            condition = " WHERE " + condition
        return self.cur.execute(
            f'SELECT {field} FROM "{table}"{condition}'
        ).fetchall()

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

    def delete(self, table, condition):
        # Delete an entry in the database
        self.cur.execute(f'DELETE FROM "{table}" WHERE {condition}')
        self.con.commit()

    def close(self):
        self.con.close()
