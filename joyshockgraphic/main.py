import sys

from joyshockgraphic.database.dmanager import DManager
from joyshockgraphic.ui.main_window import Ui_MainWindow
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QInputDialog, QWidget,
)


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialise data
        self.db = DManager()
        self.curr_prof = None  # Currently edited profile
        self.curr_cmd = None  # Currently edited command
        self.extra_cmds = dict()  # Extra commands
        # Dictionary for matching button names and commands
        self.exceptions = {"Minus": "-", "Plus": "+", "-": "Minus", "+": "Plus"}

        # Load existing profiles
        self.reload_profiles()
        # Check profile selection
        self.lwProfiles.itemSelectionChanged.connect(self.check_selection)
        # Handle profiles tab's buttons
        self.bgLibrary.buttonClicked.connect(self.configure_profiles)

        # self.inputWidgets.findChild(QPushButton, "pbS").text()

        self.bgConfig.buttonClicked.connect(self.rename)
        self.bgLoadInput.buttonClicked.connect(self.load_input)
        self.bgPickBind.buttonClicked.connect(self.pick_bind)
        self.bgSwitchInput.buttonClicked.connect(self.switch_input)

        # Connect rest of the controls
        self.pbChord.clicked.connect(self.on_chord_pick)
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

    # This function loads/reloads all existing profiles from the database
    def reload_profiles(self) -> None:
        self.lwProfiles.clear()
        for profile in self.db.select("display_name", "profiles"):
            self.lwProfiles.addItem(profile[0])
        # Call profile selection change due to selection clearing
        self.check_selection()

    # This function enables/disables profile configuration options
    # based on selection
    def check_selection(self) -> None:
        current_item = self.lwProfiles.currentItem()
        profiles = [x[0] for x in self.db.select("display_name", "profiles")]
        is_profile = bool(current_item and current_item.text() in profiles)
        if is_profile:
            # Call configurator initialisation
            self.configure()
        else:
            # Disable configurator tab
            self.mainTabs.setTabEnabled(1, False)
        self.pbEdit.setEnabled(is_profile)
        self.pbDelete.setEnabled(is_profile)

    # This function handles profiles tab's buttons
    def configure_profiles(self, sender: QPushButton) -> None:
        cases = {"pbCreate": self.create_profile, "pbEdit": self.edit_profile, "pbDelete": self.delete}
        cases[sender.objectName()]()

    # This function corrects command's name if it's an exception
    def correct_command_name(self, name: str) -> str:
        if name in self.exceptions:
            return self.exceptions[name]
        return name

    # This function renames command that is being edited
    def rename(self):
        name, ok = QInputDialog.getText(self, "Rename command", "New command name:")
        if ok:
            command = self.correct_command_name(self.curr_cmd)
            for button in self.bgPickBind.buttons():
                if button.objectName() == "pb" + command:
                    self.set_command_data(self.curr_cmd, name=name)
                    button.setText(name)

    # Init UI
    def load_input(self, sender: QPushButton):
        # Set current command for editing
        exceptions = {"pbMinus": "-", "pbPlus": "+"}
        obj_name = sender.objectName()
        self.curr_cmd = (
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
        # Load command database
        events = {
            "0": 0,
            "\\": 1,
            "/": 2,
            "'": 3,
            "_": 4,
            "+": 5,
        }
        self.cbEvent.setCurrentIndex(
            events[self.get_command_data(self.curr_cmd, "0", "event")]
        )
        actions = {
            "0": 0,
            "^": 1,
            "!": 2,
        }
        self.cbAction.setCurrentIndex(
            actions[self.get_command_data(self.curr_cmd, "0", "action")]
        )
        self.pbChord.setText(
            self.get_command_data(self.curr_cmd, "None", "chord")
        )

    # Input UI
    def pick_bind(self, sender: QPushButton):
        dlg = uic.loadUi("joyshockgraphic/resources/ui/bind_pick.ui")
        exceptions = {"pbMinus": "-", "pbPlus": "+"}
        obj_name = sender.objectName()
        e_command_before = self.curr_cmd
        self.curr_cmd = (
            obj_name[2:]
            if obj_name not in exceptions
            else exceptions[obj_name]
        )
        dlg.bgKeyboard.buttonClicked.connect(self.on_keyboard_bg)
        dlg.pbAdvanced.clicked.connect(self.on_advanced_bind)
        dlg.exec_()
        self.curr_cmd = e_command_before

    # Button group
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

    # Pick bind button group
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

        self.set_command_data(self.curr_cmd, bind=bind)
        commands = {"-": "pbMinus", "+": "pbPlus"}
        command = (
            "pb" + self.curr_cmd
            if self.curr_cmd not in commands
            else commands[self.curr_cmd]
        )
        for button in self.bgPickBind.buttons():
            if button.objectName() == command:
                result = self.db.select(
                    "name", self.curr_prof, f'command = "{bind}"'
                )
                name = (
                    result[0][0] if len(result) > 0 and result[0][0] else bind
                )
                button.setText(name)

    # Pick bind input UI
    def on_advanced_bind(self):
        bind, ok = QInputDialog.getText(
            self, "Advanced binding", "Custom binding:"
        )
        if ok:
            exclusions = {"-": "Minus", "+": "Plus"}
            command = (
                self.curr_cmd
                if self.curr_cmd not in exclusions
                else exclusions[self.curr_cmd]
            )
            for button in self.bgPickBind.buttons():
                if button.objectName() == "pb" + command:
                    self.set_command_data(self.curr_cmd, bind=bind)
                    button.setText(
                        self.get_command_data(self.curr_cmd, bind, "name")
                    )

    # UI logic
    def create_profile(self):
        # Open profile creation dialog
        dlg = uic.loadUi("joyshockgraphic/resources/ui/profile.ui")
        ok = dlg.exec_()
        if ok:
            # Create profile
            self.db.create_profile(
                dlg.leDisplayName.text(),
                dlg.leFileName.text(),
            )
            self.reload_profiles()

    # UI logic
    def edit_profile(self):
        # Open profile creation dialog
        dlg = uic.loadUi("joyshockgraphic/resources/ui/profile.ui")
        ok = dlg.exec_()
        if ok:
            display_name = self.lwProfiles.currentItem().text()
            self.db.edit_profile(
                (
                    display_name,
                    self.db.select(
                        "file_name",
                        "profiles",
                        f'display_name = "{display_name}"',
                    )[0][0],
                ),
                (dlg.leDisplayName.text(), dlg.leFileName.text()),
            )
            self.reload_profiles()

    # Init UI
    def configure(self):
        # Enable configurator and set current profile
        self.mainTabs.setTabEnabled(1, True)
        display_name = self.lwProfiles.currentItem().text()
        file_name = self.db.select("file_name", "profiles", f'display_name = "{display_name}"')[0][0]
        self.curr_prof = file_name
        self.curr_cmd = None
        self.init_configurator()

    # UI logic
    def delete(self):
        # Deletes selected profile
        self.db.delete_profile(self.lwProfiles.currentItem().text())
        self.reload_profiles()

    def closeEvent(self, event):
        self.db.close()

    # Data
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

    # Data
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
        self.db.export_profile(self.curr_prof)

    # Init UI (heavy)
    def init_configurator(self):
        # Init buttons
        special = {"pbMinus": "-", "pbPlus": "+"}
        for button in self.bgPickBind.buttons():
            # Cut off "pb" prefix from the button name
            command = (
                button.objectName()[2:]
                if button.objectName() not in special
                else special[button.objectName()]
            )
            name = self.get_command_data(command, "None")
            result = self.db.select(
                "name", self.curr_prof, f'command = "{command}"'
            )
            name = result[0][0] if len(result) > 0 and result[0][0] else name
            # Change button's text according to it's bind in profile
            button.setText(str(name))

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

    # Input UI
    def on_chord_pick(self, sender: QPushButton):
        pass

    # Init UI
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

    # Input UI
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

    # Input UI
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
        # If vertical sens, and it's written in percent format,
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

    # Input UI
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

    # This function adds a widget for an extra command
    def add_cmd(self, object_name: str, cmd_id: str) -> QWidget:
        # TODO: Think further about how to create extra commands
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
