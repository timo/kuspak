from __future__ import with_statement
import gamestate
from OpenGL.GL import *
from with_opengl import glPrimitive, glMatrix
from math import pi, sin, cos, sqrt, log
from stateobjects import *
from res import Texture

import main
from font import Text

import network

def frange(start, end, step):
  curr = start
  while curr < end:
    yield curr
    curr += step
  yield end

def renderGameGrid(player):
  with glMatrix():
    #glTranslatef(player.position[0], player.position[1], 0)
    Texture("floor").bind()
    with glPrimitive(GL_QUADS):
      glTexCoord2f(0, 0)
      glVertex2f(-100, -100)
      glTexCoord2f(100, 0)
      glVertex2f(100, -100)
      glTexCoord2f(100, 100)
      glVertex2f(100, 100)
      glTexCoord2f(0, 100)
      glVertex2f(-100, 100)

def renderWholeState(state):
  for obj in state.objects:
    for cls, met in methodMap.items():
      if isinstance(obj, cls):
        with glMatrix():
          met(obj)

playerflags = {}

def renderPlayer(player):
  glTranslate(*player.position + [0])
  glTranslate(-0.5, 0, 1)
  glRotatef(90, -1, 0, 0)
  with glMatrix():
    Texture("person").bind()
    with glPrimitive(GL_QUADS):
      glTexCoord2f(0, 0)
      glVertex2f(0, 0)
      glTexCoord2f(1, 0)
      glVertex2f(1, 0)
      glTexCoord2f(1, 1)
      glVertex2f(1, 1)
      glTexCoord2f(0, 1)
      glVertex2f(0, 1)

  tryfind = [c for c in network.clients.values() if c.stateid == player.id and c.remote]
  if tryfind:
    if tryfind[0] not in playerflags:
      txt = Text(tryfind[0].name)
      playerflags[tryfind[0]] = txt
    else:
      txt = playerflags[tryfind[0]]
    glTranslate(1.5, 0, 0)
    glScale(0.05,0.05,1)
    txt.draw()

def loadImagery():
  print "loading imagery:"
  for txt in ["wall", "floor", "person", "monster", "potion", "scroll", "book", "sword", "shield"]:
    print txt
    Texture(txt)
  print "done loading imagery."

methodMap = {PlayerState: renderPlayer}
