import pyxel


class App:
    def __init__(self):
        pyxel.init(160, 160, "Game")
        self.x = 0
        self.mapa()
        pyxel.run(self.update, self.draw)
    def update(self):
        self.x = (self.x + 1) % pyxel.width
    def draw(self):
        pyxel.cls(0)
        pyxel.rect(self.x, 0, 8, 8, 9)
        pyxel.blt(10, 10, 0, 0, 0, 120, 120, 0)
    def mapa(self):
        pyxel.images[0].load(0, 0, "../assets/BackGround/city1/6.png")


App()