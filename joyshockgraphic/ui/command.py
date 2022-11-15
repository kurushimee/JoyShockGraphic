from PyQt5.QtCore import QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QFrame


class CmdWidget(QWidget):
    lIcon: QLabel
    lName: QLabel
    pbBind: QPushButton
    pbSettings: QPushButton
    pbRemove: QPushButton

    def __init__(self, object_name: str, cmd_id: int, icon: QPixmap, parent=None):
        super(CmdWidget, self).__init__(parent)

        self.lIcon = QLabel()
        self.lIcon.setPixmap(icon)
        self.lIcon.setScaledContents(True)
        self.lIcon.setMinimumSize(40, 40)
        self.lIcon.setMaximumSize(40, 40)
        self.lName = QLabel("", f"l{object_name}_{cmd_id}")
        self.lName.setFont(QFont("Segoe UI", 16))
        self.pbBind = QPushButton("None", f"pb{object_name}_{cmd_id}")
        self.pbBind.setFont(QFont("Segoe UI", 16))
        self.pbSettings = QPushButton("", f"pb{object_name}Settings_{cmd_id}")
        self.pbSettings.setIcon(QIcon(QPixmap(".\\joyshockgraphic\\resources\\ui\\../icons/cogwheel.png")))
        self.pbSettings.setIconSize(QSize(24, 24))
        self.pbRemove = QPushButton("", f"pb{object_name}Remove_{cmd_id}")
        self.pbRemove.setIcon(QIcon(QPixmap(".\\joyshockgraphic\\resources\\ui\\../icons/minus.png")))
        self.pbRemove.setIconSize(QSize(24, 24))
        self.line = QLabel()
        self.line.setFrameStyle(QFrame.HLine)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.lIcon)
        hlayout.addStretch()
        hlayout.addWidget(self.lName)
        hlayout.addWidget(self.pbBind)
        hlayout.addWidget(self.pbSettings)
        hlayout.addWidget(self.pbRemove)

        vlayout = QVBoxLayout()
        vlayout.addLayout(hlayout)
        vlayout.addWidget(self.line)
        self.setLayout(vlayout)
