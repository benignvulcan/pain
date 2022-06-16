
import random as rnd

from PyQt5 import QtCore, QtGui, QtWidgets

from widgetutils import addSliderTo


class Grid(QtWidgets.QGraphicsObject):

  POLAR = 0
  PINSTRIPE = 1
  ISOMETRIC = 2
  SQUARE = 3
  HONEYCOMB = 4

  def __init__(self, *posargs):
    super().__init__(*posargs)
    self._boundingRect = QtCore.QRectF()
    self._type = rnd.choice([self.POLAR, self.ISOMETRIC, self.SQUARE])
    self._radius = 1024
    self._radials = rnd.randrange(12,64)
    self._radialWidgets = []
    self._spacing = rnd.randrange(8,64,4)
    self._thickness = rnd.randrange(1,5)
    self._pen = QtGui.QPen(QtCore.Qt.yellow, self._thickness)
    self._rotation_degrees = None
    self.setRotationDegrees(rnd.randrange(360))

  def updateSceneRect(self, rect):
    self.prepareGeometryChange()
    self.setPos(rect.center() + QtCore.QPointF(.5,.5))
    z = round(max(rect.width(), rect.height()) / 2)
    self._radius = z
    self._boundingRect = QtCore.QRectF(-z,-z,z*2,z*2)
    self.update()

  def itemChange(self, change, value):
    if change == QtWidgets.QGraphicsItem.ItemSceneHasChanged:
      if not value is None:
        value.sceneRectChanged.connect(self.updateSceneRect)
        self.updateSceneRect(value.sceneRect())
    return super().itemChange(change, value)

  def boundingRect(self):
    return QtCore.QRectF(self._boundingRect)

  def paint(self, painter, option, widget=0):
    painter.setClipRect(self._boundingRect)
    painter.setPen(self._pen)
    #painter.drawRect(self._boundingRect)
    if self._type == self.POLAR:
      for r in range(self._spacing, self._radius, self._spacing):
        painter.drawEllipse(QtCore.QPointF(0,0), r,r)
      if self._radials:
        for r in range(self._radials):
          painter.drawLine(0, -self._radius, 0, self._radius)
          painter.rotate(180/self._radials)
    elif self._type == self.PINSTRIPE:
      for i in range(0, self._radius*2, self._spacing):
        painter.drawLine(i-self._radius, -self._radius, i-self._radius, self._radius)   # vertical line
    elif self._type == self.ISOMETRIC:
      for j in range(3):
        painter.drawLine(0, -self._radius, 0, self._radius)     # vline at x=0
        for i in range(self._spacing, self._radius, self._spacing):
          painter.drawLine(i, -self._radius, i, self._radius)   # vline at x=i
          painter.drawLine(-i, -self._radius, -i, self._radius) # vline at x=-i
        painter.rotate(60)
    elif self._type == self.SQUARE:
      for i in range(0, self._radius*2, self._spacing):
        painter.drawLine(i-self._radius, -self._radius, i-self._radius, self._radius)   # vertical line
      for j in range(0, self._radius*2, self._spacing):
        painter.drawLine(-self._radius, j-self._radius, self._radius, j-self._radius)    # horizontal line

  def onIndexChanged(self, idx):
    self._type = idx
    for w in self._radialWidgets:
      w.setVisible(self._type == self.POLAR)
    self.update()

  def setRadials(self, value):
    if value != self._radials:
      self._radials = value
      self.update()

  def setSpacing(self, value):
    if value != self._spacing:
      self._spacing = value
      self.update()

  def setThickness(self, value):
    if value != self._thickness:
      self._thickness = value
      self._pen = QtGui.QPen(self._pen.color(), self._thickness)
      self.update()

  def setRotationDegrees(self, value):
    if value != self._rotation_degrees:
      self._rotation_degrees = value
      self.setRotation(value)
      self.update()

  def onColor(self):
    c = QtWidgets.QColorDialog.getColor( self._pen.color(), None, options=QtWidgets.QColorDialog.ShowAlphaChannel )
    if c.isValid() and c != self._pen.color():
      #self._pen.setColor(QtGui.QColor(c))
      self._pen = QtGui.QPen(c, self._thickness)
      self.update()

  def addWidgetsTo(self, layout):
    label = QtWidgets.QLabel('Grid Type:')
    #label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
    layout.addWidget(label)
    combox = QtWidgets.QComboBox()
    combox.addItems('Polar Pinstripe Isometric Square'.split())
    combox.setCurrentIndex(self._type)
    #combox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
    layout.addWidget(combox)
    combox.currentIndexChanged.connect(self.onIndexChanged)

    self._radialWidgets = addSliderTo(layout, 'Radials', 0, 180, self._radials, self.setRadials)
    addSliderTo(layout, 'Spacing', 1, 256, self._spacing, self.setSpacing)
    addSliderTo(layout, 'Thickness', 1, 32, self._thickness, self.setThickness)
    addSliderTo(layout, 'Rotation', 0, 360, self._rotation_degrees, self.setRotationDegrees, tickInt=15)

    btn = QtWidgets.QPushButton('Color')
    layout.addWidget(btn)
    btn.clicked.connect(self.onColor)
