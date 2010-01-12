#!/usr/bin/env python3.1
"""a primitive and probably unrealistic gravity simluation, acting as a mock-up"""

import sys
import raster
from math import sqrt # since you can just do **.5 why isn't this builtin?
from math import sin, cos

class Object(object):
    def __init__(self, mass, velocity, position):
        self.mass = mass
        self.velocity = list(velocity)
        self.position = list(position)

    def distance_from(self, other):
        return sum(map((lambda a_b: (a_b[0] - a_b[1]) ** 2), zip(self.position, other.position)))**.5

class GravitySim(object):
    def __init__(self, initial_state, resolution=10, G=6.67428e-11):
        self.frames = [ list(initial_state) ]
        self.resolution = resolution # frames per second
        self.G = G
    
    def tick(self):
        d_t = 1 / self.resolution
        
        next_frame = list()
        
        for object in self.state:
            new_velocity = object.velocity

            for other in self.state:
                if other is not object:
                    a_magnitude = self.G * other.mass / (object.distance_from(other) ** 2)
                    
                    # this is almost certainly wrong:
                    x_delta = object.position[0] - other.position[0]
                    y_delta = object.position[1] - other.position[1]
                    x_portion = x_delta / ( abs(x_delta) + abs(y_delta))
                    y_portion = y_delta / ( abs(x_delta) + abs(y_delta))
                    a_x = a_magnitude * x_portion
                    a_y = a_magnitude * y_portion

                    a = [a_x, a_y]

                    new_velocity = list(map(sum, zip(a, new_velocity)))
            
            next_frame.append(Object(object.mass, new_velocity, map(sum, zip(object.position, new_velocity))))
        
        self.frames.append(next_frame)
    
    def tock(self, seconds):
        for _ in range(int(resolution * seconds)):
            self.tick()
    
    @property
    def state(self):
        return self.frames[-1]

def main(frames=100):
    frames = int(frames)
    
    sim = GravitySim([ Object(10, [ 0,  0], [ 0,  0]),
                       Object( 2, [ 1, -1], [10, 10]) ],
                     G=100) # only diffs reality by a factor of 150 billion
    
    width = 128
    height = 128
    offset = [+64, +64]
                              
    image = raster.Raster_24RGB(width, height, fill=[0, 0, 0], pen=raster.PEN_MAX)
    
    for f in range(frames):
        print("Generating frame {}...".format(f))
        
        if f: sim.tick()
        
        r, g, b, a = raster.mah_spectrum(f / (frames - 1))
        
        for object in sim.state:
            image.dot([ object.position[0] + offset[0],
                        object.position[1] + offset[1] ], [r, g, b], a, radius=sqrt(object.mass) * 3)
    
    with open("out.bmp", "wb") as o:
        image.write_bmp(o)
    
if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
