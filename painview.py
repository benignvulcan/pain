
from PyQt5 import QtCore, QtGui, QtWidgets

class PainView(QtWidgets.QGraphicsView):

  def resizeEvent(self, evt):
    super().resizeEvent(evt)
    print('PainView.resizeEvent: sceneRect ==', self.scene().sceneRect())
    self.fitInView(self.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)

  def updateSceneRect(self, rect):
    super().updateSceneRect(rect)
    print('PainView.updateSceneRect({})'.format(rect))
    self.fitInView(self.scene().sceneRect(), QtCore.Qt.KeepAspectRatio)

