import pygame
from pygame.locals import *
import random


class Car(pygame.Rect):
    """initialized with position (x,y) (INT,INT)
    and travel direction ('u','d','l','r') STR"""
    def __init__(self, x, y, direction):
        self.id = id(self)
        self.color = (0,250,0)
        self.l = random.choice([20, 40, 50, 80])
        self.w = 15
        self.x = x
        self.y = y
        self.vel = simulation.speed_limit - 2 +  random.randint(0,4)
        self.speed_instructions = [] # special instructions (speed, time pair)
        self.refresh_initial_conditions(direction)
        #self.set_front() # perhaps incorporate into refresh initial conditions
       
    def refresh_initial_conditions(self, direction):
        self.direction = direction
        if self.direction in ['d', 'u']:
            self.l, self.w = self.w, self.l
        #print('new car travelling at', self.vel)

    def set_front(self):
        pass
        #front_map = {'r':self.right,'l':self.left,'u':self.top,'d':self.bottom}
        #self.front = front_map[self.direction]
        #print('front',self.front,self.direction)

    def __hash__(self):
        """adding hash, allows object to be stored in dict/set"""
        return hash(self.id)

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
        pygame.draw.rect(screen, (100,100,100), (self.x,self.y,self.w,self.h))


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


class Controller():
    def __init__(self, parent_intersection):
        self.intersection = parent_intersection
        self.cars_in = set()
        self.reservations = {} # reserved time slots for passing cars
                               # dict ordered for 3.7 and up already.
                               # can change to OrderedDict to be more general
    def reserve_spot(self, car):
        factor = self.intersection.factor
        width = self.intersection.cross_zone.width
        self.now = pygame.time.get_ticks() / 1000 # simulation time in seconds
        time_start = self.now + factor * width/car.vel # time to crossing
        time_end = time_start + (width + 1.1* car.l) / car.vel # add 10% buffer
        time_request = (time_start, time_end)
        if not self.conflicting(time_request):
            self.reservations.update({car : time_request}) 
            print('no adjustments')
        else:
            #print('Crash or close call predicted')
            self.resolve(car, time_request)

    def remove_reservation(self, car):
        self.reservations.pop(car) 

    def conflicting(self, request):
        if not self.reservations: # if empty, no overlap -> reserve time
            return False
        for _, r in self.reservations.items():
            start1, end1, start2, end2 = request[0], request[1], r[0], r[1]
            if end1 >= start2 and end2 > start1: # if there's an overlap
                return True
        return False

    def resolve(self, car, time_request):
        new_request = None
        delta = time_request[1] - time_request[0]
        res = list(self.reservations.values()) # list of reserved times
        front = (self.now, res[0][0]) # time delta range in the front
        if (delta < front[1] - front[0]) and (time_request[1] < sum(res[0])/2):
            # In this case it's better to speed up
            print('speeding up')
            new_end = front[1] - .1 * delta # 10% buffer
            new_start = new_end - delta
            new_request = (new_start, new_end)
            self.reservations.update({car : new_request})
        else: 
            last_ranges = [(res[i][1], res[i+1][0]) for i in range(len(res)-1)]
            if len(last_ranges) > 1:
                for r in last_ranges:
                    if delta < r[1]-r[0]:
                        new_start = (r[1] - r[0] - delta)/2 + r[0]
                        new_end = new_start + delta
                        new_request = (new_start, new_end)
                        print('slowing a little')
                        self.reservations.update({car : new_request})
            if not new_request: 
                # if the above failed, there's no room in front or between
                # so we add it to the end
                print('slowing')
                new_start = res[-1][1] + .1 * delta # 10% time buffer
                new_end = new_start + delta
                new_request = (new_start, new_end)
                self.reservations.update({car : new_request})

        self.send_instructions(car, new_request)

    def send_instructions(self, car, request):
        factor = self.intersection.factor
        intersection_width = self.intersection.cross_zone.w
        t1 = request[0] - self.now
        d1 = factor * intersection_width
        v1 = d1/t1
        #t2 = request[1] - request[0] 
        #d2 = intersection_width + car.l
        #v2 = car.vel # d2/t2 = car.vel, so this isn't necessary
        velocity_instructions = (v1,t1)
        car.speed_instructions.append(velocity_instructions)


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

                if event.type == pygame.KEYDOWN: # Space button restarts
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
