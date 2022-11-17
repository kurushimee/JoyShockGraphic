from PyQt5.QtWidgets import QPushButton, QInputDialog
from joyshockgraphic.database import cmds as db_cmds


# This function sets a bind for the command based on the picked button
def set_bind(self, bind: str):
    if self.curr_cmd == "Chord":
        db_cmds.set_command_data(self, self.curr_cmd, chord=bind)
    else:
        db_cmds.set_command_data(self, self.curr_cmd, bind=bind)
    command = "pb" + self.correct_command_name(self.curr_cmd)
    for button in self.bgPickBind.buttons():
        if button.objectName() == command:
            button.setText(bind)


# This function handles picked bind
def bind_picked(self, sender: QPushButton):
    exceptions = {
        "tilda": "`",
        "zero": "0",
        "one": "1",
        "two": "2",
        "three": "3",
        "four": "4",
        "five": "5",
        "six": "6",
        "seven": "7",
        "eight": "8",
        "nine": "9",
        "lpar": "[",
        "rpar": "]",
        "backslash": "\\",
        "semicolon": ";",
        "quote": "'",
        "question": "?",
        "comma": ",",
        "period": ".",
    }
    bind = sender.objectName()
    if bind in exceptions:
        bind = exceptions[bind]
    set_bind(self, bind)


# This function handles advanced binding dialog
def advanced_dlg(self):
    bind, ok = QInputDialog.getText(
        self, "Advanced binding", "Custom binding:"
    )
    if ok:
        set_bind(self, bind)
