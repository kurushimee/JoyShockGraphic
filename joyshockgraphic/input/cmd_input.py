import joyshockgraphic.database.cmds as db_cmds


# This function updates joystick settings
def change_stick(self, value):
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
    db_cmds.set_command_data(self, mode, bind=modes[value])


# This function updates gyro settings based on QLineEdit values
def change_gyro_lineedit(self):
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
        h_sens = db_cmds.get_command_data(
            self,
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
                db_cmds.get_command_data(
                    self,
                    h_sens_v[obj_name], f"{value} {value}"
                ).split()[1],
            )
        )

    db_cmds.set_command_data(self, commands[obj_name], bind=str(value))


# This function updates gyro settings based on QCheckBox values
def change_gyro_checkbox(self):
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
        self.show_accel(sender.isChecked())

    db_cmds.set_command_data(self, commands[sender.objectName()], bind=value)
