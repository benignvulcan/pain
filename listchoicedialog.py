
from PyQt5 import QtCore, QtWidgets

class ListChoiceDialog(QtWidgets.QDialog):

  def __init__(self, parent=None, flags=QtCore.Qt.WindowFlags()):
    super().__init__(parent, flags)
    self._label = QtWidgets.QLabel('')
    self._list = QtWidgets.QListWidget()
    self._btns = QtWidgets.QDialogButtonBox( QtWidgets.QDialogButtonBox.Ok
                                           | QtWidgets.QDialogButtonBox.Cancel )
    self._choiceIndex = None
    y = QtWidgets.QVBoxLayout(self)
    y.addWidget(self._label)
    y.addWidget(self._list)
    y.addWidget(self._btns)
    self._list.currentRowChanged.connect(self.setChoiceIndex)
    self._btns.accepted.connect(self.accept)
    self._btns.rejected.connect(self.reject)

  def setLabelText(self, text):
    return self._label.setText(text)

  def setListStrings(self, strings):
    self._list.addItems(strings)
    self._list.setCurrentRow(0)

  def setChoiceIndex(self, value):
    print('ListChoiceDialog.setChoiceIndex({})'.format(value))
    self._choiceIndex = value

  def choiceIndex(self):
    return self._choiceIndex

  @staticmethod
  def getChoice(parent, title, label, choices):
    dlg = ListChoiceDialog(parent)
    dlg.setWindowTitle(title)
    dlg.setLabelText(label)
    dlg.setListStrings(choices)
    if dlg.exec_() == QtWidgets.QDialog.Accepted:
      print('ListChoiceDialog.getChoice: dlg.choiceIndex == {}'.format(dlg.choiceIndex()))
      return dlg.choiceIndex()
    return None
