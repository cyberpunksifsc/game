import pyxel
from constants import STATE_MAIN_MENU, STATE_GAMEPLAY
from main_menu import MainMenu
from gameplay import Gameplay

class App:

  def __init__(self):
    self.state = STATE_MAIN_MENU
    self.HEIGHT = 256
    self.WIDTH = 256
    pyxel.init(self.WIDTH, self.HEIGHT, "Game")

    self.main_menu = MainMenu(self)
    self.gameplay = Gameplay(self)

    self.player = 0

    pyxel.run(self.update, self.draw)

  def update(self):
    if self.state == STATE_MAIN_MENU:
        new_state = self.main_menu.update()
    elif self.state == STATE_GAMEPLAY:
        new_state = self.gameplay.update()
    else:
        new_state = None

    if new_state is not None and new_state != self.state:
        self.state = new_state
        if new_state == STATE_GAMEPLAY:
            self.gameplay.enter()
  def draw(self):
    pyxel.cls(0)

    if self.state == STATE_MAIN_MENU:
      self.main_menu.draw()
    if self.state == STATE_GAMEPLAY:
      self.gameplay.draw()

App()
