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
  with glPrimitive(GL_LINES):
    for x in range(int(player.position[0] - 30), int(player.position[0] + 30), 1):
      if x % 10 == 0:
        glColor(0.3, 0.3, 0, 1)
      elif x % 10 == 5:
        glColor(0.15, 0.15, 0, 1)
      else:
        glColor(0.05, 0.05, 0, 1)
      glVertex2f(x, player.position[1] - 30)
      glVertex2f(x, player.position[1] + 30)
    for y in range(int(player.position[1] - 30), int(player.position[1] + 30), 1):
      if y % 10 == 0:
        glColor(0.3, 0.3, 0)
      elif y % 10 == 5:
        glColor(0.15, 0.15, 0)
      else:
        glColor(0.05, 0.05, 0)
      glVertex2f(player.position[0] - 30, y)
      glVertex2f(player.position[0] + 30, y)
  glColor(1.0, 1.0, 1.0)


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
    glEnable(GL_TEXTURE_2D)
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
    glEnable(GL_TEXTURE_2D)
    if tryfind[0] not in playerflags:
      txt = Text(tryfind[0].name)
      playerflags[tryfind[0]] = txt
    else:
      txt = playerflags[tryfind[0]]
    glTranslate(1.5, 0, 0)
    glScale(0.05,0.05,1)
    txt.draw()
    glDisable(GL_TEXTURE_2D)

def loadImagery():
  print "loading imagery:"
  for txt in ["wall", "floor", "person", "monster", "potion", "scroll", "book", "sword", "shield"]:
    print txt
    Texture(txt)
  print "done loading imagery."

methodMap = {PlayerState: renderPlayer}
