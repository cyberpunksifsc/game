import pyxel


STATE_INTRO = "INTRO"
STATE_GAMEPLAY = "GAMEPLAY"

class Gameplay:
    def __init__(self, app):
        self.app = app

        self.state = STATE_INTRO

        #self.carregar_recursos()

        self.camera_y = 0

    def update(self):
        if self.state == STATE_INTRO:
            if self.camera_y < 160:
                self.camera_y += 2
                if self.camera_y > 160:
                    self.camera_y = 160
            #self.camera_y+=1
            else:
                self.state = STATE_GAMEPLAY
        

    def draw(self):
        pyxel.cls(0)
        pyxel.camera(0, self.camera_y)
        pyxel.blt(0, 0, 0, 0, 0, self.app.WIDTH, 60 , 0)