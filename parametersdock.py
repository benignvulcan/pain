
from PyQt5 import QtCore, QtWidgets

from widgetutils import clearLayout

class ParametersDock(QtWidgets.QDockWidget):

  def __init__(self, *posargs):
    super().__init__(*posargs)

    self.setWindowTitle('Parameters')
    self.setFeatures( QtWidgets.QDockWidget.DockWidgetFloatable
                    | QtWidgets.QDockWidget.DockWidgetMovable )

    self._scrollWidget = QtWidgets.QScrollArea(self)
    self._scrollWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
    self._scrollWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
    self._scrollWidget.setWidgetResizable(True)

    self._contentsWidget = QtWidgets.QWidget(self._scrollWidget)
    self._contentsLayout = QtWidgets.QVBoxLayout(self._contentsWidget)
    #self._contentsLayout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)      # this prevents expansion in BOTH directions!
    #self._contentsLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)  # fails to prevent excess expansion
    self._contentsWidget.setLayout(self._contentsLayout)

    self._scrollWidget.setWidget(self._contentsWidget)
    self.setWidget(self._scrollWidget)

    #for i in range(32):
    #  self._contentsLayout.addWidget(QtWidgets.QSlider(QtCore.Qt.Horizontal, self._contentsWidget))

  def loadParamsFrom(self, source):
    clearLayout(self._contentsLayout)
    if not source is None:
      #self._contentsLayout.addWidget(QtWidgets.QLabel('Layer "{}"'.format(source.data(0)))) # not updated on rename
      source.addWidgetsTo(self._contentsLayout)
      self._contentsLayout.addStretch()  # *THIS* is what prevents excessive spacing!
