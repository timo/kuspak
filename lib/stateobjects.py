from gamestate import StateObject, stateVars, prescribeType

class PlayerState(StateObject):
  typename = "sp"
  mass = 1
  def __init__(self, data = None):
    StateObject.__init__(self)
    with stateVars(self):
      self.color = [random(), random(), random()]
      self.position = [0.0, 0.0]
      self.speed = [0.0, 0.0]        # in units per milisecond
      self.alignment = 0.0         # from 0 to 1
      self.timeToReload = 0      # in miliseconds
      self.reloadInterval = 500
      self.maxShield = 7500
      self.shield = 7500
      self.hull = 10000
      with prescribedType(self, "b"):
        self.team = 0

    self.size = 2
    self.firing = 0
    self.turning = 0
    self.thrust = 0

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
