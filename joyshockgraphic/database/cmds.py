import joyshockgraphic.database.profiles as profiles


# This function gets command's entry from the db
def get_command_data(
        self, command: str, default: str, field: str = "bind"
):
    # Get existing field or default value
    field = self.db.select(
        field, self.curr_prof, f'command = "{command}"'
    )
    return (
        field[0][0]
        if len(field) > 0 and field[0][0] is not None
        else default
    )


# This function updates command's entry in the db
def set_command_data(
        self,
        command: str,
        chord=None,
        action=None,
        bind=None,
        event=None,
        name=None,
):
    # Update an existing bind
    if (
            len(
                self.db.select("*", self.curr_prof, f'command = "{command}"')
            )
            > 0
    ):
        for field, value in (
                ("chord", chord),
                ("action", action),
                ("bind", bind),
                ("event", event),
                ("name", name),
        ):
            if value:
                self.db.update(
                    self.curr_prof, field, value, f'command = "{command}"'
                )
    else:
        self.db.insert(
            self.curr_prof, (command, chord, action, bind, event, name)
        )

    # Export profile to .txt
    profiles.export(self.db, self.curr_prof)
