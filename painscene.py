
from PyQt5 import QtCore, QtGui, QtWidgets

from widgetutils import addSpinBoxTo

class PainScene(QtWidgets.QGraphicsScene):

  def __init__(self, *posargs, **kwargs):
    super().__init__(*posargs, **kwargs)
    self._innerColor = QtGui.QColor(63,63,63)
    self._outerColor = QtGui.QColor(15,15,15)
    self._bgGradient = None
    self._bgVisible = True
    self.light = False

  def setWidth(self, value):
    r = self.sceneRect()
    if value != r.width():
      r.setWidth(value)
      self.setSceneRect(r)  # emits QGraphicsScene.sceneRectChanged(r)

  def setHeight(self, value):
    r = self.sceneRect()
    if value != r.height():
      r.setHeight(value)
      self.setSceneRect(r)

  def recomputeBackground(self):
    print('PainScene.recomputeBackground(): r={}'.format(self.light.outerRadius()))
    self._bgGradient = QtGui.QRadialGradient(self.light.pos(), self.light.outerRadius())
    self._bgGradient.setColorAt(0.0, self._innerColor)
    self._bgGradient.setColorAt(1.0, self._outerColor)
    self.setVisible(self._bgVisible)

  # setVisible(), isVisible(), and data() make this object compatible-enough with QGraphicsItems
  # for the purposes of this application.

  def setVisible(self, visible):
    self._bgVisible = visible
    if self._bgVisible:
      self.setBackgroundBrush(self._bgGradient)
    else:
      self.setBackgroundBrush(QtGui.QBrush(QtCore.Qt.NoBrush))
    self.update()

  def isVisible(self):
    return self._bgVisible

  def data(self, key):
    if key == 0:
      return 'Background'

  def setLight(self, light):
    self.light = light
    self.light.lightSourceChanged.connect(self.recomputeBackground)

  def onInnerColor(self):
    c1 = QtWidgets.QColorDialog.getColor( self._innerColor, None, options=QtWidgets.QColorDialog.ShowAlphaChannel )
    if c1.isValid() and c1 != self._innerColor:
      self._innerColor = QtGui.QColor(c1)
      self.recomputeBackground()

  def onOuterColor(self):
    c1 = QtWidgets.QColorDialog.getColor( self._outerColor, None, options=QtWidgets.QColorDialog.ShowAlphaChannel )
    if c1.isValid() and c1 != self._outerColor:
      self._outerColor = QtGui.QColor(c1)
      self.recomputeBackground()

  def addWidgetsTo(self, layout):
    addSpinBoxTo(layout, 'Width (px)', 16, 1024*8, int(self.width()), self.setWidth)
    addSpinBoxTo(layout, 'Height (px)', 16, 1024*8, int(self.height()), self.setHeight)

    btn = QtWidgets.QPushButton('Lit Color')
    layout.addWidget(btn)
    btn.clicked.connect(self.onInnerColor)

    btn = QtWidgets.QPushButton('Unlit Color')
    layout.addWidget(btn)
    btn.clicked.connect(self.onOuterColor)

