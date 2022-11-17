# This function creates a new profile
def create(self, display_name: str, file_name: str):
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


# This function edits profile's information
def edit(self, name_old: tuple, name_new: tuple):
    if name_old[1] != name_new[1]:
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


# This function deletes profile
def delete(self, display_name: str):
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


# This function exports profile to .txt
def export(self, profile):
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
                        bind.append(str(x))
                commands[command].append("".join(bind))

        # Generate a profile string
        write = "RESET_MAPPINGS\n"
        for key, value in commands.items():
            value = " ".join(value)
            value = key if len(value) == 0 else f"{key} = {value}"
            write += value + "\n"

        f.write(write)
