from __future__ import with_statement
from gamestate import StateObject, stateVars, prescribedType, Link
from stuffdb import itemDb

class PlayerState(StateObject):
  typename = "pc"
  def __init__(self, data = None):
    StateObject.__init__(self)
    with stateVars(self):
      self.position = [0.0, 0.0]
      self.alignment = 0.0         # from 0 to 1
      self.health = 20.0
      self.maxHealth = 20
      self.magic = 10.0
      self.maxMagic = 10
      self.item = Link()
      with prescribedType(self, "b"):
        self.team = 0

    if data:
      self.deserialize(data)

  def __repr__(self):
    return "<PlayerState H%f/%d M%f/%d holding %s>" % (self.health, self.maxHealth, self.magic, self.maxMagic, self.item.__repr__())

  def tick(self, dt):
    pass

  def collide(self, other, vec):
    pass

  def command(self, cmd):
    pass

class ItemState(StateObject):
  typename = "it"
  def __init__(self, statedata = None):
    StateObject.__init__(self)
    with stateVars(self):
      self.type = 0
      self.grantType = 0
      self.mod = 0

    if statedata:
      self.deserialize(statedata)
    else:
      self.translateSerializedData()
  
  def translateSerializedData(self):
    itemDb.initItem(self)

class IntrinsicState(StateObject):
  typename = "in"
  def __init__(self, statedata = None):
    StateObject.__init__(self)
    with stateVars(self):
      self.type = 0
      self.lifetimeLeft = -1

    if statedata:
      self.deserialize(statedata)
    else:
      self.translateSerializedData()

  def tick(self, dt):
    self.lifetimeLeft -= dt
    if self.lifetimeLeft < 0:
      self.die = True
