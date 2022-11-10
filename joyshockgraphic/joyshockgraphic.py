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
        self.bgLoadInput.buttonClicked.connect(self.load_input)
        self.bgPickBind.buttonClicked.connect(self.pick_bind)
        self.bgSwitchInput.buttonClicked.connect(self.switch_input)

    def populate_list(self):
        self.lwProfiles.clear()
        for profile in self.dman.select("display_name", "profiles"):
            display_name = profile[0]
            self.lwProfiles.addItem(display_name)

    def selection_changed(self):
        if self.lwProfiles.currentItem().text() in [
            x[0] for x in self.dman.select("display_name", "profiles")
        ]:
            condition = True
        else:
            condition = False
        self.pbEdit.setEnabled(condition)
        self.pbDelete.setEnabled(condition)
        self.pbConfigure.setEnabled(condition)

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
                    ),
                ),
                (dlg.leDisplayName.text(), dlg.leFileName.text()),
            )
            self.populate_list()

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
