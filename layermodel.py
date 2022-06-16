
from PyQt5 import QtCore #, QtGui, QtWidgets

class LayerModel(QtCore.QAbstractListModel):

  'An interface to the QGraphicsItems in a QGraphicsScene'

  def __init__(self, scene):
    super().__init__()
    self._scene = scene
    scene.changed.connect(self.sceneChanged)

  def scene(self):
    return self._scene

  def sceneChanged(self):
    self.layoutChanged.emit()

  #def sizeHint(self):
  #  z = super().sizeHint()
  #  if z.isValid():
  #    return z / 3
  #  return z

  def layerItems(self):
    items = list(it for it in self._scene.items() if it.parentItem() is None)
    items.append(self._scene)
    return items

  def rowCount(self, parent=QtCore.QModelIndex()):
    return len(self.layerItems())

  def index(self, row, column, parent=QtCore.QModelIndex()):
    return self.createIndex(row, 0)

  def data(self, modelIdx, role=QtCore.Qt.DisplayRole):
    if role in (QtCore.Qt.DisplayRole, QtCore.Qt.EditRole):
      # Return name of QGraphicsItem
      items = self.layerItems()
      r = modelIdx.row()
      return items[r].data(0)
    elif role == QtCore.Qt.CheckStateRole:
      # Return whether QGraphicsItem is visible
      return (QtCore.Qt.Unchecked, QtCore.Qt.Checked)[self.layerItems()[modelIdx.row()].isVisible()]
    elif role == QtCore.Qt.UserRole:
      # Return QGraphicsItem itself
      items = self.layerItems()
      if items:
        return items[modelIdx.row()]
      else:
        return None

  def setData(self, modelIdx, value, role=None):
    if role == QtCore.Qt.CheckStateRole:
      print('LayerModel.setData row={}, value={}'.format(modelIdx.row(), value))
      self.layerItems()[modelIdx.row()].setVisible(value!=QtCore.Qt.Unchecked)
      self.dataChanged.emit(modelIdx, modelIdx, [QtCore.Qt.CheckStateRole])
      return True
    elif role == QtCore.Qt.EditRole:
      self.layerItems()[modelIdx.row()].setData(0, value)
      return True
    return super().setData(modelIdx, value, role)

  def flags(self, modelIdx):
    flags = super().flags(modelIdx) | QtCore.Qt.ItemIsUserCheckable
    if modelIdx.isValid() and modelIdx.row() < self.rowCount() - 1:
      flags |= QtCore.Qt.ItemIsEditable
    return flags

  '''
  QAbstractItemModel doesn't actually provide an interface for rearranging elements!
    There's a bunch of insert and remove and move functions:
       * insert just inserts blank/empty items
       * remove doesn't return the items being removed
       * the move functions aren't called by anything in Qt
  Apparently the application programmer should just tack on their own means
    of actually manipulating the data beyond strictly viewing the data,
    editing individual items, or I guess maybe re-sizing the amount of data?
  Likewise, serializing data just to support app-internal drag & drop is
    stupidly expensive, and the programmer is I guess epxected to just
    "cheat" and stash the data somewhere.
  '''

  def removeRows_(self, row, count, parent=QtCore.QModelIndex()):
    self.beginRemoveRows(parent, row, row+count-1)
    items = self.layerItems()
    if row+count >= len(items):
      return []  # fail to delete last row
    items = items[row:row+count]
    for it in items:
      self._scene.removeItem(it)
    self.endRemoveRows()
    return items

  def removeRows(self, row, count, parent=QtCore.QModelIndex()):
    return self.removeRows_(row,count,parent) != []

  def moveDown(self, modelIdx):
    if modelIdx.isValid():
      i = modelIdx.row()
      items = self.layerItems()
      if i+2 < len(items):  # refuse to move below Background layer
        self.layoutAboutToBeChanged.emit()
        items[i].stackBefore(items[i+1])
        self._scene.update()
        self.layoutChanged.emit()
        return self.createIndex(i+1, 0)
    return QtCore.QModelIndex()  # return an invalid index

  def moveUp(self, modelIdx):
    if modelIdx.isValid():
      i = modelIdx.row()
      items = self.layerItems()
      if i > 0 and i+2 <= len(items):
        self.layoutAboutToBeChanged.emit()
        items[i-1].stackBefore(items[i])
        self._scene.update()
        self.layoutChanged.emit()
        return self.createIndex(i-1, 0)
    return QtCore.QModelIndex()  # return an invalid index

