from collections import OrderedDict
import pygame
from pygame.locals import *
import random


class Controller():
    def __init__(self, parent_intersection):
        self.intersection = parent_intersection
        self.cars_in = set()
        self.reservations = OrderedDict() # ordered for 3.7 and up already
    
    def reserve_spot(self, car):
        factor = self.intersection.factor
        width = self.intersection.cross_zone.width
        self.now = pygame.time.get_ticks() / 1000 # simulation time in seconds
        time_start = self.now + factor * width/car.vel # time to crossing
        time_end = time_start + (width + car.l) / car.vel
        time_request = (time_start, time_end)
        if not self.conflicting(time_request):
            self.reservations.update({car : time_request}) 
        else:
            print('CRASH!')
            print(self.reservations, time_request)
            self.resolve(car, time_request)
        #print(time_request)
        vel = car.vel
        car_len = car.l

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
        #print('thelist')
        #print(list(self.reservations.values())[0][0])
        res = list(self.reservations.values()) # list of reserved times
        front = (self.now, res[0][0]) # time delta range in the front
        print(sum(front)/2)
        print(time_request[1])
        if (delta < front[1] - front[0]) and (time_request[1] < sum(front)/2):
            # In this case it's better to speed up
            print('can fit in front!')
            #TODO: speed up! Not possible until I have more cars
            print()
        else: 
            last_ranges = [(res[i][1], res[i+1][0]) for i in range(len(res)-1)]
            if len(last_ranges) > 1:
                print('last range',last_ranges)
                for r in last_ranges:
                    if delta < r[1]-r[0]:
                        print(r[1] - r[0], delta)
                        print('squeeze time!')
                        #TODO: get 2 averages instruct car to adjust accordingly
                        # Not possible until I have more cars
            else:
                all_ranges = [front] + last_ranges
                print('add to end?')
                #TODO: add range to end, may be similar to above
                print()
