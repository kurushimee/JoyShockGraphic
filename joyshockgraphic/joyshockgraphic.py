import sys
from client import Client
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi("joyshockgraphic/resources/joyshockgraphic.ui", self)

        # Initialize JSM client
        self.client = Client()
        self.client.init()

        # Connect button groups
        self.bgLibrary.buttonClicked.connect(self.handle_profile)
        self.bgLoadInput.buttonClicked.connect(self.load_input)
        self.bgPickBind.buttonClicked.connect(self.pick_bind)
        self.bgSwitchInput.buttonClicked.connect(self.switch_input)

    def handle_profile(self):
        self.client.send_command('{"N = GYRO_OFF", "E = LCONTROL"}')

    def load_input(self):
        pass

    def pick_bind(self):
        pass

    def switch_input(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
