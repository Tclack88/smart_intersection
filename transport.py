import pygame
from pygame.locals import *
import random

WIDTH = 1000
HEIGHT = 1000
GREEN = (0,255,0)
BLACK = (0,0,0)
FPS = 30

# Keeping this here if I have to go the "sprite" route
# class Car(pygame.sprite.Sprite):
#     def __init__(self):
#         pygame.sprite.Sprite.__init__(self)
#         self.image = pygame.Surface((40,15))
#         self.image.fill(GREEN)
#         self.rect = self.image.get_rect()
#         self.rect.center = (0, HEIGHT/2)
# 
#     def update(self):
#         self.rect.x += 5

class Car:
    # direction: right, down for now
    def __init__(self, x, y, direction='r'):
        self.l = 40
        self.w = 15
        self.x = x
        self.y = y
        self.vel = 20 + random.randint(0,10) - 5
        self.direction = direction
        if self.direction == 'd':
            self.l, self.w = self.w, self.l
        print(self.vel)

    def render(self, screen):
        pygame.draw.rect(screen,(0,250,0),(self.x,self.y,self.l, self.w))

    def update(self):
        if self.direction == 'r':
            self.x += self.vel
        elif self.direction == 'd':
            self.y += self.vel



class Road:
    def __init__(self, orientation, location):
        """orientation: str: 'h' or 'v' (horizontal/vertical)
        location: 0 < float < 1 (fraction of screen width/height)"""
        if orientation == 'h':
            self.w = WIDTH
            self.h = 50
            self.x = 0 
            self.y = HEIGHT/2 - self.h/2
        elif orientation == 'v':
            self.h = HEIGHT
            self.w = 50
            self.y = 0
            self.x = WIDTH/2 - self.w/2

    def render(self, screen):
        pygame.draw.rect(screen, (100,100,100), (self.x, self.y, self.w, self.h))


class Simulation:
    def __init__(self):
        self.running = True
        self.size = self.WIDTH, self.HEIGHT = 1000, 1000
        self.screen = pygame.display.set_mode(self.size)

    def on_init(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Smart Intersection Simulation")
        self.clock = pygame.time.Clock()
        self.FPS = 30
    
    def object_init(self):
        self.cars = [Car(0, HEIGHT/2), Car(WIDTH/2, 0, 'd')]
        self.roads = [Road('h',.5), Road('v',.5)]

    def on_loop(self):
        while self.running:
            # keep loop running at the right speed
            self.clock.tick(self.FPS)
            # Process input (events)
            for event in pygame.event.get():
                # check for closing window
                if event.type == pygame.QUIT:
                    self.running = False

            #all_sprites = pygame.sprite.Group()
            #all_sprites.add(car)

            # Update
            
            #all_sprites.update()
            for car in self.cars:
                car.update()
            pygame.display.update()
            # Draw / render
            self.screen.fill(BLACK)
            for road in self.roads:
                road.render(self.screen)
            for car in self.cars:
                car.render(self.screen)
            #all_sprites.draw(screen)
            # *after* drawing everything, flip the display
            #pygame.display.flip()

        pygame.quit()

    def execute(self):
        self.on_init()
        self.object_init()
        self.on_loop()


if __name__ == "__main__":
    simulation = Simulation()
    simulation.execute()
