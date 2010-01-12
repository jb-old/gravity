#!/usr/bin/env python3.1
import sys
import raster
from math import sqrt # since you can just do **.5 why isn't this builtin?
from math import sin, cos

class Vector(object):
    def __init__(self, components):
        self.components = list(components)
    
    def __getitem__(self, key):
        return self.components[key]
    
    def __setitem__(self, key, value):
        self.components[key] = value
    
    @staticmethod
    def __component_shortcut( index):
        def get(self): return self.components[index]
        def set(self, value): self.components[index] = value
        return property(get, set)
    
    x = __component_shortcut(0)
    y = __component_shortcut(1)
    z = __component_shortcut(2)

V = lambda *components: Vector(components) # shortcut to define Vector((1, 2, 3)) as V(1, 2, 3)

class Object(object):
    def __init__(self, mass, velocity, position):
        self.mass = mass
        self.velocity = list(velocity)
        self.position = list(position)

    def distance_from(self, other):
        value = sum(map((lambda a_b: (a_b[0] - a_b[1]) ** 2), zip(self.position, other.position)))**.5
        if value < .1:
            value = .1
        return value

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
                    x_portion = -x_delta / ( abs(x_delta) + abs(y_delta)) if x_delta or y_delta else 0
                    y_portion = -y_delta / ( abs(x_delta) + abs(y_delta)) if x_delta or y_delta else 0
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

def main(in_filename="-", out_filename="-"):
    in_ = open(in_filename,  "rt") if in_filename  != "-" else sys.stdin
    out = open(out_filename, "wb") if out_filename != "-" else sys.stdout.buffer
    
    import json
    
    with in_, out:
        pass
    
    frames = int(frames)
    
    sim = GravitySim([ Object(10, [ 0, +0.3], [ 0,  0]),
                       Object( 2, [ 0, -1.5], [30,  0]), ],
                       Object(5, [ -.1,   1], [-64, -64]) ],
                     G=10, resolution=15) # only diffs reality by a factor of 150 billion
    
    width = height = 192
    offset = [ width / 2, height / 2]
                              
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
