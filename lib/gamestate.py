from __future__ import with_statement
import struct
from math import pi, sin, cos, sqrt
from random import random
import copy

class NotFound(Exception):
  pass

# randomly bend a vector around
def scatter(lis, amount = 1):
  return lis
  #return [random() * amount - amount / 2 + lisi for lisi in lis]

# store the serialization data, so that it doesn't have to be regenerated on
# each gamestate objects init.
serializeKnowledgeBase =  {}
# store, what short name each object has
typeKnowledgeBase = {}

# this object can be used with the "with" statement to turn on the automatic
# serialization registration magic of StateObject
class stateVars:
  def __init__(self, other):
    global serializeKnowledgeBase
    if type(other) in serializeKnowledgeBase:
      self.knowndata = serializeKnowledgeBase[type(other)]
    if other.typename not in typeKnowledgeBase:
      typeKnowledgeBase[other.typename] = type(other)
    self.so = other

  def __enter__(self):
    if "knowndata" not in dir(self):
      self.so.statevars_enabled = True

  def __exit__(self, a, b, c):
    global serializeKnowledgeBase
    if "knowndata" in dir(self):
      self.so.statevars = self.knowndata["statevars"]
      self.so.statevars_format = self.knowndata["statevars_format"]
      self.so.tuples = self.knowndata["tuples"]
      self.so.links = self.knowndata["links"]
    else:
      del self.so.statevars_enabled
      d = {"statevars": self.so.statevars,
           "statevars_format": self.so.statevars_format,
           "tuples": self.so.tuples,
           "links": self.so.links,
           "len": struct.calcsize(self.so.statevars_format)}
      serializeKnowledgeBase[type(self.so)] = d

# using this object with the "with" statement, the type of the included vars
# can be predetermined, instead of letting the magic find it out.
# this can be used to use smaller types (b instead of i) for saving space.
class prescribedType:
  def __init__(self, other, type):
    self.so = other
    self.typ = type

    try:
      self.pretyp = self.so.statevars_pretype
    except: pass

  def __enter__(self):
    self.so.statevars_pretype = self.typ

  def __exit__(self, a, b, c):
    del self.so.statevars_pretype
    try:
      self.so.statevars_pretype = self.pretyp
    except: pass

# the GameState object holds all objects in the state and can serialize or
# deserialize itself. it can also accept input commands and relay it to the
# objects that are supposed to get it.
class GameState:
  def __init__(self, data = None):
    self.objects = []
    self.tickinterval = 50 # in miliseconds
    self.clock = 0
    self.nextNewId = 0
    self.links = []
    if data:
      self.deserialize(data)

    self.spawns = []

  def copy(self):
    return copy.deepcopy(self)

  def tick(self):
    # advance the clock and let all objects to their business.
    self.spawns = []
    self.clock += self.tickinterval
    for o in self.objects:
      o.tick(self.tickinterval)
      if o.die:
        self.objects.remove(o)

    self.doCollisions(self.tickinterval)

  def spawn(self, object, obvious=False):
    # spawn the object into the state and bind it
    if not obvious or object.id == 0:
      object.id = self.nextNewId
      self.nextNewId += 1
    else:
      print "spawning with forced ID:", object.id
    self.objects.append(object.bind(self))
    if not obvious:
      self.spawns.append(object)
    print "spawned:", `object`

  def registerLink(self, link):
    self.links.append(link)

  def serialize(self):
    # serialize the whole gamestate
    data = struct.pack("!i", self.clock)
    data = data + "".join(obj.typename + obj.serialize() for obj in self.objects)
    return data

  def getSerializeType(self, dataFragment):
    type, data = dataFragment[:2], dataFragment[2:]
    print `dataFragment`, `type`, `data`
    if type in typeKnowledgeBase:
      obj = typeKnowledgeBase[type]
    else:
      print "got unknown type:", `type`, `typeKnowledgeBase`

    return obj

  def getSerializedLen(self, dataFragment):
    if isinstance(dataFragment, str):
      try:
        return serializeKnowledgeBase[self.getSerializeType(dataFragment)]["len"]
      except IndexError:
        return struct.calcsize(self.getSerializeType(dataFragment).statevars_format)
    else:
      return struct.calcsize(dataFragment.statevars_format)

  def deserialize(self, data):
    # deserialize the data

    # the fact, that objects gets cleared, is the reason for the StateObjectProxy
    # objects to exist
    self.objects = []
    self.work = []
    odata = data
    self.clock, data = struct.unpack("!i", data[:4])[0], data [4:]
    while len(data) > 0:
      print "string is:", `data`
      obj = self.getSerializeType(data)

      # cut the next N bytes out of the data.
      if obj == LinkList:
        # the first integer of the thingie is the number of items in the list,
        # so we add 4 bytes for the first integer and 4 for each following one.
        print struct.unpack("!2i", data[2:10])
        objlen = struct.unpack("!2i", data[2:10])[1] * 4 + 8
      else:
        objlen = self.getSerializedLen(data)
      data = data[2:]
      objdat, data = data[:objlen], data[objlen:]

      obj = obj()

      obj.bind(self)
      try:
        print "deserializing a", `obj`, "from", `objdat`
        obj.deserialize(objdat)
      except:
        print "could not deserialize", `odata`, "- chunk:", `objdat`
        raise

      self.objects.append(obj)
      try:
        self.work.extend(obj.work)
      except: pass

    for work in self.work:
      work()
    self.work = []

    for l in self.links:
      l.proxy_update()

  def getById(self, id):
    for obj in self.objects:
      if obj.id == id:
        return obj

    if id == -1:
      return EmptyLinkTarget()
    raise NotFound(id)

  def doCollisions(self, dt):
    for a in self.objects:
      for b in self.objects:
        if a == b: continue

        dv = [a.position[i] - b.position[i] for i in range(2)]
        lns = dv[0] * dv[0] + dv[1] * dv[1]

        if lns < (a.size + b.size) ** 2:
          a.collide(b, dv)
          b.collide(a, dv)

  def control(self, commands):
    # relays control messages to the objects.
    for id, cmd in commands:
      self.getById(id).command(cmd)

  def __repr__(self):
    return "<GameState at clock %d containing: %s>" % (self.clock, `self.objects`)

# the base class for a State Object, that also implements the serialization
# black magic.
class StateObject(object):
  typename = "ab"#stract
  mass = 0
  def __init__(self):
    self.state = None
    self.statevars = ["id"]
    self.tuples = []
    self.links = []
    self.statevars_format = "!i"
    self.die = False
    self.id = 0

  def __setattr__(self, attr, value):

    def addAttr(attr, value):
      self.statevars.append(attr)
      try: self.statevars_format += self.statevars_pretype
      except AttributeError:
        if type(value) == int:
          self.statevars_format += "i"
        elif type(value) == float:
          self.statevars_format += "d"
        else:
          print "unknown serialization type:"
          print attr, value, type(value)
      object.__setattr__(self, attr, value)

    try:
      # only when the magic is turned on and only if the attribute is relevant,
      # shall we cause magic to happen.
      if self.statevars_enabled and not attr.startswith("statevars"):
        if type(value) == list:
          for i in range(len(value)):
            addAttr("_%s_%d" % (attr, i), value[i])
          self.tuples.append(attr)
          # don't forget to add the actual tuple value for internal usage.
          raise Exception
        elif isinstance(value, GameState) or isinstance(value, Link):
          addAttr("_%s_linkid" % attr, value.id)
          self.links.append(attr)
          raise Exception
        else:
          addAttr(attr, value)
      else:
        # this is usually called when statevars_enabled is not set.
        raise Exception

    except Exception:
      object.__setattr__(self, attr, value)

  # the base class does nothing by itself.
  def tick(self, dt):
    pass

  def bind(self, state):
    self.state = state
    return self

  # since the struct module cannot handle lists, we do it instead
  def pre_serialize(self):
    for tup in self.tuples:
      thetup = object.__getattribute__(self, tup)
      for i in range(len(thetup)):
        object.__setattr__(self, "_%s_%d" % (tup, i), thetup[i])
    for link in self.links:
      theobj = object.__getattribute__(self, link)
      object.__setattr__(self, "_%s_linkid" % link, theobj.id)

  def post_deserialize(self):
    for tup in self.tuples:
      val = [object.__getattribute__(self, "_%s_%d" % (tup, i)) \
               for i in range(len( object.__getattribute__(self, tup) )) \
            ]
      object.__setattr__(self, tup, val)
    for link in self.links:
      val = object.__getattribute__(self, "_%s_linkid" % link)
      try:
        object.__setattr__(self, link, Link(self.state.getById(val)))
      # if we don't have a state bound yet or if the other object has not yet
      # been deserialized, we let the gamestate do the setup later
      except (NotFound, AttributeError): 
        fun = lambda: object.__setattr__(self, link, Link(self.state.getById(val)))
        try:
          self.work.append(fun)
        except AttributeError:
          self.work = [fun]

  # this function can be used to set up data from the games "database"
  # items, for example.
  def translateSerializedData(self):
    pass

  def serialize(self):
    self.pre_serialize()
    return struct.pack(self.statevars_format, *[getattr(self, varname) for varname in self.statevars])

  def collide(self, other, vec):
    pass

  def deserialize(self, data):
    try:
      vals = struct.unpack(self.statevars_format, data)
    except:
      print "error while unpacking a", self.typename, `self`
      raise
    for k, v in zip(self.statevars, vals):
      setattr(self, k, v)
    
    self.post_deserialize()

    self.translateSerializedData()

    return self

  def command(self, cmd):
    pass

  # return a proxy object that points at us.
  def getProxy(self, history):
    return StateObjectProxy(self, history)

# the proxy object uses the gamestate history object in order to always point
# at the current instance of the object it was generated from.
class StateObjectProxy(object):
  def __init__(self, obj, history):
    if isinstance(obj, StateObject) or isinstance(obj,StateObjectProxy):
      self.proxy_id = obj.id
      self.proxy_objref = obj
    else:
      raise Exception("Proxy objects must be objects.")
    history.registerProxy(self)

  def proxy_set(self, obj):
    self.proxy_id = obj.id
    self.proxy_objref = obj

  def proxy_update(self, gamestate):
    self.proxy_objref = gamestate.getById(self.proxy_id)
  
  # all attributes that do not have anything to do with the proxy will be
  # proxied to the StateObject
  def __getattr__(self, attr):
    if attr.startswith("proxy_"):
      return object.__getattribute__(self, attr)
    else:
      return self.proxy_objref.__getattribute__(attr)

  def __setattr__(self, attr, value):
    if attr.startswith("proxy_"):
      object.__setattr__(self, attr, value)
    else:
      self.objref.__setattr__(attr, value)

  def __repr__(self):
    return "<Proxy of (%d): %s>" % (self.proxy_id, `self.proxy_objref`)

# the Link class is basically like a StateObjectProxy, but limited to
# one gamestate, rather than the history. it is managed by the GameState.

class StateStub:
  def getById(self, id):
    return EmptyLinkTarget()
  
  def registerLink(self,link):
    pass

class EmptyLinkTarget(object):
  def __init__(self):
    self.id = -1
    self.state = StateStub()

class Link(StateObjectProxy):
  def __init__(self, obj = None):
    if obj:
      self.proxy_id = obj.id
      self.proxy_objref = obj
      obj.state.registerLink(self)
    else:
      self.proxy_objref = EmptyLinkTarget()
      self.proxy_id = None

  def proxy_update(self):
    self.proxy_objref = self.proxy_objref.state.getById(self.proxy_id)

  def __repr__(self):
    if isinstance(self.proxy_objref, EmptyLinkTarget):
      return "|-> None <-|"
    else:
      return "|-> (%d): %s <-|" % (self.proxy_id, `self.proxy_objref`)

class LinkList(StateObject):
  typename = "ll"
  def __init__(self, statedata = None):
    self.links = []
    self.work = []
    self.state = None
    self.id = 0

    if statedata:
      self.deserialize(statedata)

  def serialize(self):
    data = struct.pack("!2i", self.id, len(self.links))
    data += struct.pack(*(["!" + str(len(self.links)) + "i"] + [link.id for link in self.links]))
    return data

  def deserialize(self, data):
    self.id, amount = struct.unpack("!2i", data[:8])
    data = data[8:]
    del self.links[:]
    while data:
      chunk, data = data[:4], data[4:]
      print "adding", `chunk`
      self.work.append(lambda: self.links.append(Link(self.state.getById(struct.unpack("!i", chunk)[0]))))

  def pre_serialize(self): pass
  def post_deserialize(self): pass

  def assureLink(self, v):
    if isinstance(v, Link):
      return v
    else:
      return Link(v)

  def __setitem__(self, x, v):
    self.links[x] = self.assureLink(v)

  def __getitem__(self, x): return self.links[x]
  def __delitem__(self, x): del self.links[x]
  def append(self, v):  self.links.append(self.assureLink(v))

  def __repr__(self):
    return "<LinkList of %s>" % (`self.links`)

typeKnowledgeBase["ll"] = LinkList

# the StateHistory object saves a backlog of GameState objects in order to
# interpret input data at the time it happened, even if received with a
# latency. this allows for fair treatment of all players, except for cheaters,
# who could easily abuse this system.
class StateHistory:
  def __init__(self, initialState):
    self.gsh = [initialState]
    self.inputs = [[]]
    self.maxstates = 20
    self.firstDirty = 0

    self.proxies = []
 
  def __getitem__(self, i):
    return self.gsh.__getitem__(i)

  def registerProxy(self, po):
    self.proxies.append(po)

  def updateProxies(self):
    for po in self.proxies:
      po.proxy_update(self.gsh[-1])

  def byClock(self, clock):
    found = 0
    for i in range(len(self.gsh)):
      if self.gsh[i].clock == clock:
        found = i
        break
    return found

  def inject(self, id, command, clock = None):
    if clock:
      found = self.byClock(clock)
    else:
      found = len(self.gsh) - 1

    self.firstDirty = found
    self.inputs[found].append((id, command))

  def injectObject(self, object, clock = None):
    if clock:
      found = self.byClock(clock)
    else:
      found = len(self.gsh) -1

    self.firstDirty = found
    self.gsh[found].spawn(object, True)

  def updateObject(self, id, data, clock = None):
    if clock:
      found = self.byClock(clock)
    else:
      found = len(self.gsh) -1

    self.firstDirty = found
    self.gsh[found].getById(id).deserialize(data)

  def apply(self):
    for i in range(self.firstDirty + 1, len(self.gsh)):
      # this trick allows us to keep the gamestates
      # instead of regenerating them all the time
      self.gsh[i] = self.gsh[i - 1]
      self.gsh[i - 1] = self.gsh[i - 1].copy()
      self.gsh[i].control(self.inputs[i - 1])
      self.gsh[i].tick()

    if self.firstDirty + 1 - len(self.gsh):
      self.updateProxies()
    self.firstDirty = len(self.gsh)

    if len(self.gsh) < self.maxstates:
      self.gsh = self.gsh[:-1] + [self.gsh[-1].copy(), self.gsh[-1]]
      self.inputs.append([])
    else:
      # again: make sure to keep the gamestate at the top intact!
      self.gsh = self.gsh[1:-1] + [self.gsh[-1].copy(), self.gsh[-1]]
      self.inputs = self.inputs[1:] + [[]]

    if self.inputs[-2]:
      self.gsh[-1].control(self.inputs[-2])
    self.gsh[-1].tick()
