class itemdb(object):
  def __init__(self):
    db = {}

  def register(self, fun, typeId):
    self.db[typeId] = fun
    return fun

  def initItem(self, item):
    self.db[item.itemType](item)

itemDb = itemdb()

itemDb.register(1)
def setupSword(item):
  
