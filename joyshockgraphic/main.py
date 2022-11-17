import sys
from functools import partial

from joyshockgraphic.database.controls import DbControls
from joyshockgraphic.ui.main_window import Ui_MainWindow
from joyshockgraphic.input import cmd_input
from joyshockgraphic.input import picker_input
from joyshockgraphic.database import profiles
from joyshockgraphic.database import cmds as db_cmds
from joyshockgraphic import init_interface
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QInputDialog, QLabel,
)


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Initialise data
        self.db = DbControls()
        self.curr_prof = None  # Currently edited profile
        self.curr_cmd = None  # Currently edited command
        # Dictionary for matching button names and commands
        self.exceptions = {"Minus": "-", "Plus": "+", "-": "Minus", "+": "Plus"}

        # Load existing profiles
        init_interface.reload_profiles(self)
        # Check profile selection
        self.lwProfiles.itemSelectionChanged.connect(self.check_selection)
        # Handle profiles tab's buttons
        self.bgLibrary.buttonClicked.connect(self.configure_profiles)

        self.bgConfig.buttonClicked.connect(self.rename_cmd)
        self.bgLoadInput.buttonClicked.connect(self.load_input)
        self.bgPickBind.buttonClicked.connect(self.pick_bind)
        self.bgSwitchInput.buttonClicked.connect(self.switch_input)

        # Connect rest of the controls
        # self.pbChord.clicked.connect(self.on_chord_pick)
        # Joysticks
        change_stick = partial(cmd_input.change_stick, self)
        self.cbRmode.currentIndexChanged.connect(change_stick)
        self.cbLmode.currentIndexChanged.connect(change_stick)
        # Gyro line edits
        gyro_lineedit = partial(cmd_input.change_gyro_lineedit, self)
        self.leRWC.returnPressed.connect(gyro_lineedit)
        self.leSens.returnPressed.connect(gyro_lineedit)
        self.leGyroSens.returnPressed.connect(gyro_lineedit)
        self.leVSens.returnPressed.connect(gyro_lineedit)
        self.leMinGyroSens.returnPressed.connect(gyro_lineedit)
        self.leMinVSens.returnPressed.connect(gyro_lineedit)
        self.leMinThreshold.returnPressed.connect(gyro_lineedit)
        self.leMaxGyroSens.returnPressed.connect(gyro_lineedit)
        self.leMaxVSens.returnPressed.connect(gyro_lineedit)
        self.leMaxThreshold.returnPressed.connect(gyro_lineedit)
        # Gyro check boxes
        gyro_checkbox = partial(cmd_input.change_gyro_checkbox, self)
        self.chAutoCalibrate.stateChanged.connect(gyro_checkbox)
        self.chAccel.stateChanged.connect(gyro_checkbox)
        self.chVSens.stateChanged.connect(gyro_checkbox)
        self.chMinVSens.stateChanged.connect(gyro_checkbox)
        self.chMaxVSens.stateChanged.connect(gyro_checkbox)

    # This function corrects command's name if it's an exception
    def correct_command_name(self, name: str) -> str:
        if name in self.exceptions:
            return self.exceptions[name]
        return name

    # This function handles profiles tab's buttons
    def configure_profiles(self, sender: QPushButton) -> None:
        cases = {"pbCreate": self.create_profile, "pbEdit": self.edit_profile, "pbDelete": self.delete_profile}
        cases[sender.objectName()]()

    # This function enables configurator and loads profile into it
    def load_configurator(self):
        # Enable configurator tab
        self.mainTabs.setTabEnabled(1, True)
        # Set current profile
        display_name = self.lwProfiles.currentItem().text()
        file_name = self.db.select("file_name", "profiles", f'display_name = "{display_name}"')[0][0]
        self.curr_prof = file_name
        self.curr_cmd = None

        init_interface.init_cmds(self)

    # This function summons a dialog for creating a profile
    def create_profile(self):
        # Open profile creation dialog
        dlg = uic.loadUi("joyshockgraphic/resources/ui/profile.ui")
        ok = dlg.exec_()
        if ok:
            # Create profile
            profiles.create(
                self.db,
                dlg.leDisplayName.text(),
                dlg.leFileName.text(),
            )
            init_interface.reload_profiles(self)

    # This function summons a dialog for editing a profile
    def edit_profile(self):
        # Open profile creation dialog
        dlg = uic.loadUi("joyshockgraphic/resources/ui/profile.ui")
        ok = dlg.exec_()
        if ok:
            display_name = self.lwProfiles.currentItem().text()
            profiles.edit(
                self.db,
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
            init_interface.reload_profiles(self)

    # This function deletes profile
    def delete_profile(self):
        profiles.delete(self.db, self.lwProfiles.currentItem().text())
        init_interface.reload_profiles(self)

    # This function enables/disables profile configuration options
    # based on selection
    def check_selection(self) -> None:
        current_item = self.lwProfiles.currentItem()
        profile_names = [x[0] for x in self.db.select("display_name", "profiles")]
        is_profile = bool(current_item and current_item.text() in profile_names)
        if is_profile:
            # Call configurator initialisation
            self.load_configurator()
        else:
            # Disable configurator tab
            self.mainTabs.setTabEnabled(1, False)
        self.pbEdit.setEnabled(is_profile)
        self.pbDelete.setEnabled(is_profile)

    # This function selects command for editing in the menu on the right
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
            events[db_cmds.get_command_data(self, self.curr_cmd, "0", "event")]
        )
        actions = {
            "0": 0,
            "^": 1,
            "!": 2,
        }
        self.cbAction.setCurrentIndex(
            actions[db_cmds.get_command_data(self, self.curr_cmd, "0", "action")]
        )
        self.pbChord.setText(
            db_cmds.get_command_data(self, self.curr_cmd, "None", "chord")
        )

    # This function summons a dialog for picking a command bind
    def pick_bind(self, sender: QPushButton):
        dlg = uic.loadUi("joyshockgraphic/resources/ui/bind_pick.ui")
        obj_name = sender.objectName()
        e_command_before = self.curr_cmd
        self.curr_cmd = self.correct_command_name(obj_name[2:])
        dlg.bgKeyboard.buttonClicked.connect(partial(picker_input.bind_picked, self))
        dlg.pbAdvanced.clicked.connect(lambda: picker_input.advanced_dlg(self))
        dlg.exec_()
        self.curr_cmd = e_command_before

    # This function switches active tab in configurator
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

    # This function renames command that is being edited
    def rename_cmd(self):
        name, ok = QInputDialog.getText(self, "Rename command", "New command name:")
        if ok:
            db_cmds.set_command_data(self, self.curr_cmd, name=name)
            command = self.correct_command_name(self.curr_cmd)
            self.inputWidgets.findChild(QLabel, "l" + command).text()

    # This function shows/hides accel controls
    def show_accel(self, state: bool):
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

    # This function is used to close connection with the db on program exit
    def closeEvent(self, event):
        self.db.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Main()
    ex.show()
    sys.exit(app.exec_())
