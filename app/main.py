import pyxel


class App:

  def __init__(self):
    self.HEIGHT = 256
    self.WIDTH = 256
    pyxel.init(self.WIDTH, self.HEIGHT, "Game")

    self.player = 0
    self.carregar_recursos()

    pyxel.run(self.update, self.draw)

  def carregar_recursos(self):
    pyxel.images[0].load(0, 0, "../assets/BackGround/city1/6.png")

  def update(self):
    pass

  def draw(self):
    pyxel.cls(0)

    pyxel.camera(0, 0)

    pyxel.blt(0, 0, 0, 0, 0, self.WIDTH, self.HEIGHT, 0)

    pyxel.text(self.WIDTH / 2 - 10, self.HEIGHT / 2, "Teste", 7)

    pyxel.text(self.WIDTH/2 - 28, self.HEIGHT/2 + 10, "Start the Game", 7)


App()
