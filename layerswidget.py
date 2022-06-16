
from PyQt5 import QtCore, QtWidgets

import listchoicedialog
from confetti import Confetti
from grid import Grid

class LayersWidget(QtWidgets.QListView):

  'A list view onto a LayerModel'

  def __init__(self, parent):
    super().__init__(parent)
    #self.setHeaderHidden(True)
    self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
    self.setDefaultDropAction(QtCore.Qt.MoveAction)

  def sizeHint(self):
    # Typically just a few layers, so shrink the typical vertal size.
    z = super().sizeHint()
    return QtCore.QSize(z.width(), z.height()//3)

  def moveCurrentDown(self):
    newIdx = self.model().moveDown(self.currentIndex())
    if newIdx.isValid():
      self.setCurrentIndex(newIdx)

  def moveCurrentUp(self):
    newIdx = self.model().moveUp(self.currentIndex())
    if newIdx.isValid():
      self.setCurrentIndex(newIdx)

  def startDrag(self, actions):
    self._drag_item = self.currentItem()
    if not isinstance(self._drag_item, BackgroundLayer):
      print('startDrag ', self._drag_item)
      super().startDrag(actions)

  def dropEvent(self, evt):
    print('LayersWidget.dropEvent: evt={}'.format(evt))
    idx = self.indexAt(evt.pos())
    print('LayersWidget.dropEvent: idx.isValid()={}, idx.row={}, idx.parent={}, action={:02X}'.format(idx.isValid(), idx.row(), idx.parent(), evt.dropAction()))
    if not self.indexAt(evt.pos()).isValid() or evt.dropAction() != QtCore.Qt.MoveAction or evt.source() != self:
      return
    super().dropEvent(evt)
    # TODO: find the layer that was dropped and move it to wherever it now is in the QListWidget

  def newLayer(self):
    choice_names = 'Confetti Grid'.split()
    choice = listchoicedialog.ListChoiceDialog.getChoice(self, 'New Layer', 'Layer Type?', choice_names)
    if choice is None:
      return
    item = [Confetti, Grid][choice]()
    item.setData(0, choice_names[choice])
    #item = Confetti()
    #item.setData(0, 'Confetti')
    self.model().scene().addItem(item)
    self.setCurrentIndex(self.model().index(0,0))

  def get_current_item(self):
    return self.model().data( self.currentIndex(), QtCore.Qt.UserRole )

  def deleteCurrentLayer(self):
    if self.currentIndex().row() + 1 >= self.model().rowCount():
      return
    if not isinstance(self.get_current_item(), (Confetti,Grid)):
      return
    stdBtnId = QtWidgets.QMessageBox.question(self
                 , 'Delete Current Layer', 'Are you sure you want to delete layer "{}"?\nThis cannot be undone.'.format(
                       self.model().data(self.currentIndex(), role=QtCore.Qt.DisplayRole) ) )
    if stdBtnId == QtWidgets.QMessageBox.Yes:
      self.model().removeRows(self.currentIndex().row(), 1)

