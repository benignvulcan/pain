
from PyQt5 import QtCore, QtWidgets

from layerswidget import LayersWidget


class LayersDock(QtWidgets.QDockWidget):

  def __init__(self, parent, model, paramsDock, *posargs):
    super().__init__(parent, *posargs)
    self._paramsDock = paramsDock

    self.setWindowTitle('Layers')
    self.setFeatures( QtWidgets.QDockWidget.DockWidgetFloatable
                    | QtWidgets.QDockWidget.DockWidgetMovable )

    # A QDockWidget contains only one widget.
    self._layersPanel = QtWidgets.QWidget(self)
    self.setWidget(self._layersPanel)
    
    # But a regular QWidget can contain many other QWidgets,
    # and they can be arranged using nested QLayouts without need for additional intermediate QWidgets.
    self._layersLayout = QtWidgets.QVBoxLayout(self._layersPanel)

    self._layersWidget = LayersWidget(self._layersPanel)
    self._layersWidget.setModel(model)
    #self._layersWidget.currentItemChanged.connect(self.currentLayerChanged)
    self._layersWidget.selectionModel().currentChanged.connect(self.currentLayerChanged)
    #self._layersWidget.itemClicked.connect(self.layerClicked)  # notifies of any click, not checkbox change.
    #             # treeWidget.model().dataChanged.connect(handle_dataChanged) probably isn't quite it either
    self._layersLayout.addWidget(self._layersWidget)

    self._buttonLayout = QtWidgets.QGridLayout()
    self._layersLayout.addLayout(self._buttonLayout)
    up = QtWidgets.QPushButton('Up')
    dn = QtWidgets.QPushButton('Down')
    nw = QtWidgets.QPushButton('New')
    dl = QtWidgets.QPushButton('Delete')
    self._buttonLayout.addWidget(up,0,0)
    self._buttonLayout.addWidget(dn,1,0)
    self._buttonLayout.addWidget(nw,0,1)
    self._buttonLayout.addWidget(dl,1,1)
    dn.clicked.connect(self._layersWidget.moveCurrentDown)
    up.clicked.connect(self._layersWidget.moveCurrentUp)
    nw.clicked.connect(self._layersWidget.newLayer)
    dl.clicked.connect(self._layersWidget.deleteCurrentLayer)

    #self._layersLayout.addStretch()  # does not prevent excess size

  def insertLayer(self, layer):
    #self._layersWidget.insertTopLevelItem(0, layer)
    self._layersWidget.insertItem(0, layer)
    self._paramsDock.loadParamsFrom(layer)

  def selectLayer(self, y=0):
    model = self._layersWidget.model()
    midx = model.index(y,0)
    if midx.isValid():
      self._layersWidget.selectionModel().setCurrentIndex(model.index(y,0), QtCore.QItemSelectionModel.Select)
    else:
      print('selectLayer: index({},0) is invalid'.format(y))

  def currentLayerChanged(self, current_modelIdx, previous_modelIdx):
    print('LayersDock.currentLayerChanged')
    self._paramsDock.loadParamsFrom(current_modelIdx.data(role=QtCore.Qt.UserRole))

  def layerClicked(self, item, column):
    print('LayersDock.layerClicked(item={}, column={})'.format(item, column))
    print('  item.checkState(0) = {}'.format(item.checkState(0)))

