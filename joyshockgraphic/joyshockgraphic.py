import sys
from dmanager import DManager
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QInputDialog,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("joyshockgraphic/resources/joyshockgraphic.ui", self)

        # Initialise database manager
        self.dman = DManager()
        # Populate lwProfiles with already existing profiles
        self.populate_list()
        # Enable profile specific buttons based on selection
        self.lwProfiles.itemSelectionChanged.connect(self.selection_changed)

        # Connect button groups
        self.bgLibrary.buttonClicked.connect(self.handle_profile)
        self.bgConfig.buttonClicked.connect(self.config)
        self.bgLoadInput.buttonClicked.connect(self.load_input)
        self.bgPickBind.buttonClicked.connect(self.pick_bind)
        self.bgSwitchInput.buttonClicked.connect(self.switch_input)

        # Connect rest of the controls
        # Joysticks
        self.cbRmode.currentIndexChanged.connect(self.on_stick_mode_change)
        self.cbLmode.currentIndexChanged.connect(self.on_stick_mode_change)
        # Gyro line edits
        self.leRWC.returnPressed.connect(self.on_gyro_le)
        self.leSens.returnPressed.connect(self.on_gyro_le)
        self.leGyroSens.returnPressed.connect(self.on_gyro_le)
        self.leVSens.returnPressed.connect(self.on_gyro_le)
        self.leMinGyroSens.returnPressed.connect(self.on_gyro_le)
        self.leMinVSens.returnPressed.connect(self.on_gyro_le)
        self.leMinThreshold.returnPressed.connect(self.on_gyro_le)
        self.leMaxGyroSens.returnPressed.connect(self.on_gyro_le)
        self.leMaxVSens.returnPressed.connect(self.on_gyro_le)
        self.leMaxThreshold.returnPressed.connect(self.on_gyro_le)
        # Gyro check boxes
        self.chAutoCalibrate.stateChanged.connect(self.on_gyro_ch)
        self.chAccel.stateChanged.connect(self.on_gyro_ch)
        self.chVSens.stateChanged.connect(self.on_gyro_ch)
        self.chMinVSens.stateChanged.connect(self.on_gyro_ch)
        self.chMaxVSens.stateChanged.connect(self.on_gyro_ch)

    def populate_list(self):
        self.lwProfiles.clear()
        for profile in self.dman.select("display_name", "profiles"):
            display_name = profile[0]
            self.lwProfiles.addItem(display_name)
        self.selection_changed()

    def selection_changed(self):
        currentItem = self.lwProfiles.currentItem()
        if currentItem and currentItem.text() in [
            x[0] for x in self.dman.select("display_name", "profiles")
        ]:
            condition = True
            self.configure()
        else:
            condition = False
            self.mainTabs.setTabEnabled(1, False)
        self.pbEdit.setEnabled(condition)
        self.pbDelete.setEnabled(condition)

    def handle_profile(self, sender: QPushButton):
        cond = sender.objectName()
        if cond == "pbCreate":
            self.create()
        elif cond == "pbEdit":
            self.edit()
        elif cond == "pbDelete":
            self.delete()

    def config(self, sender: QPushButton):
        name, ok = QInputDialog.getText(
            self, "Rename command", "New command name:"
        )
        if ok:
            exceptions = {"-": "Minus", "+": "Plus"}
            command = (
                self.e_command
                if self.e_command not in exceptions
                else exceptions[self.e_command]
            )
            for button in self.bgPickBind.buttons():
                if button.objectName() == "pb" + command:
                    self.set_command_data(self.e_command, name=name)
                    button.setText(name)

    def load_input(self, sender: QPushButton):
        # Set current command for editing
        exceptions = {"pbMinus": "-", "pbPlus": "+"}
        obj_name = sender.objectName()
        self.e_command = (
            obj_name[2:-8]
            if obj_name not in exceptions
            else exceptions[obj_name]
        )
        # Enable command editing controls
        self.cbEvent.setEnabled(True)
        self.lAction.setEnabled(True)
        self.cbAction.setEnabled(True)
        self.lChord.setEnabled(True)
        self.pbChord.setEnabled(True)
        self.pbRename.setEnabled(True)
        # Load command data
        events = {
            0: 0,
            "\\": 1,
            "/": 2,
            "'": 3,
            "_": 4,
            "+": 5,
        }
        self.cbEvent.setCurrentIndex(
            events[self.get_command_data(self.e_command, 0, "event")]
        )
        actions = {
            0: 0,
            "^": 1,
            "!": 2,
        }
        self.cbAction.setCurrentIndex(
            actions[self.get_command_data(self.e_command, 0, "action")]
        )
        self.pbChord.setText(
            self.get_command_data(self.e_command, "None", "chord")
        )

    def pick_bind(self, sender: QPushButton):
        dlg = uic.loadUi("joyshockgraphic/resources/picker.ui")
        exceptions = {"pbMinus": "-", "pbPlus": "+"}
        obj_name = sender.objectName()
        e_command_before = self.e_command
        self.e_command = (
            obj_name[2:]
            if obj_name not in exceptions
            else exceptions[obj_name]
        )
        dlg.bgKeyboard.buttonClicked.connect(self.on_keyboard_bg)
        dlg.exec_()
        self.e_command = e_command_before

    def switch_input(self, sender: QPushButton):
        tabs = {
            "pbButtons": 0,
            "pbDpad": 1,
            "pbTriggers": 2,
            "pbJoysticks": 3,
            "pbTouchpad": 4,
            "pbGyro": 5,
        }
        self.inputWidgets.setCurrentIndex(tabs[sender.objectName()])

    def on_keyboard_bg(self, sender: QPushButton):
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
        obj_name = sender.objectName()
        bind = obj_name if obj_name not in exceptions else exceptions[obj_name]

        self.set_command_data(self.e_command, bind=bind)
        commands = {"-": "pbMinus", "+": "pbPlus"}
        command = (
            "pb" + self.e_command
            if self.e_command not in commands
            else commands[self.e_command]
        )
        for button in self.bgPickBind.buttons():
            if button.objectName() == command:
                result = self.dman.select(
                    "name", self.e_profile, f'command = "{bind}"'
                )
                name = (
                    result[0][0] if len(result) > 0 and result[0][0] else bind
                )
                button.setText(name)

    def create(self):
        # Open profile creation dialog
        dlg = uic.loadUi("joyshockgraphic/resources/profile.ui")
        ok = dlg.exec_()
        if ok:
            # Create profile
            self.dman.create_profile(
                dlg.leDisplayName.text(),
                dlg.leFileName.text(),
            )
            self.populate_list()

    def edit(self):
        # Open profile creation dialog
        dlg = uic.loadUi("joyshockgraphic/resources/profile.ui")
        ok = dlg.exec_()
        if ok:
            display_name = self.lwProfiles.currentItem().text()
            self.dman.edit_profile(
                (
                    display_name,
                    self.dman.select(
                        "file_name",
                        "profiles",
                        f'display_name = "{display_name}"',
                    )[0][0],
                ),
                (dlg.leDisplayName.text(), dlg.leFileName.text()),
            )
            self.populate_list()

    def configure(self):
        # Enable configurator and set current profile
        self.mainTabs.setTabEnabled(1, True)
        self.e_profile = self.lwProfiles.currentItem().text()
        self.e_command = None
        self.init_configurator()

    def delete(self):
        # Deletes selected profile
        self.dman.delete_profile(self.lwProfiles.currentItem().text())
        self.populate_list()

    def closeEvent(self, event):
        self.dman.close()

    def get_command_data(
        self, command: str, default: str, field: str = "bind"
    ):
        # Get existing field or default value
        field = self.dman.select(
            field, self.e_profile, f'command = "{command}"'
        )
        return (
            field[0][0]
            if len(field) > 0 and field[0][0] is not None
            else default
        )

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
                self.dman.select("*", self.e_profile, f'command = "{command}"')
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
                    self.dman.update(
                        self.e_profile, field, value, f'command = "{command}"'
                    )
        else:
            self.dman.insert(
                self.e_profile, (command, chord, action, bind, event, name)
            )

    def init_configurator(self):
        # Init buttons
        special = {"pbMinus": "-", "pbPlus": "+"}
        for button in self.bgPickBind.buttons():
            # Cut off "pb" prefix from the button name
            name = (
                button.objectName()[2:]
                if button.objectName() not in special
                else special[button.objectName()]
            )
            result = self.dman.select(
                "name", self.e_profile, f'command = "{name}"'
            )
            if len(result) > 0 and result[0][0] is not None:
                name = result[0][0]
            # Change button's text according to it's bind in profile
            button.setText(self.get_command_data(name, "None"))

        # Init joysticks
        modes = {
            "AIM": 0,
            "FLICK": 1,
            "FLICK_ONLY": 2,
            "ROTATE_ONLY": 3,
            "MOUSE_RING": 4,
            "MOUSE_AREA": 5,
            "NO_MOUSE": 6,
            "SCROLL_WHEEL": 7,
        }
        self.cbRmode.setCurrentIndex(
            modes[self.get_command_data("RIGHT_STICK_MODE", "AIM")]
        )
        self.cbLmode.setCurrentIndex(
            modes[self.get_command_data("LEFT_STICK_MODE", "NO_MOUSE")]
        )

        # Init gyro
        self.leRWC.setText(
            str(self.get_command_data("REAL_WORLD_CALIBRATION", "45"))
        )
        self.leSens.setText(str(self.get_command_data("IN_GAME_SENS", "1")))
        auto_calibrate = {"ON": True, "OFF": False}
        self.chAutoCalibrate.setChecked(
            auto_calibrate[self.get_command_data("AUTO_CALIBRATE", "OFF")]
        )
        self.chAccel.setChecked(bool(self.get_command_data("accel", "True")))
        self.on_accel_change(self.chAccel.isChecked())

        self.leGyroSens.setText(
            str(self.get_command_data("GYRO_SENS", "3 3").split()[0])
        )
        self.chVSens.setChecked(bool(self.get_command_data("v_sens", "")))
        self.leVSens.setText(
            str(self.get_command_data("GYRO_SENS", "3 3").split()[1])
        )

        self.leMinGyroSens.setText(
            str(self.get_command_data("MIN_GYRO_SENS", "2 2").split()[0])
        )
        self.chMinVSens.setChecked(
            bool(self.get_command_data("min_v_sens", ""))
        )
        self.chMaxVSens.setChecked(
            bool(self.get_command_data("max_v_sens", ""))
        )
        self.leMaxGyroSens.setText(
            str(self.get_command_data("MAX_GYRO_SENS", "4 4").split()[1])
        )
        self.leMinThreshold.setText(
            str(self.get_command_data("MIN_GYRO_THRESHOLD", "0"))
        )
        self.leMaxThreshold.setText(
            str(self.get_command_data("MAX_GYRO_THRESHOLD", "75"))
        )

    def on_accel_change(self, state: bool):
        self.lGyroSens.setEnabled(not state)
        self.leGyroSens.setEnabled(not state)
        self.chVSens.setEnabled(not state)
        self.leVSens.setEnabled(self.chVSens.isChecked() and not state)

        self.lMinSens.setEnabled(state)
        self.lMaxSens.setEnabled(state)
        self.leMinGyroSens.setEnabled(state)
        self.leMaxGyroSens.setEnabled(state)
        self.lMinThreshold.setEnabled(state)
        self.lMaxThreshold.setEnabled(state)
        self.leMinThreshold.setEnabled(state)
        self.leMaxThreshold.setEnabled(state)
        self.chMinVSens.setEnabled(state)
        self.chMaxVSens.setEnabled(state)
        self.leMinVSens.setEnabled(self.chMinVSens.isChecked() and state)
        self.leMaxVSens.setEnabled(self.chMaxVSens.isChecked() and state)

    def on_stick_mode_change(self, value):
        modes = {
            0: "AIM",
            1: "FLICK",
            2: "FLICK_ONLY",
            3: "ROTATE_ONLY",
            4: "MOUSE_RING",
            5: "MOUSE_AREA",
            6: "NO_MOUSE",
            7: "SCROLL_WHEEL",
        }
        mode = (
            "RIGHT_STICK_MODE"
            if self.sender().objectName() == "cbRmode"
            else "LEFT_STICK_MODE"
        )
        self.set_command_data(mode, bind=modes[value])

    def on_gyro_le(self):
        value = self.sender().text()
        commands = {
            "leRWC": "REAL_WORLD_CALIBRATION",
            "leSens": "IN_GAME_SENS",
            "leGyroSens": "GYRO_SENS",
            "leVSens": "GYRO_SENS",
            "leMinGyroSens": "MIN_GYRO_SENS",
            "leMinVSens": "MIN_GYRO_SENS",
            "leMinThreshold": "MIN_GYRO_THRESHOLD",
            "leMaxGyroSens": "MAX_GYRO_SENS",
            "leMaxVSens": "MAX_GYRO_SENS",
            "leMaxThreshold": "MAX_GYRO_THRESHOLD",
        }

        # If horizontal or vertical sens, find the other one
        # for combined command value
        # If vertical sens and it's written in percent format,
        # calculate it's value based on horizontal sens
        v_sens_h = {
            "leVSens": "leGyroSens",
            "leMinVSens": "leMinGyroSens",
            "leMaxVSens": "leMaxGyroSens",
        }
        h_sens_v = {
            "leGyroSens": "leVSens",
            "leMinGyroSens": "leMinVSens",
            "leMaxGyroSens": "leMaxVSens",
        }
        default_sens = {
            "leGyroSens": "3",
            "leMinGyroSens": "2",
            "leMaxGyroSens": "4",
        }
        obj_name = self.sender().objectName()
        if obj_name in v_sens_h:
            h_sens = self.get_command_data(
                v_sens_h[obj_name],
                f"{default_sens[v_sens_h[obj_name]]} {value}",
            ).split()[0]
            v_sens = (
                int(h_sens) * (int(value[:-1]) / 100)
                if value[-1] == "%"
                else value
            )
            value = " ".join((h_sens, v_sens))
        if obj_name in h_sens_v:
            value = " ".join(
                (
                    value,
                    self.get_command_data(
                        h_sens_v[obj_name], f"{value} {value}"
                    ).split()[1],
                )
            )

        self.set_command_data(commands[obj_name], bind=str(value))

    def on_gyro_ch(self):
        commands = {
            "chAutoCalibrate": "AUTO_CALIBRATE",
            "chAccel": "accel",
            "chVSens": "v_sens",
            "chMinVSens": "min_v_sens",
            "chMaxVSens": "max_v_sens",
        }
        v_sens_counterpart = {
            "chVSens": self.leVSens.setEnabled,
            "chMinVSens": self.leMinVSens.setEnabled,
            "chMaxVSens": self.leMaxVSens.setEnabled,
        }
        sender = self.sender()
        value = ("", "True")[int(sender.isChecked())]
        if sender.objectName() == "chAutoCalibrate":
            value = ("OFF", "ON")[int(sender.isChecked())]
        elif sender.objectName() != "chAccel":
            v_sens_counterpart[sender.objectName()](sender.isChecked())
        else:
            self.on_accel_change(sender.isChecked())

        self.set_command_data(commands[sender.objectName()], bind=value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
