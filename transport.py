import pygame
from pygame.locals import *
import random


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

class Car(pygame.Rect):
    # direction: right, down for now (r,d)
    def __init__(self, x, y, direction='r'):
        self.color = (0,250,0)
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
        pygame.draw.rect(screen,self.color,(self.x,self.y,self.l, self.w))

    def update(self):
        if self.direction == 'r':
            self.x += self.vel
        elif self.direction == 'd':
            self.y += self.vel

    def change_color(self, status):
        # color change to indicate inside boundary
        if status == 'enter':
            self.color = (250,0,0)
        elif status == 'exit':
            self.color = (0,250,0)


class Road(pygame.Rect):
    def __init__(self, orientation, location):
        """orientation: str: 'h' or 'v' (horizontal/vertical)
        location: 0 < float < 1 (fraction of screen width/height)"""
        if orientation == 'h':
            self.w = simulation.WIDTH
            self.h = 50
            self.x = 0 
            self.y = simulation.HEIGHT/2 - self.h/2
        elif orientation == 'v':
            self.h = simulation.HEIGHT
            self.w = 50
            self.y = 0
            self.x = simulation.WIDTH/2 - self.w/2

    def render(self, screen):
        pygame.draw.rect(screen, (100,100,100), (self.x, self.y, self.w, self.h))

class Intersection:
    def __init__(self, roads):
        self.count = 0
        self.cars = set() # rolling list of contained cars
        self.roads = roads
        self.intersection = roads[0].clip(self.roads[1]) # created from road overlap
        self.factor = 5 # factor
        self.coords = (self.intersection.x - self.factor*self.intersection.w,
                self.intersection.y - self.factor*self.intersection.h,
                self.intersection.w*(2*self.factor + 1), # arbitrary choice 
                self.intersection.h*(2*self.factor + 1))
        self.outer_boundary = pygame.Rect(self.coords)

    def render(self, screen):
        pygame.draw.rect(screen,(150,150,0),self.intersection,1)
        pygame.draw.rect(screen,(10,150,0),self.coords,1) 
        #pygame.draw.rect(screen,(10,150,0),self.outer_boundary,1) # same as above
    def check(self):
        current_cars = set(self.outer_boundary.collidelistall(simulation.cars))
        cars_in = current_cars - self.cars
        cars_out = self.cars - current_cars
        if cars_in:
            for car in cars_in:
                print('new car in:',car)
                print(simulation.cars[car].color)
                simulation.cars[car].change_color('enter')
                simulation.cars[car].render(simulation.screen)
                print(simulation.cars[car].color)
        if cars_out:
            for car in cars_out:
                print('car leaving:',car)
                print(simulation.cars[car].color)
                simulation.cars[car].change_color('exit')
                simulation.cars[car].render(simulation.screen)
                print(simulation.cars[car].color)

        self.cars = current_cars

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
        self.FPS = 20
    
    def object_init(self):
        self.cars = [Car(0, self.HEIGHT/2), Car(self.WIDTH/2, 0, 'd')]
        self.roads = [Road('h',.5), Road('v',.5)]
        self.intersection = Intersection(self.roads)

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
            self.screen.fill((0,0,0))
            for road in self.roads:
                road.render(self.screen)

            self.intersection.render(self.screen)
            self.intersection.check()

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
