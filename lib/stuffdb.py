class objectdb(object):
  def __init__(self):
    self.db = {}

  def register(self, cls, typeId):
    self.db[typeId] = cls
    return cls

  def initItem(self, obj):
    self.db[obj.type].assimilate(item)

itemDb = objectdb()
intrinsicDb = objectdb()

class Item(object):
  drink = None
  equip = None
  meleeDamage = 1
  def assimilate(self, other):
    other.melee = self.melee
    other.drink = self.drink
    other.equip = self.equip
  
  def melee(self, user):
    dmg = 0
    if user.hasIntrinsic(self.meleeIntrinsic):
      dmg += 1
    return self.meleeDamage + dmg

class Weapon(Item):
  def __init__(self):
    pass

def basicIntrinsic(intName):
  class myIntrinsic(object):
    name = intName
    lifetime = None
  intrinsicDb.register(myIntrinsic, len(intrinsicDb.db))

basicIntrinsic("Fire Resistance")
basicIntrinsic("Cold Resistance")
basicIntrinsic("Acid Resistance")
basicIntrinsic("Spark Resistance")
basicIntrinsic("Quick")
basicIntrinsic("Alert")
