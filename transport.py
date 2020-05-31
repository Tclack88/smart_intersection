import pygame
from pygame.locals import *
import random

WIDTH = 1000
HEIGHT = 1000
GREEN = (0,255,0)
BLACK = (0,0,0)
FPS = 30

class Car(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((40,15))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (0, HEIGHT/2)

    def update(self):
        self.rect.x += 5

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


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Intersection Simulation")
clock = pygame.time.Clock()

# Initialize
car = Car(0, HEIGHT/2)
c2 = Car(WIDTH/2, 0, 'd')
rh = Road('h',.5)
rv = Road('v',.5)
# Game loop
running = True
while running:
    # keep loop running at the right speed
    clock.tick(FPS)
    # Process input (events)
    for event in pygame.event.get():
        # check for closing window
        if event.type == pygame.QUIT:
            running = False

    #all_sprites = pygame.sprite.Group()
    #all_sprites.add(car)

    # Update
    
    #all_sprites.update()
    car.update()
    c2.update()
    pygame.display.update()
    # Draw / render
    screen.fill(BLACK)
    rh.render(screen)
    rv.render(screen)
    car.render(screen)
    c2.render(screen)
    #all_sprites.draw(screen)
    # *after* drawing everything, flip the display
    #pygame.display.flip()

pygame.quit()
