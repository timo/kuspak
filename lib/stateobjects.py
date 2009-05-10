from gamestate import StateObject, stateVars, prescribeType, Link

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
    return "<ShipState at %s, team %d, id %d>" % (self.position, self.team, self.id)

  def tick(self, dt):
    pass

  def collide(self, other, vec):
    pass

  def command(self, cmd):
    pass


class Item(StateObject):
  typename = "it"
  def __init__(self, statedata = None):
    StateObject.__init__(self)
    with stateVars(self):
      self.name = ""

    if statedata:
      self.deserialize(statedata)
