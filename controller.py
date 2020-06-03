from collections import OrderedDict
import pygame
from pygame.locals import *
import random


class Controller():
    def __init__(self, parent_intersection):
        self.intersection = parent_intersection
        self.cars_in = set()
        self.reservations = {} # OrderedDict() # ordered for 3.7 and up already

    def reserve_spot(self, car):
        factor = self.intersection.factor
        width = self.intersection.cross_zone.width
        self.now = pygame.time.get_ticks() / 1000 # simulation time in seconds
        time_start = self.now + factor * width/car.vel # time to crossing
        time_end = time_start + (width + car.l) / car.vel
        time_request = (time_start, time_end)
        if not self.conflicting(time_request):
            self.reservations.update({car : time_request})
            print('no adjustments')
        else:
            #print('Crash or close call predicted')
            self.resolve(car, time_request)

    def remove_reservation(self, car):
        #self.reservations.pop(car) # probably something like this
        try:
            self.reservations.pop(car) # probably something like this
        except:
            # TODO: Debug
            print('\nREMOVE RESERVATION ERROR \n') # Get it the next time around

    def conflicting(self, request):
        if not self.reservations: # if empty, no overlap -> reserve time
            return False
        for _, r in self.reservations.items():
            start1, end1, start2, end2 = request[0], request[1], r[0], r[1]
            if end1 >= start2 and end2 > start1: # if there's an overlap
                return True
        return False

    def resolve(self, car, time_request):
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
            else:
                print('slowing')
                new_start = res[-1][1] + .1 * delta # 10% time buffer
                new_end = new_start + delta
                new_request = (new_start, new_end)
                self.reservations.update({car : new_request})

        try:
            self.send_instructions(car, new_request)
        except:
            #TODO debug
            print('SEND INSTRUCTIONS ERROR')

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
