import pygame
from pygame.locals import *

WIDTH = 640
HEIGHT = 400
GREEN = (0,255,0)
FPS = 30

class Car(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40,15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH/2, HEIGHT/2)

class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 640, 400
 
    def on_init(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self._display_surf = pygame.display.set_mode(self.size)#, pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._running = True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False
    def on_loop(self):
        pass
    def on_render(self):
        print('render')
        car = Car()
        all_sprites = pygame.sprite.Group()
        all_sprites.add(car)
        all_sprites.draw(self._display_surf)
        self._display_surf.update()

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False
 
        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)
            self.clock.tick(FPS)
            self.on_loop()
            self.on_render()
        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()
