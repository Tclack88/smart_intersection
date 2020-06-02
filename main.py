from collections import OrderedDict
from controller import Controller
import pygame
from pygame.locals import *
import random


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


class Car(pygame.Rect):
    """initialized with position (x,y) (INT,INT) 
    and travel direction ('u','d','l','r') STR"""
    def __init__(self, x, y, direction='r'):
        self.id = id(self)
        self.color = (0,250,0)
        self.l = 40
        self.w = 15
        self.x = x
        self.y = y
        self.vel = 20 + random.randint(0,10) - 10
        self.direction = direction
        if self.direction in ['d', 'u']:
            self.l, self.w = self.w, self.l

    def __hash__(self):
        """adding hash, allows object to be stored in dict/set"""
        return hash(self.id)

    def render(self, screen):
        pygame.draw.rect(screen,self.color,(self.x,self.y,self.l, self.w))

    def update(self):
        if self.direction == 'r':
            self.x += self.vel
        elif self.direction == 'd':
            self.y += self.vel
        elif self.direction == 'l':
            self.x -= self.vel
        elif self.direction == 'u':
            self.y -= self.vel

        if 0 > self.x > simulation.WIDTH or 0 > self.y > simulation.HEIGHT:
            self.destroy()

    def approach_speed_limit(self):
        diff = self.vel - simulation.speed_limit
        self.vel -= diff

    def destroy(self):
        """ remove cars beyond boundary lines """
        simulation.cars.remove(self)
        simulation.intersection.cars = set(simulation.cars)

    def change_color(self, status):
        """ color change to indicate if within boundary """
        if status == 'enter':
            self.color = (250,0,0)
        elif status == 'exit':
            self.color = (0,250,0)


class Intersection:
    """ Input: a list of two road (pygame rect objects)  
    Establishes - crossing zone - where the road rectangles cross
                - outer boundary - buffer zone for cars to accelerate
    """
    def __init__(self, roads):
        self.controller = Controller(self) # Init. controller to manage cars
        self.count = 0
        self.cars = set() # rolling list of contained cars
        self.roads = roads
        # Make coordinates for crossing zone (actual intersection)
        self.cross_zone = roads[0].clip(self.roads[1]) # Overlapping area
        # Make coordinates for outer boundary (acceleration zone)
        self.factor = 5 # factor - arbitrary. Can be int or .5
        self.bndry_coords = (self.cross_zone.x - self.factor*self.cross_zone.w,
                self.cross_zone.y - self.factor*self.cross_zone.h,
                self.cross_zone.w*(2*self.factor + 1), # arbitrary choice 
                self.cross_zone.h*(2*self.factor + 1))
        self.outer_boundary = pygame.Rect(self.bndry_coords)

    def render(self, screen):
        pygame.draw.rect(screen,(150,150,0),self.cross_zone,1)
        pygame.draw.rect(screen,(10,150,0),self.bndry_coords,1) 

    def check(self):
        """ Update records of cars entering and leaving boundary"""
        current_cars = set(self.outer_boundary.collidelistall(simulation.cars))
        current_cars = set([simulation.cars[c] for c in current_cars])
        cars_incoming = current_cars - self.cars
        cars_outgoing = self.cars - current_cars
        if cars_incoming:
            for car in cars_incoming:
                car.change_color('enter')
                car.render(simulation.screen)
                self.controller.reserve_spot(car)
        if cars_outgoing:
            for car in cars_outgoing:
                car.change_color('exit')
                car.render(simulation.screen)
                car.approach_speed_limit()

        self.cars = current_cars
        crossing_cars = set(self.cross_zone.collidelistall(list(self.cars)))
        if crossing_cars:
            pass #TODO: for each car, chase original speed


class Simulation:
    def __init__(self):
        self.running = True
        self.size = self.WIDTH, self.HEIGHT = 1000, 1000
        self.screen = pygame.display.set_mode(self.size)
        pygame.font.init()
        t = pygame.font.SysFont('dejavusans',30)
        self.message = t.render('press <space> to restart', False,(255,255,255))

    def on_init(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Smart Intersection Simulation")
        self.clock = pygame.time.Clock()
        self.FPS = 20
        self.SPAWN = pygame.USEREVENT + 1
        self.speed_limit = 20
        pygame.time.set_timer(self.SPAWN, 1000)
    
    def object_init(self):
        self.cars = [Car(0, self.HEIGHT/2, 'r'), Car(self.WIDTH/2-20, 0, 'd')]#,
        self.roads = [Road('h',.5), Road('v',.5)]
        self.intersection = Intersection(self.roads)

    def on_loop(self):
        while self.running:
            # keep loop running at the right speed
            self.clock.tick(self.FPS)
            # Process input (events)
            for event in pygame.event.get():
                if event.type == self.SPAWN:
                    self.cars.append(random.choice([Car(0, self.HEIGHT/2, 'r'),
                        Car(self.WIDTH/2 - 20, 0, 'd'),
                        Car(self.WIDTH, self.HEIGHT/2-20, 'l'), 
                        Car(self.WIDTH/2, self.HEIGHT,'u')]))
                # check for space bar pressed (reset)
                if event.type == pygame.KEYDOWN: 
                    if event.key == pygame.K_SPACE:
                        self.execute()
                # check for closing window
                elif event.type == pygame.QUIT:
                    self.running = False


            # Update
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


            self.screen.blit(self.message,(0,0))
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
