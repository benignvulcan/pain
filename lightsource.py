
from PyQt5 import QtCore, QtGui, QtWidgets

from widgetutils import addSliderTo, addSpinBoxTo

class LightSource(QtWidgets.QGraphicsObject):

  def __init__(self, *posargs):
    super().__init__(*posargs)
    self._boundingRect = QtCore.QRectF(-8,-8,16,16)
    self._x = .5
    self._y = .5
    self._inner_r = .20
    self._outer_r = .80
    self._scene_inner_r = 400
    self._scene_outer_r = 1600
    self._color = QtGui.QColor(255,255,255)
    self.setVisible(False)
 
  lightSourceChanged = QtCore.pyqtSignal(object)  # a Signal whose arg is a tuple

  def computeLightSource(self):
    print('computeLightSource')
    self.setPos(QtCore.QPointF(self.scene().width()*self._x, self.scene().height()*self._y))
    diameter = max(self.scene().width(), self.scene().height())
    if self._inner_r <= self._outer_r:
      self._scene_inner_r = diameter * self._inner_r
      self._scene_outer_r = diameter * self._outer_r
    else:
      self._scene_inner_r = self._scene_outer_r = diameter * self._outer_r
    self.lightSourceChanged.emit( (self.pos(), self._scene_inner_r, self._scene_outer_r) )
    self.scene().update()

  def itemChange(self, change, value):
    if change == QtWidgets.QGraphicsItem.ItemSceneHasChanged:
      self.computeLightSource()
    return super().itemChange(change, value)

  def innerRadius(self):
    return self._scene_inner_r

  def outerRadius(self):
    return self._scene_outer_r

  def boundingRect(self):
    return QtCore.QRectF(self._boundingRect)

  def paint(self, painter, option, widget=0):
    painter.setPen(QtCore.Qt.NoPen)
    painter.setBrush(QtCore.Qt.white)
    painter.drawEllipse(self._boundingRect)
    return

  def setLightSourceX(self, value):
    value = value/100.0
    if value != self._x:
      self._x = value
      self.computeLightSource()

  def setLightSourceY(self, value):
    value = value/100.0
    if value != self._y:
      self._y = value
      self.computeLightSource()

  def setLightSourceInnerR(self, value):
    value = value/100.0
    if value != self._inner_r:
      self._inner_r = value
      self.computeLightSource()

  def setLightSourceOuterR(self, value):
    value = value/100.0
    if value != self._outer_r:
      self._outer_r = value
      self.computeLightSource()

  def color(self):
    return QtGui.QColor(self._color)

  def onColor(self):
    c = QtWidgets.QColorDialog.getColor( self._color, None, options=QtWidgets.QColorDialog.ShowAlphaChannel )
    if c.isValid() and c != self._color:
      self._color = QtGui.QColor(c)
      self.computeLightSource()

  def addWidgetsTo(self, layout):
    addSliderTo(layout, 'Light Source X', -100, 200, int(self._x*100), self.setLightSourceX)
    addSliderTo(layout, 'Light Source Y', -100, 200, int(self._y*100), self.setLightSourceY)
    addSliderTo(layout, 'Light Source Inner Radius', 10, 400, int(self._inner_r*100), self.setLightSourceInnerR)
    addSliderTo(layout, 'Light Source Outer Radius', 10, 400, int(self._outer_r*100), self.setLightSourceOuterR)
    
    btn = QtWidgets.QPushButton('Color')
    layout.addWidget(btn)
    btn.clicked.connect(self.onColor)

