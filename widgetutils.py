
from PyQt5 import QtCore, QtGui, QtWidgets

def clearLayout(layout):
  'Remove all widgets and sub-layouts (and their widgets) from the given layout.'
  # This does not directly remove grand-child widgets, and should not need to.
  # This will likely fail if you've somehow managed to nest layouts many dozens deep.
  # See the remarkably incomplete discussion at
  #   https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
  if not layout is None:
    while layout.count():
      item = layout.takeAt(0)
      w = item.widget()
      if not w is None:
        w.setParent(None)
        w.deleteLater()
      else:
        y = item.layout()
        if not y is None:
          clearLayout(y)  # Recurse on sub-layouts.
      layout.removeItem(item)  # Whatever it is, remove it from the layout.

def addSliderTo(layout, name, lo, hi, value, setter, tickInt=None):
  label = QtWidgets.QLabel(name)
  layout.addWidget(label)
  slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
  slider.setRange(lo, hi)
  slider.setValue(value)
  if not tickInt is None:
    slider.setTickInterval(tickInt)
    slider.setTickPosition(QtWidgets.QSlider.TicksAbove)
  #label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
  #slider.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
  layout.addWidget(slider)
  slider.valueChanged.connect(setter)
  slider.sliderMoved.connect(lambda v: QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), str(v)))
  return (label, slider)

def addSpinBoxTo(layout, name, lo, hi, value, setter):
  y = QtWidgets.QHBoxLayout()
  label = QtWidgets.QLabel(name)
  #label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
  y.addWidget(label)
  spinbox = QtWidgets.QSpinBox()
  spinbox.setRange(lo,hi)
  spinbox.setValue(value)
  #spinbox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum)
  y.addWidget(spinbox)
  layout.addLayout(y)
  spinbox.valueChanged.connect(setter)
  return (label, spinbox)
