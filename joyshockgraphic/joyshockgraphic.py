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

        # Connect button groups
        self.bgLibrary.buttonClicked.connect(self.handle_profile)
        self.bgLoadInput.buttonClicked.connect(self.load_input)
        self.bgPickBind.buttonClicked.connect(self.pick_bind)
        self.bgSwitchInput.buttonClicked.connect(self.switch_input)

    def handle_profile(self, sender: QPushButton):
        match sender.objectName():
            case "pbCreate":
                # Create a new profile with a dialog
                dlg = uic.loadUi("joyshockgraphic/resources/new_profile.ui")
                ok = dlg.exec_()
                if ok:
                    self.dman.create_profile(
                        dlg.leDisplayName.text(),
                        dlg.leFileName.text(),
                    )
                    # Append the profile to the QListWidget
                    QListWidgetItem(dlg.leDisplayName.text(), self.lwProfiles)

    def load_input(self, sender: QPushButton):
        pass

    def pick_bind(self, sender: QPushButton):
        pass

    def switch_input(self, sender: QPushButton):
        pass

    def closeEvent(self, event):
        self.dman.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
