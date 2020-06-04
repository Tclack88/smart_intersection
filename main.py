from collections import OrderedDict
from controller import Controller
import pygame
from pygame.locals import *
import random


class Road(pygame.Rect):
    def __init__(self, orientation, location):
        """orientation: str: 'h' or 'v' (horizontal/vertical)
        location: 0 < float < 1 (fraction of screen width/height)"""
        self.orientation = orientation # used for car initialzation

        if orientation == 'h':
            self.w = simulation.WIDTH
            self.h = 50
            self.center = (simulation.WIDTH / 2 , simulation.HEIGHT * location)
            self.buffer = (self.h - 30) // 4 # subtract 2 car widths, to get
                                             # remainder. Leave 50% that for
                                             # "center divide" & 25% to ends
        elif orientation == 'v':
            self.h = simulation.HEIGHT
            self.w = 50
            self.center = (simulation.WIDTH * location, simulation.HEIGHT / 2)
            self.buffer = (self.w - 30) // 4
    
    def render(self, screen):
        pygame.draw.rect(screen, (100,100,100), (self.x,self.y,self.w,self.h))


    def add_car(self):
        """ Initializes a car going in a random direction from either end """
        possible_directions = {'h':['l','r'], 'v':['u','d']}
        starting_points = {
                'l': (self.right, self.top + self.buffer),
                'r': (self.left, self.bottom - self.buffer - 15),
                'u': (self.right - self.buffer - 15, self.bottom),
                'd': (self.left + self.buffer, self.top)}

        direction = random.choice(possible_directions[self.orientation])
        starting_point = starting_points[direction]
        simulation.cars.append(Car(starting_point, direction))


class Car(pygame.Rect):
    """initialized with point tuple (x,y) (INT,INT)
    and travel direction ('u','d','l','r') STR"""
    def __init__(self, starting_point, direction):
        self.color = (0,250,0)
        self.l = random.choice([20, 40, 50, 80])
        self.w = 15
        self.x = starting_point[0]
        self.y = starting_point[1]
        self.vel = simulation.speed_limit - 5 +  random.randint(0,5)
        self.speed_instructions = [] # special instructions (speed, time) tuple
        self.direction = direction
        if self.direction in ['d', 'u']:
            self.l, self.w = self.w, self.l
        self.speed_instructions = [] # special instructions (speed, time pair)
        #print('new car travelling at', self.vel)

    def __hash__(self):
        """adding hash, allows object to be stored in dict/set"""
        return hash(id(self))

    def render(self, screen):
        pygame.draw.rect(screen,self.color,(self.x,self.y,self.l, self.w))


    def update(self):
        if self.speed_instructions: # issued by controller
            now = pygame.time.get_ticks() / 1000
            marker_time = self.speed_instructions[0][1]
            if now > marker_time:
                # if we're past the instruction time,
                # remove it and return to the original speed
                # NOTE: Strong assumption there's only one instruction
                # To get around this I will probably have to call self.update
                # again, but I'd just need to be careful of recursive errors
                self.speed_instructions.pop(0)
                vel = self.vel
            else:
                vel = self.speed_instructions[0][0]
        else:
            vel = self.vel

        if self.direction == 'r':
            self.x += vel
        elif self.direction == 'd':
            self.y += vel
        elif self.direction == 'l':
            self.x -= vel
        elif self.direction == 'u':
            self.y -= vel


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
        self.cars = set() # rolling set of contained cars
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
        """draw cross zone (actual intersection) and outer boundary"""
        pygame.draw.rect(screen,(150,150,0),self.cross_zone,1)
        pygame.draw.rect(screen,(10,150,0),self.bndry_coords,1) 

    def check_for_cars(self):
        """ Update records of cars entering and leaving boundary"""
        current_cars = self.outer_boundary.collidelistall(simulation.cars)
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
                self.controller.remove_reservation(car)
                car.approach_speed_limit()

        self.cars = current_cars



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
        self.FPS = 30
        self.SPAWN = pygame.USEREVENT + 1
        self.speed_limit = 20
        pygame.time.set_timer(self.SPAWN, 300)

    def object_init(self):
        self.roads = [Road('h',.5), Road('v',.5)]
        self.cars = []
        self.intersection = Intersection(self.roads)

    def on_loop(self):
        while self.running:
            # keep loop running at the right speed
            self.clock.tick(self.FPS)
            # Process input (events)
            for event in pygame.event.get():

                if event.type == self.SPAWN:
                    random.choice(self.roads).add_car()

                elif event.type == pygame.KEYDOWN: # Space button restarts
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
            self.intersection.check_for_cars()

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
