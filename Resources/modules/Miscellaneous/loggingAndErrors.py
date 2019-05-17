from PyQt5 import QtWidgets
def showErrorMessage(parent, msg):
        """
        """
        print(msg)
        
        errorMsg = QtWidgets.QMessageBox.warning(parent, "Error", msg)

def displayDialogYesNo(message):
        """
        """
        box = QtWidgets.QMessageBox()
        box.setText(message)
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
        ret = box.exec_()

        if ret == QtWidgets.QMessageBox.Yes:
                yesNo = True
        else:
                yesNo = False

        return yesNo