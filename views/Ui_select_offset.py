# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/select_offset.ui'
#
# Created: Sat Jun  1 17:18:45 2013
#      by: PyQt4 UI code generator 4.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Select_Offset(object):
    def setupUi(self, Select_Offset):
        Select_Offset.setObjectName(_fromUtf8("Select_Offset"))
        Select_Offset.resize(246, 330)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Select_Offset.sizePolicy().hasHeightForWidth())
        Select_Offset.setSizePolicy(sizePolicy)
        Select_Offset.setModal(False)
        self.verticalLayout = QtGui.QVBoxLayout(Select_Offset)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.widget = QtGui.QWidget(Select_Offset)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(self.widget)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.line_music21_duration = QtGui.QLineEdit(self.widget)
        self.line_music21_duration.setInputMask(_fromUtf8(""))
        self.line_music21_duration.setMaxLength(12)
        self.line_music21_duration.setObjectName(_fromUtf8("line_music21_duration"))
        self.horizontalLayout.addWidget(self.line_music21_duration)
        self.verticalLayout.addWidget(self.widget)
        self.widget_2 = QtGui.QWidget(Select_Offset)
        self.widget_2.setObjectName(_fromUtf8("widget_2"))
        self.gridLayout = QtGui.QGridLayout(self.widget_2)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.btn_0_25 = QtGui.QToolButton(self.widget_2)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/sixteenth.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_0_25.setIcon(icon)
        self.btn_0_25.setIconSize(QtCore.QSize(32, 64))
        self.btn_0_25.setObjectName(_fromUtf8("btn_0_25"))
        self.gridLayout.addWidget(self.btn_0_25, 1, 2, 1, 1)
        self.btn_2 = QtGui.QToolButton(self.widget_2)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/half.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_2.setIcon(icon1)
        self.btn_2.setIconSize(QtCore.QSize(32, 64))
        self.btn_2.setObjectName(_fromUtf8("btn_2"))
        self.gridLayout.addWidget(self.btn_2, 0, 2, 1, 1)
        self.btn_1 = QtGui.QToolButton(self.widget_2)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/quarter.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_1.setIcon(icon2)
        self.btn_1.setIconSize(QtCore.QSize(32, 64))
        self.btn_1.setObjectName(_fromUtf8("btn_1"))
        self.gridLayout.addWidget(self.btn_1, 1, 0, 1, 1)
        self.btn_4 = QtGui.QToolButton(self.widget_2)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/whole.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_4.setIcon(icon3)
        self.btn_4.setIconSize(QtCore.QSize(32, 64))
        self.btn_4.setObjectName(_fromUtf8("btn_4"))
        self.gridLayout.addWidget(self.btn_4, 0, 1, 1, 1)
        self.btn_8 = QtGui.QToolButton(self.widget_2)
        icon4 = QtGui.QIcon()
        icon4.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/breve.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_8.setIcon(icon4)
        self.btn_8.setIconSize(QtCore.QSize(32, 64))
        self.btn_8.setObjectName(_fromUtf8("btn_8"))
        self.gridLayout.addWidget(self.btn_8, 0, 0, 1, 1)
        self.btn_0_5 = QtGui.QToolButton(self.widget_2)
        icon5 = QtGui.QIcon()
        icon5.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/eighth.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_0_5.setIcon(icon5)
        self.btn_0_5.setIconSize(QtCore.QSize(32, 64))
        self.btn_0_5.setObjectName(_fromUtf8("btn_0_5"))
        self.gridLayout.addWidget(self.btn_0_5, 1, 1, 1, 1)
        self.btn_0_125 = QtGui.QToolButton(self.widget_2)
        icon6 = QtGui.QIcon()
        icon6.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/thirty_second.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_0_125.setIcon(icon6)
        self.btn_0_125.setIconSize(QtCore.QSize(32, 64))
        self.btn_0_125.setObjectName(_fromUtf8("btn_0_125"))
        self.gridLayout.addWidget(self.btn_0_125, 2, 0, 1, 1)
        self.btn_0_0625 = QtGui.QToolButton(self.widget_2)
        icon7 = QtGui.QIcon()
        icon7.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/sixty_fourth.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_0_0625.setIcon(icon7)
        self.btn_0_0625.setIconSize(QtCore.QSize(32, 64))
        self.btn_0_0625.setObjectName(_fromUtf8("btn_0_0625"))
        self.gridLayout.addWidget(self.btn_0_0625, 2, 1, 1, 1)
        self.btn_all = QtGui.QToolButton(self.widget_2)
        self.btn_all.setEnabled(False)
        self.btn_all.setObjectName(_fromUtf8("btn_all"))
        self.gridLayout.addWidget(self.btn_all, 2, 2, 1, 1)
        self.verticalLayout.addWidget(self.widget_2)
        self.widget_3 = QtGui.QWidget(Select_Offset)
        self.widget_3.setObjectName(_fromUtf8("widget_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(332, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.btn_submit = QtGui.QPushButton(self.widget_3)
        self.btn_submit.setText(_fromUtf8(""))
        icon8 = QtGui.QIcon()
        icon8.addPixmap(QtGui.QPixmap(_fromUtf8(":/icons/icons/show_checkmark.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_submit.setIcon(icon8)
        self.btn_submit.setIconSize(QtCore.QSize(32, 32))
        self.btn_submit.setObjectName(_fromUtf8("btn_submit"))
        self.horizontalLayout_2.addWidget(self.btn_submit)
        self.verticalLayout.addWidget(self.widget_3)

        self.retranslateUi(Select_Offset)
        QtCore.QMetaObject.connectSlotsByName(Select_Offset)

    def retranslateUi(self, Select_Offset):
        Select_Offset.setWindowTitle(_translate("Select_Offset", "Choose an Offset Duration", None))
        self.label.setText(_translate("Select_Offset", "music21 Duration:", None))
        self.line_music21_duration.setText(_translate("Select_Offset", "0.5", None))
        self.btn_0_125.setText(_translate("Select_Offset", "32nd", None))
        self.btn_all.setText(_translate("Select_Offset", "all", None))

import icons_rc
