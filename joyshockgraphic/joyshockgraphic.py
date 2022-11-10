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
        self.profile = self.lwProfiles.currentItem().text()
        self.init_configurator()

    def delete(self):
        # Deletes selected profile
        self.dman.delete_profile(self.lwProfiles.currentItem().text())
        self.populate_list()

    def closeEvent(self, event):
        self.dman.close()

    def init_configurator(self):
        for button in self.bgPickBind.buttons():
            i = (
                0
                if button.objectName()[-2] != r"^_[1-9]$"
                else int(button.objectName()[-1])
            )
            print(i)
            special = {"pbMinus": "-", "pbPlus": "+"}
            name = button.objectName()[:-2] if i > 0 else button.objectName()
            name = name[2:] if name not in special else special[name]
            button.setText(
                self.dman.select("bind", self.profile, f'command = "{name}"')[
                    i
                ]
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
