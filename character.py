
'''
Base class for characters
'''
from utils import *
from constants import *

class Character():
  def __init__( self, name, w ):
    self.name = name
    self.w = w
    # icon
    self.image = []
    self.inventory = {}

    # character attributes
    self.experience = None
    self.strength = None
    self.intelligence = None
    self.dexterity = None

    self.hitPoints = None
    self.armor = None
    self.weapon = None

  def processEvent( self, e ):
    return True