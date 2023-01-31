from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor
import requests
import time
import subprocess

app = QApplication.instance()

class UpdaterDialog(QDialog):

  def __init__(self):

    QDialog.__init__(self)
    self.setUI()
    self.update_button.setEnabled(False)
    self.update_button.pressed.connect(self.update_software)
    self.progress_text.append('Looking for updates...')
    releases = requests.get('https://api.github.com/repos/usbr/PyForecast/releases', verify=False).json()
    self.newest_release = None
    for release in releases:
      if release['tag_name'].startswith('5.'):
        self.newest_release = release
    
    if self.newest_release:
      self.new_version = self.newest_release['tag_name'].strip()
      if self.new_version != app.PYCAST_VERSION:
        self.progress_text.append(f'\nThere is a new version available.')
        self.progress_text.append(f'\nYou have version: {app.PYCAST_VERSION}')
        self.progress_text.append(f'\nThe most recent version is: {self.new_version}')
        self.progress_text.append(f'\n\nPLEASE SAVE YOUR WORK BEFORE UPDATING!!\n\n')
        self.progress_text.append(f'\nPress the update button to download the latest version.')
        self.update_button.setEnabled(True)
      else:
        self.progress_text.append(f'\nYou have the most recent version ({app.PYCAST_VERSION})')
        self.update_button.setEnabled(False)
    else:
      self.progress_text.append(f'\nCould not find a release for major version {app.PYCAST_VERSION.split(".")[0]}')
      self.update_button.setEnabled(False)

  def update_software(self):
    self.update_button.setEnabled(False)
    self.progress_text.append('Checking for patch file')
    self.patch_file = False
    app.processEvents()
    
    for asset in self.newest_release['assets']:
      if asset['name'] == f'patch_{app.PYCAST_VERSION}_to_{self.new_version}.zip':
        self.patch_file = True
        self.file_name = asset['browser_download_url']
        self.total_download_size = asset['size']
    if not self.patch_file:
      self.file_name = self.newest_release['assets'][0]['browser_download_url']
      self.total_download_size = self.newest_release['assets'][0]['size']
    app.processEvents()

    self.progress_text.append('Downloading Update')
    app.processEvents()
    with open(app.base_dir+'/update_file.exe', 'wb') as f:
      response = requests.get(self.file_name, stream=True, verify=False)
      dl = 0
      for data in response.iter_content(chunk_size=4096):
        dl += len(data)
        f.write(data)
        done = int(50 * dl/self.total_download_size)
        self.progress_text.setFocus()
        cursor = self.progress_text.textCursor()
        self.progress_text.moveCursor(QTextCursor.End, QTextCursor.MoveAnchor)
        self.progress_text.moveCursor(QTextCursor.StartOfLine, QTextCursor.MoveAnchor)
        self.progress_text.moveCursor(QTextCursor.End, QTextCursor.KeepAnchor)
        self.progress_text.textCursor().removeSelectedText()
        self.progress_text.textCursor().deletePreviousChar()
        self.progress_text.setTextCursor(cursor)
        self.progress_text.append(f'[{"="*done}{" "*(50-done)}] {2*done}%')
        app.processEvents()
  
    self.progress_text.append('Download Completed. Updating now.')
    time.sleep(1)
    subprocess.Popen([f"{app.base_dir+'/update_file.exe'}"], start_new_session=True)
    app.quit()    

  def setUI(self):
    self.setWindowTitle('Update Check')
    self.setMinimumWidth(700)
    self.setMinimumHeight(500)
    layout = QVBoxLayout()
    self.update_button = QPushButton('Update')
    self.progress_text = QTextEdit(objectName='monospace')

    layout.addWidget(self.progress_text)
    hlayout = QHBoxLayout()
    hlayout.addStretch(1)
    hlayout.addWidget(self.update_button)
    layout.addLayout(hlayout)

    self.setLayout(layout)
