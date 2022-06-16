#!/usr/bin/env python3

'Polyagonal Artistic Interactive Notions'

import time, argparse
import os

from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

from painscene import PainScene
from lightsource import LightSource
from grid import Grid
from confetti import Confetti
from painview import PainView

from layermodel import LayerModel
from layersdock import LayersDock
from parametersdock import ParametersDock

class PainMainWindow(QtWidgets.QMainWindow):

  def __init__(self, *posargs):
    super().__init__(*posargs)
    self.initUI()

  def initUI(self):
    self.resize(QtWidgets.QApplication.primaryScreen().availableGeometry().size()*.92)
    self.setWindowTitle(__doc__)

    #self._scene = PainScene(0,0,1920,1280)
    self._scene = PainScene(QtCore.QRectF(QtCore.QPointF(0,0), QtCore.QSizeF(self.largestWallpaperSize())))
    self._scene.setBackgroundBrush(QtCore.Qt.black)

    self._view = PainView()
    self._view.setScene(self._scene)
    self._view.setRenderHint(QtGui.QPainter.Antialiasing, True)
    self._scene.sceneRectChanged.connect(self._view.updateSceneRect)
    self.setCentralWidget(self._view)

    self._model = LayerModel(self._scene)

    self._paramsDock = ParametersDock(self)
    self._layersDock = LayersDock(self, self._model, self._paramsDock)

    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._layersDock)
    self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._paramsDock)

    self._menuBar = QtWidgets.QMenuBar(self)
    self._fileMenu = QtWidgets.QMenu('&File', self._menuBar)
    self._fileMenu.addAction('Export PNG...', self.onExportPng)
    self._fileMenu.addAction('Export SVG...', self.onExportSvg)
    self._fileMenu.addAction('&Quit', self.close, 'Ctrl+Q')
    self.setMenuBar(self._menuBar)
    self._menuBar.addAction(self._fileMenu.menuAction())

    self.addInitialLayers()
    self._layersDock.selectLayer(1)
    self.show()

  def addInitialLayers(self):
    #self._scene.addRect(self._scene.sceneRect(), QtGui.QPen(QtCore.Qt.green, 3))

    light = LightSource()
    light.setData(0, 'Light Source')
    self._scene.setLight(light)

    grid = Grid()
    grid.setData(0, 'Grid')
    self._scene.addItem(grid)
    #QtWidgets.QGraphicsEllipseItem(400,300, 800,600, grid) # test child items are not layers

    confetti = Confetti()
    confetti.setData(0, 'Confetti')
    self._scene.addItem(confetti)

    self._scene.addItem(self._scene.light)

  def largestWallpaperSize(self):
    screens = QtWidgets.QApplication.screens()
    sizes = [ scr.size() for scr in screens ] + [ scr.virtualSize() for scr in screens ]
    w = 64
    h = 64
    for z in sizes:
      if z.width() > w: w = z.width()
      if z.height() > h: h = z.height()
    return QtCore.QSize(w,h)

  def renderToSvgFileName(self, filename):
    # Note that gradients are stupidly verbosely rendered (two stops are rendered as about 20 stops in the SVG).
    # Note that the Confetti "specular" option somehow triggers rendering a bunch of stuff as embedded raster images!!
    #   At least up thru Qt 5.15.2
    # In theory, just be sure nothing has antialiasing or caching enabled.
    for item in self._scene.items():
      assert item.cacheMode() == QtWidgets.QGraphicsItem.NoCache
    svgGen = QtSvg.QSvgGenerator()
    svgGen.setFileName(filename)
    sz = self._scene.sceneRect().toAlignedRect().size()
    svgGen.setSize(sz)
    #svgGen.setResolution(90)  # trial-and-error reveals this fuck-ass magic number to get the SVG size (in mm!) to match the content
    svgGen.setViewBox(self._scene.sceneRect())  # or, set this.
    svgGen.setTitle("Polyagonal Artistic Interactive Notions")
    svgGen.setDescription("Confetti Art")
    #self._view.setRenderHint(QtGui.QPainter.Antialiasing, False)
    painter = QtGui.QPainter()
    painter.begin(svgGen)
    painter.setRenderHint(QtGui.QPainter.Antialiasing, False)
    print("Rendering to {} x {} SVG file at {} DPI...".format(sz.width(), sz.height(), svgGen.resolution()))
    self._scene.render(painter)
    print("...done.")
    painter.end()
    del painter
    del svgGen

  def renderToPngFileName(self, filename):
    sz = self._scene.sceneRect().toAlignedRect().size()
    qi = QtGui.QImage(sz, QtGui.QImage.Format_ARGB32)
    painter = QtGui.QPainter(qi)
    print("Rendering to {} x {} PNG file...".format(sz.width(), sz.height()))
    painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
    self._scene.render(painter)
    qi.save(filename, "PNG")
    print("...done.")
    del painter
    del qi

  def getSaveFileName(self, extension):
    assert not extension.startswith('.') and not extension.startswith('*')
    defaultName = time.strftime('pain-%Y%m%d@%H%M%S', time.gmtime())
    # NOTE that this triggers a harmless-seeming bug on some (non-KDE?) GNU/Linux systems,
    # causing stderr to output:
    #   Gtk-Message: GtkDialog mapped without a transient parent. This is discouraged.
    (name, selectedFilter) = QtWidgets.QFileDialog.getSaveFileName(self
      , directory = defaultName
      , filter = '*.' + extension
     , options = QtWidgets.QFileDialog.DontConfirmOverwrite #| QtWidgets.QFileDialog.HideNameFilterDetails
      )
    if name:
      if not name.lower().endswith('.'+extension.lower()):
        name = name + '.' + extension
      if os.path.exists(name):
        stdBtnId = QtWidgets.QMessageBox.question(self, 'Overwrite file?',
          'A file named "{}" already exists.  Are you sure you want to overwrite it?'.format(name))
        if stdBtnId != QtWidgets.QMessageBox.Yes:
          name = ''
    return name

  def onExportSvg(self):
    name = self.getSaveFileName('svg')
    if name:
      self.renderToSvgFileName(name)
    return True

  def onExportPng(self):
    name = self.getSaveFileName('png')
    if name:
      self.renderToPngFileName(name)
    return True

  def closeEvent(self, evt):
    evt.accept()


def main(argv):
  global qapp  # prevent eager GC from causing segfault on return from main

  '''
  Note that QApplication seems to ignore nearly all errors in arguments,
  and often seems to ignore arguments it recognizes, too.
  QApplication.arguments() will reveal by omission which arguments were recognized.
  '''
  ap = argparse.ArgumentParser()
  opts, argv_remaining = ap.parse_known_args()

  #np_test()

  qapp = QtWidgets.QApplication(argv[:1] + argv_remaining)

  print('Available "-style" choices: ', ', '.join(QtWidgets.QStyleFactory.keys()))

  mainWnd = PainMainWindow()
  return qapp.exec_()


if __name__=='__main__':
  import sys
  sys.exit(main(sys.argv))
