from lib.gamestate import *
from lib.stateobjects import *

def run():
  gs = GameState()
  pl = PlayerState()
  gs.spawn(pl)

  pli = LinkList()
  gs.spawn(pli)
  pl.items.proxy_set(pli)

  for i in range(5):
    it = ItemState()
    gs.spawn(it)
    pl.items.append(it)

  gstr = gs.serialize()
  print `gstr`

  gs2 = GameState(gstr)

  print `gs`
  print `gs2`

run()
