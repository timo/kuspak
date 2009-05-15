class objectdb(object):
  def __init__(self):
    db = {}

  def register(self, cls, typeId):
    self.db[typeId] = cls
    return cls

  def initItem(self, obj):
    self.db[obj.type].assimilate(item)

itemDb = objectdb()

class Item(object):
  def assimilate(self, other):
    other.melee = self.melee
    other.thrown = self.thrown
    other.thrownDistance =
  
  def melee(self, user):
    

class Weapon(Item):
  def __init__(self):
    
  
