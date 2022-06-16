
import math
import random as rnd
import time

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets, QtSvg

from qmathturtle import RecordingTurtle
from widgetutils import addSliderTo


'''
How to do affine transforms of arrays of points using numpy?
  row-major notation:
    matrix sizes & indices are written row first: (r,c)
    Note that this is typically equivalent to (y,x) !
  row-major storage ordering (usually also n row-major notation):
    element(r,c) = element[r*width + c]
    NumPy and C uses row-major: element[r][c]
    OpenGL is confusing/weird, but apparently uses column-major storage and notation.
  Basic linear algebra:
    Matrices are associative but not commutative:
      A * B * C = (A * B) * C = A * (B * C)
      A * B != B * A
    See 'composing transformations pre vs post mutiply 6-Transformation_II.pdf'
    Post-multiplcation of transforms tends to be more natural:
      v' = M * v       # where M is the 3x3 transformation matrix, and v is a column vector [x,y{{,z},1}]
      M = R * T * S  # to rotate, translate, and then scale
      v' = M * v = R * T * S * v
      Used by OpenGL.
      Apparently the way QTransform does it.
    Switching to pre-multiplication requires transposing the matrix and the vector:
      v' = v * M = v * S * T * R   # where v is a row vector
    Handedness
      Most systems use right-handed coordinate systems.
  NumPy
    dot(a, b)
    matmul(a, b)
    meshgrid, mgrid ?
  Qt Transformations:
    QTransform(m11,m12, m21,m22, dx,dy)
    QTransform(m11,m12,m13, m21,m22,m23, dx,dy,m33=1)
      sx  m12 m13  Rotation is controled by sx,m12,m21,sy
      m21 sy  m23
      dx  dy  m33
      Seems to implicitly post-multiply.
  QPolygonF(QVector of QPointF)
  From https://stackoverflow.com/questions/35034389/applying-a-fast-coordinate-transformation-in-python :
      xy = np.vstack([xx.ravel(), yy.ravel()])   # xy = [XS,YS] # a 2-row, N-column array
      xy_t = np.dot(s, xy)
      xx_t, yy_t = xy_t.reshape((2, image_dimension, image_dimension))
    pts' = np.dot(M, pts)

  See https://staff.fnwi.uva.nl/r.vandenboomgaard/IPCV20162017/LectureNotes/MATH/homogenous.html

'''

def np_test():
  print('==== NP test')
  XY = np.array([[0, 3, 3, 0, -1]
                ,[0, 0, 2, 2, -1]
                ,[1, 1, 1, 1,  1]])  # add "1" ordinate for homogenous coordinates
  print(XY)
  M = np.array([[4, 0, 0]     # [sx * cos r,     -sin r, dx]
               ,[0, 4, 3]     # [     sin r, sy * cos r, dy]
               ,[0, 0, 1]])   # [         0,          0,  1]
  print(M)
  XY2 = np.dot(M, XY)
  print(XY2)
  XY3 = XY2 / XY2[-1]    # divide back out the homogenous ordinate
  print(XY3)
  print('====')

def RegularPolygonNP(sides, r=1.0, rotate=0.0):
  '''Return a numpy array of shape (sides,2) containing the coordinates of the requested regular polygon.
  The vertices start on the positive X axis and rotate CCW around the origin.'''
  # However one decides the radius and orientation, computing the rectangular
  #   coordinates of a regular polygon comes down to this.
  # At this stage, rotation is particularly cheap, so include it as an option.
  thetas = np.arange(sides) * (rotate + (2*math.pi/sides))          # compute angles
  return np.column_stack((r * np.cos(thetas), r * np.sin(thetas)))  # compute coordinates

def StarPolygon(n,d, size=1):
  '''
    n = number of points
    d = number of winds or turns = visit every d-th point
  '''
  spike_exterior_angle = 360 * d / n
  spike_interior_angle = 180 - spike_exterior_angle
  crotch_angle = 180 - (360 / n + spike_interior_angle)
  spike_height = size * math.sin(math.radians(crotch_angle))
  '''
    # know angle A and sides b and c, need side a
    a*a = b*b + c*c - 2*b*c*cos(A)          # law of cosines
    a = sqrt( b*b + c*c - 2*b*c*cos(A) )
    a = sqrt( s*s + s*s - 2*s*s*cos(A) )    # sides b and c are the same
    a = sqrt(   2*s*s   - 2*s*s*cos(A) )
    a = sqrt(    s*s * (2 - 2*cos(A))  )    # factor s*s out
    a =    sqrt(s*s) * sqrt(2 - 2*cos(A))   # root of products equals product of roots
    a =            s * sqrt(2 - 2*cos(A))
  '''
  circumscribed_polygon_side = size * math.sqrt(2 - 2*math.cos(math.radians(180-crotch_angle)))
  radius = circumscribed_polygon_side / (2*math.sin(math.pi/n))
  t = RecordingTurtle()
  # Draw star centered and with first point up
  t.pu().lt(90).bk(radius).lt(spike_interior_angle/2).pd()
  for i in range(n):
    t.fd(size).lt(crotch_angle)
    if i < n - 1:
      t.fd(size).rt(spike_exterior_angle)
  return t.polygon()

def inverse_distribution(low, high):
  'Return an array of values from high to low, steeply tilted in favor of low.'
  # I don't know what this is really called.
  assert isinstance(low, int)
  assert isinstance(high, int)
  h = high-low+1
  return [ low - 1 + (h/x) for x in range(1,h) ]

SAMPLES = 500
INVERSE_DISTRIBUTION = np.array(inverse_distribution(0, SAMPLES))   # 500 .. 0.002
LINEAR_DISTRIBUTION = np.array(list(float(SAMPLES - x) for x in range(SAMPLES+1))) # 500 .. 0
print(INVERSE_DISTRIBUTION)
print(LINEAR_DISTRIBUTION)

class Shape:
  def __init__(self, name):
    self._name = name

class Polygon(Shape):
  def __init__(self, name, qpolygonf):
    super().__init__(name)
    self._qpolygonf = qpolygonf
  def transformed(self, xform):
    return Polygon(self._name, xform.map(self._qpolygonf))
  def addToPath(self, path):
    path.addPolygon(self._qpolygonf)
  def paint(self, painter):
    painter.drawPolygon(self._qpolygonf)
  def paintShadow(self, painter, dx, dy):
    t = QtGui.QTransform.fromTranslate(dx, dy)
    painter.drawPolygon(t.map(self._qpolygonf))

class RegularPolygon(Polygon):
  def __init__(self, name, sides, r, qpolygonf=None):
    self._sides = sides
    self._radius = r
    if qpolygonf is None:
      qpolygonf = QtGui.QPolygonF([QtCore.QPointF(*p) for p in RegularPolygonNP(sides=sides, r=r)])
    super().__init__(name, qpolygonf=qpolygonf)
  def area(self):
    return self._sides * self._radius**2 * math.sin(2*math.pi/self._sides) / 2
  def transformed(self, xform):
    r2 = xform.map(QtCore.QLineF(QtCore.QPointF(0,0), QtCore.QPointF(self._radius, 0))).length()
    return RegularPolygon(self._name, self._sides, r2, qpolygonf=xform.map(self._qpolygonf))

class Star(Polygon):
  def __init__(self, name, r, qpolygonf=None):
    self._radius = r
    if qpolygonf is None:
      qpolygonf=StarPolygon(5,2,r)
    super().__init__(name, qpolygonf=qpolygonf)
  def transformed(self, xform):
    r2 = xform.map(QtCore.QLineF(QtCore.QPointF(0,0), QtCore.QPointF(self._radius, 0))).length()
    return Star(self._name, r2, qpolygonf=xform.map(self._qpolygonf))

class Circle(Shape):
  def __init__(self, name, r=1.0, center=None):
    super().__init__(name)
    self._radius = r
    if center is None:
      center = QtCore.QPointF(0,0)
    self._center = center
  def area(self):
    return math.pi * self._radius**2
  def transformed(self, xform):
    r2 = xform.map(QtCore.QLineF(self._center, self._center + QtCore.QPointF(self._radius, 0))).length()
    return Circle(self._name, r2, center=xform.map(self._center))
  def addToPath(self, path):
    path.addEllipse(self._center, self._radius, self._radius)
  def paint(self, painter):
    painter.drawEllipse(self._center, self._radius, self._radius)
  def paintShadow(self, painter, dx, dy):
    t = QtGui.QTransform.fromTranslate(dx, dy)
    painter.drawEllipse(t.map(self._center), self._radius, self._radius)

class Confetti(QtWidgets.QGraphicsObject):

  def __init__(self, *posargs, **kwargs):
    super().__init__(*posargs, **kwargs)
    #self.setData(0, 'Confetti')
    #scene.addItem(self)
    self._boundingRect = QtCore.QRectF(0,0,800,600)        # bounding rect for rendered content
    print('Confetti._boundingRect =', self._boundingRect)

    self._max_quantity = 2**14                      # maximum allowed _quantity
    self._quantity = int(self._max_quantity / 8)    # current number of polygons

    self.initShapes()

    # See https://math.stackexchange.com/questions/3157030/parametrizing-the-square-spiral
    ns = np.arange(self._max_quantity)
    nss = np.sqrt(ns)
    self._arranged_xlateX = nss * np.cos(2*np.pi*nss/4) / 80
    self._arranged_xlateY = nss * np.sin(2*np.pi*nss/4) / 80
    self._posRandomness = 1000

    self._theta = 0
    self._theta_variation = 2 * math.pi
    self._radius_param = 16                           # circumscribed radius of polygons
    self._radius_variation = self._radius_param // 2  # randomly change radius by this much
    self._radius_aux = 0

    self._MAX_BORDER = 64
    self._edgeThickness = 1

    self._hue = rnd.randrange(360) #300
    self._hue_variation = rnd.randrange(5, 180) #60
    self._min_saturation = 100
    self._max_saturation = 100
    self._kappa = .5                                # distribution of lightness values
    self._min_lightness = 50
    self._max_lightness = 50

    self._min_opacity = 255                             # opacity == alpha channel
    self._gradient_opacity = 191

    self._shadow_opacity = 204
    self._shadow_divisor = 50
    self._specularGradient = None
    self._specularBrightness = 0
    self._specularDepth = 33      # percentage
    self._specularSharpness = 75  # percentage
    self._bevelThickness = 0

    self._pressed_render = False
    self._last_full_render_time = 1/30

    # Array quantities
    #self._rnd_lightnesses = None                      # array of lightness values, before clamping
    #self._rnd_saturations = None
    self.randomize()
    self.invalidateAll()

  def initShapes(self):
    self._shapes = []        # a list of available Shape objects
    NAMES = 'Triangles Squares Pentagons Hexagons'.split()
    area = math.pi
    for i in range(len(NAMES)):
      sides = i+3
      r = math.sqrt( 2 * area / (sides * math.sin(2*math.pi/sides)) )
      #print('{} radius = {}'.format(NAMES[i], r))
      shp = RegularPolygon(NAMES[i], sides, r)
      shp.qty = rnd.randrange(2,20)
      self._shapes.append(shp)
    # https://www.quora.com/How-do-you-find-the-area-of-a-regular-5-pointed-star-inscribed-in-the-circle-of-radius-R
    # a = 5 r^2 / (tan 72 + tan 54)
    AREA = 1
    r = math.sqrt( AREA * ((math.tan(math.radians(72)) + math.tan(math.radians(54))) / 5) )
    #print('star: area {} -> radius {}'.format(AREA, r))
    shp = Star('Stars', r=r)
    shp.qty = 1
    self._shapes.append(shp)
    c = Circle('Circles')
    c.qty = rnd.randrange(2,20)
    self._shapes.append(c)

  def invalidateFillGradients(self):
    self._fill_gradients = None                           # array of Qt gradients

  def invalidateColor(self):
    self._color = None                              # array of derived fill colors
    self.invalidateFillGradients()

  def invalidateHue(self):
    self._clamped_hues = None
    self.invalidateColor()

  def invalidateSaturation(self):
    self._clamped_saturations = None
    self.invalidateColor()

  def invalidateLightness(self):
    self._clamped_lightness = None
    self.invalidateColor()

  def invalidateXformedShapes(self):
    self._xformed_shapes = None
    self.invalidateFillGradients()
    self.invalidateSpecular()

  def invalidateXforms(self):
    self._xform = None
    self.invalidateXformedShapes()

  def invalidateSpecular(self):
    self.invalidateLightness()
    self._specularGradient = None
    self._bevelGradient = None

  def invalidateAll(self):
    self.invalidateXforms()
    self.invalidateHue()
    self.invalidateSaturation()
    self.invalidateLightness()
    self.invalidateSpecular()

  def itemChange(self, change, value):
    #print('Confetti.itemChange({}, {})'.format(change, value))
    '''
      ItemSceneChange: `value` is proposed new Scene; return None to prevent Scene change.
        Sent before changing self.scene(), which is still the old Scene.
        This includes being sent when self is being added to its initial Scene.
      ItemSceneHasChanged: `value` is the new Scene; return value is ignored.
        Sent after changing self.scene(), which is the new Scene (including None).
    '''
    if change == QtWidgets.QGraphicsItem.ItemSceneChange: #, QtWidgets.QGraphicsItem.ItemSceneHasChanged):
      # value is the proposed/new Scene
      print('Confetti.itemChange(ItemSceneChange, {})'.format(value))
      if value is None:
        if not self.scene() is None:
          print('  disconnecting from lightSourceChanged signal')
          self.scene().light.lightSourceChanged.disconnect(self.updateLightSource)
          self.scene().sceneRectChanged.disconnect(self.updateSceneRect)
      else:
        self.prepareGeometryChange()
        self._boundingRect = value.sceneRect()
        self.invalidateXforms()
        self.update()
        print('  connecting to lightSourceChanged signal')
        value.light.lightSourceChanged.connect(self.updateLightSource)
        value.sceneRectChanged.connect(self.updateSceneRect)
        return value
    else:
      return super().itemChange(change, value)

  def updateSceneRect(self, r):
    self.prepareGeometryChange()
    self._boundingRect = r
    self.invalidateXforms()
    self.update()

  def setQuantity(self, value):
    if value > self._max_quantity:
      value = self._max_quantity
    elif value < 0:
      value = 0
    if value != self._quantity:
      old = self._quantity
      self._quantity = value
      #self.quantityChanged.emit(old, value)
      self.update()

  def setShapeQuantity(self, shape, value):
    if value != shape.qty:
      shape.qty = value
      self.invalidateXformedShapes()
      self.update()

  def setPosRandomness(self, value):
    if value != self._posRandomness:
      self._posRandomness = value
      self.invalidateXforms()
      self.update()

  def setTheta(self, value):
    rad = value * math.pi / 180
    if rad != self._theta:
      self._theta = rad
      self.invalidateXforms()
      self.update()

  def setThetaVariation(self, value):
    rad = value * math.pi / 180
    if rad != self._theta_variation:
      self._theta_variation = rad
      self.invalidateXforms()
      self.update()

  def setRadius(self, value):
    if value != self._radius_param:
      self._radius_param = value
      self.invalidateXforms()
      self.update()

  def setRadiusVariation(self, value):
    if value != self._radius_variation:
      old = value
      self._radius_variation = value
      self.invalidateXforms()
      self.update()

  def setRadiusAux(self, value):
    if value != self._radius_aux:
      self._radius_aux = value
      self.invalidateXforms()
      self.update()

  def setEdgeThickness(self, value):
    if value > self._MAX_BORDER:
      value = self._MAX_BORDER
    elif value < 0:
      value = 0
    if value != self._edgeThickness:
      old = self._edgeThickness
      self._edgeThickness = value
      self.update()

  def setHue(self, value):
    if value != self._hue:
      self._hue = value
      self.invalidateHue()
      self.update()

  def setHueVariation(self, value):
    if value != self._hue_variation:
      self._hue_variation = value
      self.invalidateHue()
      self.update()

  def setMinSaturation(self, value):
    if value != self._min_saturation:
      self._min_saturation = value
      #if value > self._max_saturation:
      #  self._max_saturation = value
      print('setMinSaturation({})'.format(value))
      self.invalidateSaturation()
      self.update()

  def setMaxSaturation(self, value):
    if value != self._max_saturation:
      self._max_saturation = value
      #if value < self._min_saturation:
      #  self._min_saturation = value
      print('setMaxSaturation({})'.format(value))
      self.invalidateSaturation()
      self.update()

  def updateLightSource(self, light_source):
    self.invalidateLightness()
    self.invalidateSpecular()
    self.update()

  def setShadowOpacity(self, value):
    if value != self._shadow_opacity:
      self._shadow_opacity = value
      self.update()

  def setShadowDivisor(self, value):
    if value != self._shadow_divisor:
      self._shadow_divisor = value
      self.invalidateLightness()
      self.update()

  def setMinLightness(self, value):
    if value != self._min_lightness:
      self._min_lightness = value
      self.invalidateLightness()
      self.update()

  def setMaxLightness(self, value):
    if value != self._max_lightness:
      self._max_lightness = value
      self.invalidateLightness()
      self.update()

  def setMinOpacity(self, value):
    if value != self._min_opacity:
      self._min_opacity = value
      self.invalidateFillGradients()
      self.update()

  def setGradientOpacity(self, value):
    if value > 255: value = 255
    elif value < 0: value = 0
    if value != self._gradient_opacity:
      old = self._gradient_opacity
      self._gradient_opacity = value
      self.invalidateFillGradients()
      self.update()

  #def setSpecular(self, state):
  #  self._specular = (state != QtCore.Qt.Unchecked)
  #  self.update()

  def setSpecularBrightness(self, value):
    if value != self._specularBrightness:
      self._specularBrightness = value
      self.invalidateSpecular()
      self.update()

  def setSpecularDepth(self, value):
    if value != self._specularDepth:
      self._specularDepth = value
      self.invalidateSpecular()
      self.update()

  def setSpecularSharpness(self, value):
    if value != self._specularSharpness:
      self._specularSharpness = value
      self.invalidateSpecular()
      self.update()

  def setBevelThickness(self, value):
    if value != self._bevelThickness:
      self._bevelThickness = value
      self.invalidateSpecular()
      self.update()

  def boundingRect(self):
    return QtCore.QRectF(self._boundingRect)

  def randomize(self):
    # "New code should use the uniform method of a default_rng() instance instead; please see
    #   https://numpy.org/doc/stable/reference/random/index.html#random-quick-start "
    # np.random.uniform() returns float values from 0.0 to 1.0 NOT including 1.0
    # The implications of the half-open interval are completely unclear to me.

    seed = None
    rng = np.random.default_rng(seed)

    self._rnd_shapes = rng.uniform(size=self._max_quantity)           # which shapes to use
    self._rndPosX = rng.uniform(size=self._max_quantity) - .5 # -.5 to +.5
    self._rndPosY = rng.uniform(size=self._max_quantity) - .5
    self._rnd_thetas = rng.uniform(size=self._max_quantity)
    #self._rnd_radii  = rng.uniform(size=self._max_quantity)
    #self._rnd_radii  = .01 / np.power(.025+.975*rng.uniform(size=self._max_quantity), 2)  # approx 1/x^2
    #self._rnd_radii = rng.choice(SCALED_AREA_DISTRIBUTION, size=self._max_quantity) # 0 to 500
    self._rnd_radii_idxs = rng.integers(SAMPLES, size=self._max_quantity)

    self._rnd_hues = rng.uniform(size=self._max_quantity)
    self._rnd_saturations = rng.uniform(size=self._max_quantity)
    #self._rnd_saturations = 1 - np.sqrt(rng.uniform(size=self._max_quantity))
    self._rnd_lightnesses = rng.uniform(size=self._max_quantity)       # [0..1)
    #self._rnd_lightnesses = [
                          # .5                 # all fully saturated, no black or white
                          # rnd.uniform(0,1.0) # many colors, but too much black & white
                          #rnd.triangular()   # lots of color, some black & white
    #                      rnd.vonmisesvariate(math.pi, self._kappa)/(2*math.pi)
    #                      for i in range(self._max_quantity) ]
    #self._rnd_lightnesses = (rng.vonmises(math.pi, self._kappa, size=self._max_quantity)+math.pi) / (2*math.pi)
    self._rnd_opacities = 1 - np.sqrt(rng.uniform(size=self._max_quantity))

    self.invalidateAll()

  def computeXforms(self):
    'Recompute translation/rotation/scaling matrix transforms'
    assert type(self._quantity) is int
    if self._xform is None or len(self._xform) < self._quantity:
      maxwh = max(self._boundingRect.width(), self._boundingRect.height())
      pr = self._posRandomness / 1000
      xs = (self._arranged_xlateX*(1-pr) + self._rndPosX*pr) * maxwh + self._boundingRect.width()/2
      ys = (self._arranged_xlateY*(1-pr) + self._rndPosY*pr) * maxwh + self._boundingRect.height()/2
      #variation = self._radius_aux / 100 / (.1+.9*self._rnd_radii) ** 2
      #variation = np.power(self._rnd_radii, 1/(2 - self._radius_aux/100))
      #scales = np.maximum(0, self._radius_param + self._radius_variation * variation / 256)
      aux = self._radius_aux/100
      variation = LINEAR_DISTRIBUTION[self._rnd_radii_idxs] * (1-aux) + INVERSE_DISTRIBUTION[self._rnd_radii_idxs] * aux
      scales = np.maximum(0, self._radius_param + self._radius_variation * variation / 256 )
      rots = self._theta + self._rnd_thetas * self._theta_variation
      self._xform = []
      for i in range(self._quantity):
        self._xform.append(
          QtGui.QTransform.fromTranslate(xs[i], ys[i])
          .scale(scales[i],scales[i])
          .rotateRadians(rots[i])
        )

  def computeLightMetrics(self):
    # Compute a simple metric of how well lit each shape is.
    self.computeXforms()

    light_source_xy = self.scene().light.pos()
    zz = QtCore.QPointF(0,0)
    dxs = np.zeros(self._max_quantity)
    dys = np.zeros(self._max_quantity)
    for i in range(self._quantity):
      delta = self._xform[i].map(zz) - light_source_xy
      dxs[i] = delta.x()
      dys[i] = delta.y()
    dists = np.hypot(dxs, dys)
    dirs = np.arctan2(dys, dxs)
    self._lightDists = dists[:self._quantity]

    light_source_inner_radius = self.scene().light.innerRadius()
    light_source_outer_radius = self.scene().light.outerRadius()
    fade_dist = abs(light_source_outer_radius - light_source_inner_radius)
    #self._illuminances = 1 - np.minimum( np.maximum(0.0, dists - light_source_inner_radius) / light_source_outer_radius, 1.0)
    self._illuminances = 1 - np.minimum( np.maximum(0.0, dists - light_source_inner_radius) / (fade_dist+1), 1.0)

    self._shadow_dxs = dxs / self._shadow_divisor
    self._shadow_dys = dys / self._shadow_divisor

  def computeColor(self):
    if self._clamped_hues is None or len(self._clamped_hues) < self._quantity:
      self._clamped_hues = ((self._hue_variation * (self._rnd_hues - .5) + self._hue) % 360) / 360
      self._color = None
    if self._clamped_saturations is None or len(self._clamped_saturations) < self._quantity:
      #self._clamped_saturations = (
      #  (1 - self._rnd_saturations * (1 - self._min_saturation / 100)) * self._max_saturation / 100
      #)
      if self._min_saturation <= self._max_saturation:
        satrange = (self._max_saturation - self._min_saturation) / 100
        self._clamped_saturations = self._min_saturation/100 + self._rnd_saturations * satrange
      else:
        avg = (self._min_saturation + self._max_saturation) / 200
        self._clamped_saturations = avg + self._rnd_saturations * 0
      self._color = None
    if self._clamped_lightness is None or len(self._clamped_lightness) < self._quantity:
      self.computeXforms()
      self.computeLightMetrics()
      if self._min_lightness <= self._max_lightness:
        lightnessrange = (self._max_lightness - self._min_lightness) / 100
        clamped_lightness = (self._min_lightness/100 + self._rnd_lightnesses * lightnessrange)# * self._illuminances
      else:
        avg = (self._min_lightness + self._max_lightness) / 200
        clamped_lightness = (avg + self._rnd_lightnesses * 0)# * self._illuminances
      self._clamped_lightness = clamped_lightness[:self._quantity]
      self._color = None
    if self._color is None or len(self._color) < self._quantity:
      light_color = self.scene().light.color()
      (r,g,b) = (light_color.redF(), light_color.greenF(), light_color.blueF())
      self._color = []
      for i in range(self._quantity):
        c = QtGui.QColor.fromHslF( self._clamped_hues[i]
                                 , self._clamped_saturations[i]
                                 , self._clamped_lightness[i] ).getRgbF()
        self._color.append( QtGui.QColor.fromRgbF(c[0]*r*self._illuminances[i], c[1]*g*self._illuminances[i], c[2]*b*self._illuminances[i]) )

  def computeShapePicks(self):
    'Regenerate the list used to randomly pick shapes.'
    self._shape_picks = []
    for shp in self._shapes:
      self._shape_picks.extend(list(shp for i in range(shp.qty)))
    if not self._shape_picks:
      self._shape_picks.append(self._shapes[3])

  def computeXformedShapes(self):
    'Recompute transformation of each shape'
    if self._xformed_shapes is None or len(self._xformed_shapes) < self._quantity:
      self.computeXforms()
      self.computeShapePicks()
      npicks = len(self._shape_picks)
      self._xformed_shapes = []
      for i in range(self._quantity):
        shp = self._shape_picks[ int(self._rnd_shapes[i] * npicks) ]
        self._xformed_shapes.append( shp.transformed(self._xform[i]) )

  def computeGradient(self):
    if self._fill_gradients is None or len(self._fill_gradients) < self._quantity:
      #t0 = time.perf_counter()
      self.computeColor()
      self.computeXforms()
      self._fill_gradients = []
      p0 = QtCore.QPointF(-1,0)
      p1 = QtCore.QPointF( 1,0)
      for i in range(self._quantity):
        xfmap = self._xform[i].map
        # QLinearGradient takes the pixel coordinates of the start and end stops.
        g = QtGui.QLinearGradient( xfmap(p0), xfmap(p1) )
        c1 = QtGui.QColor(self._color[i])
        a1 = 255 - int((255-self._min_opacity) * self._rnd_opacities[i])
        c1.setAlpha(a1)
        g.setColorAt(0.0, c1)
        c2 = QtGui.QColor(self._color[i])
        a2 = min(a1, self._gradient_opacity)
        c2.setAlpha(a2)
        g.setColorAt(1.0, c2)
        self._fill_gradients.append(g)
      #print('computeGradient {:.2f} hz'.format(1/(time.perf_counter() - t0)))

  def computeSpecular(self):
    if self._specularGradient is None or len(self._specularGradient) < self._quantity or self._bevelGradient is None or len(self._bevelGradient) < self._quantity:
      self.computeXforms()
      self._specularGradient = []
      self._bevelGradient = []
      light_source_xy = self.scene().light.pos()
      light_color = self.scene().light.color()
      invisible_light = QtGui.QColor(light_color)
      invisible_light.setAlpha(0)
      for i in range(self._quantity):
        lightDist = self._lightDists[i]     # distance to center of shape
        r = self._xformed_shapes[i]._radius
        L = self._illuminances[i] * self._specularBrightness

        # Compute specular gloss
        prime_gradius = max(lightDist,r) + (r * (self._specularDepth-50)/100)
        gradius_radius = r * (100 - self._specularSharpness) / 100
        inner_gradius = prime_gradius - gradius_radius
        outer_gradius = prime_gradius + gradius_radius
        g = QtGui.QRadialGradient(light_source_xy, outer_gradius, light_source_xy, inner_gradius) # smooth
        #g = QtGui.QRadialGradient(light_source_xy, max(lightDist,r), light_source_xy, max(lightDist,r)-2) # sharp
        '''
          Reading the Qt source code, it appears that the default ColorInterpolation mode causes
          at least 50 stops to be generated for any gradient whose alpha value isn't constant!
          PyQt doesn't export access to QGradient.setInterpolationMode!
          Also, this appears to somehow be what triggers rendering as raster images embedded inside SVG!
        '''
        #g.setInterpolationMode(QtGui.QGradient.ComponentInterpolation)
        c1 = QtGui.QColor(light_color)
        c1.setAlpha(L)
        g.setColorAt(0.0, c1)
        g.setColorAt(1.0, invisible_light)
        self._specularGradient.append(g)

        # Compute (specular) bevel gradient
        g2 = QtGui.QRadialGradient(light_source_xy, max(lightDist+r,r), light_source_xy, max(lightDist,r)-r) # smooth
        c2 = QtGui.QColor(light_color)
        c2.setAlpha(L)
        g2.setColorAt(0.0, c2)
        c0 = QtGui.QColor(self._color[i])
        c0.setAlpha(0)
        g2.setColorAt(0.5, c0)
        g2.setColorAt(1.0, QtGui.QColor(0,0,0,L))
        self._bevelGradient.append(g2)

  def paint(self, painter, option, widget=0):
    fast = self._pressed_render and self._last_full_render_time > .1
    faster = fast and self._last_full_render_time > .5

    self.computeXformedShapes()
    self.computeColor()
    if not fast:
      self.computeGradient()
      if self._specularBrightness or self._bevelThickness:
        self.computeSpecular()
    painter.setClipRect(self._boundingRect)  # To avoid needing clipping, be honest about actual boundingRect

    shadow = QtGui.QColor(0,0,0,self._shadow_opacity)

    if self._edgeThickness == 0:
      pen = QtCore.Qt.NoPen
    elif faster:
      pen = QtGui.QPen(QtCore.Qt.black, 1)
    else:
      pen = QtGui.QPen(QtCore.Qt.black, self._edgeThickness)
    painter.setPen(pen)

    #if fast:
    #  #painter.setBrush(QtCore.Qt.NoBrush)
    #  painter.setBrush(QtCore.Qt.gray)

    t0 = time.perf_counter()
    for i in range(self._quantity):
      if self._shadow_opacity:
        painter.setPen(QtCore.Qt.NoPen)
        if fast:
          painter.setBrush(shadow)
        else:
          a1 = 255 - int((255-self._min_opacity) * self._rnd_opacities[i])
          painter.setBrush(QtGui.QColor(0,0,0,self._shadow_opacity * a1 / 255))
        self._xformed_shapes[i].paintShadow(painter, self._shadow_dxs[i], self._shadow_dys[i])
        painter.setPen(pen)
      #if faster:
      #  brush = QtCore.Qt.NoBrush
      if fast or (self._min_opacity == 255 and self._gradient_opacity == 255):
        brush = QtGui.QColor(self._color[i])
        brush.setAlpha(255)
      else:
        brush = self._fill_gradients[i]
      painter.setBrush(brush)
      self._xformed_shapes[i].paint(painter)
      if not fast and self._specularBrightness:
        # Paint specular highlight
        painter.setBrush(self._specularGradient[i])
        self._xformed_shapes[i].paint(painter)
      if not fast and self._bevelThickness:
        # Paint bevel
        # The bevel is drawn translucently on top of the opaque black edge,
        # so it can be hard to notice that it is on top.
        path = QtGui.QPainterPath()
        self._xformed_shapes[i].addToPath(path)
        path.closeSubpath()
        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(self._bevelThickness*2)
        strokedPath = stroker.createStroke(path)#.simplified()
        innerStrokedPath = strokedPath.intersected(path)
        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(self._bevelGradient[i])
        #painter.setClipPath(path)
        painter.drawPath(innerStrokedPath)
        #painter.setClipRect(self._boundingRect)

    dt = time.perf_counter() - t0
    print('paint {:.3f} s = {:.2f} hz'.format(dt, 1.0/dt))
    if not (fast or faster):
      self._last_full_render_time = dt

  def startPressedRender(self):
    self._pressed_render = True
  def stopPressedRender(self):
    self._pressed_render = False
    self.update()

  def addSliderTo(self, layout, name, lo, hi, value, setter, tickInt=None):
    label, slider = addSliderTo(layout, name, lo, hi, value, setter, tickInt)
    slider.sliderPressed.connect(self.startPressedRender)
    slider.sliderReleased.connect(self.stopPressedRender)
    return (label, slider)

  def addWidgetsTo(self, layout):
    self.addSliderTo(layout, 'Quantity', 1, self._max_quantity, self._quantity, self.setQuantity)
    setter = lambda shp: lambda value: self.setShapeQuantity(shp, value)  # curry setShapeQuantity
    for i in range(len(self._shapes)):
      self.addSliderTo(layout, self._shapes[i]._name, 0, 100, self._shapes[i].qty, setter(self._shapes[i]))
    self.addSliderTo(layout, 'Positional Randomness', 0, 1000, self._posRandomness, self.setPosRandomness)
    self.addSliderTo(layout, 'Rotation (degrees)', 0, 360, int(self._theta*360/math.pi), self.setTheta, tickInt=15)
    self.addSliderTo(layout, 'Rotation Variation', 0, 360, int(self._theta_variation*360/math.pi), self.setThetaVariation, tickInt=15)
    self.addSliderTo(layout, 'Radius (px, circumscribed)', 1, 512, self._radius_param, self.setRadius)
    self.addSliderTo(layout, 'Radius Variation', 0, 256, self._radius_variation, self.setRadiusVariation)
    self.addSliderTo(layout, 'Radius Power', 0, 100, self._radius_aux, self.setRadiusAux)
    self.addSliderTo(layout, 'Edge Thickness (px)', 0, self._MAX_BORDER, self._edgeThickness, self.setEdgeThickness)
    self.addSliderTo(layout, 'Hue', 0, 360, self._hue, self.setHue, tickInt=30)
    self.addSliderTo(layout, 'Hue Variation', 0, 360, self._hue_variation, self.setHueVariation, tickInt=30)
    self.addSliderTo(layout, 'Minimum Saturation', 0, 100, self._min_saturation, self.setMinSaturation, tickInt=10)
    self.addSliderTo(layout, 'Maximum Saturation', 0, 100, self._max_saturation, self.setMaxSaturation, tickInt=10)
    self.addSliderTo(layout, 'Minimum Lightness', 0, 100, self._min_lightness, self.setMinLightness, tickInt=10)
    self.addSliderTo(layout, 'Maximum Lightness', 0, 100, self._max_lightness, self.setMaxLightness, tickInt=10)
    self.addSliderTo(layout, 'Minimum Opacity', 0, 255, self._min_opacity, self.setMinOpacity, tickInt=16)
    self.addSliderTo(layout, 'Gradient Opacity', 0, 255, self._gradient_opacity, self.setGradientOpacity, tickInt=16)
    self.addSliderTo(layout, 'Shadow Opacity', 0, 255, self._shadow_opacity, self.setShadowOpacity)
    self.addSliderTo(layout, 'Shadow Closeness', 1, 1024, self._shadow_divisor, self.setShadowDivisor)
    #chkbox = QtWidgets.QCheckBox('Specular')
    #chkbox.setCheckState((QtCore.Qt.Unchecked,QtCore.Qt.Checked)[self._specular])
    #layout.addWidget(chkbox)
    #chkbox.stateChanged.connect(self.setSpecular)
    self.addSliderTo(layout, 'Specular Brightness', 0, 255, self._specularBrightness, self.setSpecularBrightness)
    self.addSliderTo(layout, 'Specular Sharpness', 1, 100, self._specularSharpness, self.setSpecularSharpness)
    self.addSliderTo(layout, 'Specular Depth', 1, 100, self._specularDepth, self.setSpecularDepth)
    self.addSliderTo(layout, 'Bevel Thickness', 0, 64, self._bevelThickness, self.setBevelThickness)
    
    #for i in range(32):
    #  layout.addWidget(QtWidgets.QSlider(QtCore.Qt.Horizontal))
