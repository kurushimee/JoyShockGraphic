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
        ok = dlg.exec_()
        if ok:
            pass

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

    def gbind(self, command: str, default: str):
        # Get existing bind or default value
        bind = self.dman.select(
            "bind", self.e_profile, f'command = "{command}"'
        )
        return bind[0][0] if len(bind) > 0 else default

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
            button.setText(self.gbind(name, "None"))

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
            modes[self.gbind("RIGHT_STICK_MODE", "AIM")]
        )
        self.cbLmode.setCurrentIndex(
            modes[self.gbind("LEFT_STICK_MODE", "NO_MOUSE")]
        )

        # Init gyro
        self.leRWC.setText(self.gbind("REAL_WORLD_CALIBRATION", "45"))
        self.leSens.setText(self.gbind("IN_GAME_SENS", "1"))
        auto_calibrate = {"ON": True, "OFF": False}
        self.chAutoCalibrate.setChecked(
            auto_calibrate[self.gbind("AUTO_CALIBRATE", "OFF")]
        )
        self.chAccel.setChecked(bool(self.gbind("accel", "True")))
        self.accel(self.chAccel.isChecked())

        self.leGyroSens.setText(self.gbind("GYRO_SENS", "3 3").split()[0])
        self.chVSens.setChecked(bool(self.gbind("v_sens", "")))
        self.leVSens.setText(self.gbind("GYRO_SENS", "3 3").split()[1])

        self.leMinGyroSens.setText(
            self.gbind("MIN_GYRO_SENS", "2 2").split()[0]
        )
        self.chMinVSens.setChecked(bool(self.gbind("min_v_sens", "")))
        self.chMaxVSens.setChecked(bool(self.gbind("max_v_sens", "")))
        self.leMaxGyroSens.setText(
            self.gbind("MAX_GYRO_SENS", "4 4").split()[1]
        )
        self.leMinThreshold.setText(self.gbind("MIN_GYRO_THRESHOLD", "0"))
        self.leMaxThreshold.setText(self.gbind("MAX_GYRO_THRESHOLD", "75"))

    def accel(self, accel: bool):
        self.lGyroSens.setEnabled(not accel)
        self.leGyroSens.setEnabled(not accel)
        self.chVSens.setEnabled(not accel)
        self.leVSens.setEnabled(self.chVSens.isChecked() and not accel)

        self.lMinSens.setEnabled(accel)
        self.lMaxSens.setEnabled(accel)
        self.leMinGyroSens.setEnabled(accel)
        self.leMaxGyroSens.setEnabled(accel)
        self.lMinThreshold.setEnabled(accel)
        self.lMaxThreshold.setEnabled(accel)
        self.leMinThreshold.setEnabled(accel)
        self.leMaxThreshold.setEnabled(accel)
        self.chMinVSens.setEnabled(accel)
        self.chMaxVSens.setEnabled(accel)
        self.leMinVSens.setEnabled(self.chMinVSens.isChecked() and accel)
        self.leMaxVSens.setEnabled(self.chMaxVSens.isChecked() and accel)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
