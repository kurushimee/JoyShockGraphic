from PyQt5.QtWidgets import QLabel

from joyshockgraphic.database import cmds as db_cmds


# This function loads/reloads all existing profiles from the database
def reload_profiles(self) -> None:
    self.lwProfiles.clear()
    for profile in self.db.select("display_name", "profiles"):
        self.lwProfiles.addItem(profile[0])
    # Call profile selection change due to selection clearing
    self.check_selection()


# This function loads all the values from the config into the configurator
def init_cmds(self):
    # Init buttons
    special = {"pbMinus": "-", "pbPlus": "+"}
    for button in self.bgPickBind.buttons():
        # Cut off "pb" prefix from the button name
        command = (
            button.objectName()[2:]
            if button.objectName() not in special
            else special[button.objectName()]
        )
        # Change button's text according to it's bind in profile
        bind = db_cmds.get_command_data(self, command, "None")
        button.setText(str(bind))

        pb_name = button.objectName()[2:]
        if pb_name != "Chord":
            # Change command's label according to it's name in profile
            name = db_cmds.get_command_data(self, pb_name, "", "name")
            self.inputWidgets.findChild(QLabel, "l" + pb_name).setText(name)

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
        modes[db_cmds.get_command_data(self, "RIGHT_STICK_MODE", "AIM")]
    )
    self.cbLmode.setCurrentIndex(
        modes[db_cmds.get_command_data(self, "LEFT_STICK_MODE", "NO_MOUSE")]
    )

    # Init gyro
    self.leRWC.setText(
        str(db_cmds.get_command_data(self, "REAL_WORLD_CALIBRATION", "45"))
    )
    self.leSens.setText(str(db_cmds.get_command_data(self, "IN_GAME_SENS", "1")))
    auto_calibrate = {"ON": True, "OFF": False}
    self.chAutoCalibrate.setChecked(
        auto_calibrate[db_cmds.get_command_data(self, "AUTO_CALIBRATE", "OFF")]
    )
    self.chAccel.setChecked(bool(db_cmds.get_command_data(self, "accel", "True")))
    self.show_accel(self.chAccel.isChecked())

    self.leGyroSens.setText(
        str(db_cmds.get_command_data(self, "GYRO_SENS", "3 3").split()[0])
    )
    self.chVSens.setChecked(bool(db_cmds.get_command_data(self, "v_sens", "")))
    self.leVSens.setText(
        str(db_cmds.get_command_data(self, "GYRO_SENS", "3 3").split()[1])
    )

    self.leMinGyroSens.setText(
        str(db_cmds.get_command_data(self, "MIN_GYRO_SENS", "2 2").split()[0])
    )
    self.chMinVSens.setChecked(
        bool(db_cmds.get_command_data(self, "min_v_sens", ""))
    )
    self.chMaxVSens.setChecked(
        bool(db_cmds.get_command_data(self, "max_v_sens", ""))
    )
    self.leMaxGyroSens.setText(
        str(db_cmds.get_command_data(self, "MAX_GYRO_SENS", "4 4").split()[1])
    )
    self.leMinThreshold.setText(
        str(db_cmds.get_command_data(self, "MIN_GYRO_THRESHOLD", "0"))
    )
    self.leMaxThreshold.setText(
        str(db_cmds.get_command_data(self, "MAX_GYRO_THRESHOLD", "75"))
    )
