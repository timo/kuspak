from __future__ import with_statement
from gamestate import GameState, StateObject, stateVars, prescribedType, Link, LinkList, typeKnowledgeBase
from stuffdb import itemDb
from struct import unpack
from math import *

def playerStartup(name, state):
  plr = state.spawn(PlayerState(state))
  plr.items.append(state.spawn(ItemState(state)))
  return plr

class PlayerState(StateObject):
  typename = "pc"
  def __init__(self, state, data = None):
    StateObject.__init__(self, state)
    with stateVars(self):
      self.position = [0.0, 0.0]
      self.target = [0.0, 0.0]
      self.alignment = 0.0         # from 0 to 1
      self.health = 20.0
      self.maxHealth = 20
      self.magic = 10.0
      self.maxMagic = 10
      self.items = Link(state.spawn(LinkList(state)))
      self.intrins = Link(state.spawn(LinkList(state)))
      with prescribedType(self, "b"):
        self.team = 0

    if data:
      self.deserialize(data)

  def __repr__(self):
    return "<PlayerState at (%d, %d) H%f/%d M%f/%d holding %s with intrinsics %s>" % (self.position[0], self.position[1], self.health, self.maxHealth, self.magic, self.maxMagic, `self.items`, `self.intrins`)

  def tick(self, dt):
    dv = [self.target[i] - self.position[i] for i in range(2)]
    if not (abs(dv[0]) <= 0.1 and abs(dv[1]) <= 0.1):
      ln = sqrt(dv[0] * dv[0] + dv[1] * dv[1])
      if ln < dt * 0.01:
        self.position = list(self.target)
      else:
        self.position = [self.position[i] + (dv[i] / ln) * dt * 0.01 for i in range(2)]

  def collide(self, other, vec):
    pass

  def posesses(self, other):
    for it in self.items:
      if it.id == other:
        return True

    return False

  def command(self, cmd):
    if cmd[0] == "r":   # read (a scroll or book)
      if self.posesses(unpack("!i", cmd[1:])[0]):
        print "reading it."
      else:
        print "can't read something that is not in your inventory"
    elif cmd[0] == "t": # target (for movement and attacks)
      self.target = unpack("!dd", cmd[1:])
    #elif cmd[0] == "e": # equip an item at a slot
    #elif cmd[0] == "u": # unequip an item from a slot
    #elif cmd[0] == "q": # quaff a potion
    #elif cmd[0] == "c": # eat (citka) some food

PlayerState(GameState())

class ItemState(StateObject):
  typename = "it"
  def __init__(self, state, statedata = None):
    StateObject.__init__(self, state)
    with stateVars(self):
      self.type = 0
      self.grantType = 0
      self.mod = 0

    if statedata:
      self.deserialize(statedata)
    else:
      self.translateSerializedData()
  
  def translateSerializedData(self):
    pass
    #itemDb.initItem(self)

ItemState(GameState())

class IntrinsicState(StateObject):
  typename = "in"
  def __init__(self, state, statedata = None):
    StateObject.__init__(self, state)
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

IntrinsicState(GameState())
