import sys
from dmanager import DManager
from PyQt5 import uic
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QListWidgetItem,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("joyshockgraphic/resources/joyshockgraphic.ui", self)

        # Initialise database manager
        self.dman = DManager()
        # Populate lwProfiles with already existing profiles
        self.populate_list()

        # Connect button groups
        self.bgLibrary.buttonClicked.connect(self.handle_profile)
        self.bgLoadInput.buttonClicked.connect(self.load_input)
        self.bgPickBind.buttonClicked.connect(self.pick_bind)
        self.bgSwitchInput.buttonClicked.connect(self.switch_input)

    def populate_list(self):
        for profile in self.dman.select("display_name", "profiles"):
            display_name = profile[0]
            QListWidgetItem(display_name, self.lwProfiles)

    def handle_profile(self, sender: QPushButton):
        cond = sender.objectName()
        if cond == "pbCreate":
            self.create()
        elif cond == "pbEdit":
            self.edit()
        elif cond == "pbConfigure":
            self.configure()
        elif cond == "pbDelete":
            self.delete()

    def load_input(self, sender: QPushButton):
        pass

    def pick_bind(self, sender: QPushButton):
        dlg = uic.loadUi("joyshockgraphic/resources/picker.ui")
        ok = dlg.exec_()
        if ok:
            pass

    def switch_input(self, sender: QPushButton):
        pass

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
            # Append profile to lwProfiles
            QListWidgetItem(dlg.leDisplayName.text(), self.lwProfiles)

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
                    ),
                ),
                (dlg.leDisplayName.text(), dlg.leFileName.text()),
            )

    def configure(self):
        pass

    def delete(self):
        pass

    def closeEvent(self, event):
        self.dman.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
