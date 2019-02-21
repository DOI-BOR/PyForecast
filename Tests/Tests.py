# Script Name:      Tests.py
# Script Author:    Jon Rocha
#
# Description:      Tests contains Unit Tests for core PyForecast features,
#                   processes, and functionality.

# Import libraries and the application
import sys
import time
import unittest
from PyQt5 import QtGui, QtWidgets, QtCore
import Resources.application as application
from datetime import datetime
from Resources.Functions.miscFunctions import readConfig,writeConfig

app = QtWidgets.QApplication(sys.argv)

class pyforecastTest(unittest.TestCase):

    def setUp(self):
        self.form = application.mainWindow(datetime.strftime(datetime.now(), '%Y-%m-%d'))

    def test_setDate(self):
        writeConfig('programtime',"2000-01-01")
        self.assertEqual(readConfig('programtime'),"2000-01-01")


if __name__ == "__main__":
    unittest.main()

