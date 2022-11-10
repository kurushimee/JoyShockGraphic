import sys
from dmanager import DManager
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
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
        pass

    def load_input(self, sender: QPushButton):
        pass

    def pick_bind(self, sender: QPushButton):
        dlg = uic.loadUi("joyshockgraphic/resources/picker.ui")
        exceptions = {"pbMinus": "-", "pbPlus": "+"}
        obj_name = sender.objectName()
        self.e_command = (
            obj_name[2:]
            if obj_name not in exceptions
            else exceptions[obj_name]
        )
        dlg.bgKeyboard.buttonClicked.connect(self.on_keyboard_bg)
        dlg.exec_()

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

        self.set_bind(self.e_command, bind=bind)
        commands = {"-": "pbMinus", "+": "pbPlus"}
        command = (
            "pb" + self.e_command
            if self.e_command not in commands
            else commands[self.e_command]
        )
        for button in self.bgPickBind.buttons():
            if button.objectName() == command:
                button.setText(bind)

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
        self.e_bind = None
        self.init_configurator()

    def delete(self):
        # Deletes selected profile
        self.dman.delete_profile(self.lwProfiles.currentItem().text())
        self.populate_list()

    def closeEvent(self, event):
        self.dman.close()

    def get_bind(self, command: str, default: str):
        # Get existing bind or default value
        bind = self.dman.select(
            "bind", self.e_profile, f'command = "{command}"'
        )
        return bind[0][0] if len(bind) > 0 else default

    def set_bind(
        self, command: str, chord=None, action=None, bind=None, event=None
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
            ):
                self.dman.update(
                    self.e_profile, field, value, f'command = "{command}"'
                )
        else:
            self.dman.insert(
                self.e_profile, (command, chord, action, bind, event)
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
            # Change button's text according to it's bind in profile
            button.setText(self.get_bind(name, "None"))

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
            modes[self.get_bind("RIGHT_STICK_MODE", "AIM")]
        )
        self.cbLmode.setCurrentIndex(
            modes[self.get_bind("LEFT_STICK_MODE", "NO_MOUSE")]
        )

        # Init gyro
        self.leRWC.setText(str(self.get_bind("REAL_WORLD_CALIBRATION", "45")))
        self.leSens.setText(str(self.get_bind("IN_GAME_SENS", "1")))
        auto_calibrate = {"ON": True, "OFF": False}
        self.chAutoCalibrate.setChecked(
            auto_calibrate[self.get_bind("AUTO_CALIBRATE", "OFF")]
        )
        self.chAccel.setChecked(bool(self.get_bind("accel", "True")))
        self.on_accel_change(self.chAccel.isChecked())

        self.leGyroSens.setText(
            str(self.get_bind("GYRO_SENS", "3 3").split()[0])
        )
        self.chVSens.setChecked(bool(self.get_bind("v_sens", "")))
        self.leVSens.setText(str(self.get_bind("GYRO_SENS", "3 3").split()[1]))

        self.leMinGyroSens.setText(
            str(self.get_bind("MIN_GYRO_SENS", "2 2").split()[0])
        )
        self.chMinVSens.setChecked(bool(self.get_bind("min_v_sens", "")))
        self.chMaxVSens.setChecked(bool(self.get_bind("max_v_sens", "")))
        self.leMaxGyroSens.setText(
            str(self.get_bind("MAX_GYRO_SENS", "4 4").split()[1])
        )
        self.leMinThreshold.setText(
            str(self.get_bind("MIN_GYRO_THRESHOLD", "0"))
        )
        self.leMaxThreshold.setText(
            str(self.get_bind("MAX_GYRO_THRESHOLD", "75"))
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
        self.set_bind(mode, bind=modes[value])

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
            h_sens = self.get_bind(
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
                    self.get_bind(
                        h_sens_v[obj_name], f"{value} {value}"
                    ).split()[1],
                )
            )

        self.set_bind(commands[obj_name], bind=str(value))

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

        self.set_bind(commands[sender.objectName()], bind=value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
