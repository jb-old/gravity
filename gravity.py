#!/usr/bin/env python3.1
"""This module provides basic gravitional system simulation and
visualization using the dubious math raster image module.

You may encounter issues if you do not treat the types in this module
as though they were immutable. Maybe not. This keeps changing."""

class Vector(object):
    """A Vector value of any number of dimensions."""
    
    def __init__(self, components):
        self.components = list(components)

    def magnitude(self):
        return sum(x ** 2 for x in self.components) ** (1/2)
    
    def __getitem__(self, index):
        return self.components[index]
    
    def __setitem__(self, index, value):
        self.components[index] = value
    
    def __add__(self, vector):
        return type(self)(a + b for (a, b) in (self.components, vector.components))
    
    def __sub__(self, vector):
        return type(self)(a - b for (a, b) in (self.components, vector.components))
    
    def __mul__(self, scalar):
        return type(self)(x * scalar for x in self.components)
    
    def __div__(self, scalar):
        return type(self)(x / scalar for x in self.components)
    
    def __neg__(self):
        return type(self)(-x for x in self.components)

    def __iter__(self): # meant for use in iterable instantation, not direct iteration
        return iterator(self.components)

    def __bool__(self):
        return any(self)

    def __eq__(self, other):
        return self.components == other.components

def V(*components):
    """Shortcut for creating Vectors: V(x, y...) -> Vector((x, y...))"""
    
    return Vector(components)

class Object(object):
    """A kinematic Object with mass, displacement and velocity."""
    
    def __init__(self, mass, position, velocity):
        self.mass = mass
        self.displacement = Vector(displacement)
        self.velocity = Vector(velocity)

class System(list):
    def advanced(self, dt_per_step, steps=1, G=6.67428e-11):
        current = System(self)

        for _ in range(steps):
            next = System()
            
            for old_object in self:
                new_object = copy(old_object)
                
                for other in self:
                    if other is not old_object:
                        displacement = old_object.displacement - other.displacement
                        
                        if displacement: # they aren't at the same position
                            acceleration_magnitude = G * other.mass / displacement.magnitude ** 2
                            
                            
                            
                        
            current = next
        
        return current # Python not having tail recursion optimization is stupid.
                       # If it did, I'd implement this recursively and be happier.
    
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

import sys
import raster

def main(in_filename="-", out_filename="-"):
    in_ = open(in_filename,  "rt") if in_filename  != "-" else sys.stdin
    out = open(out_filename, "wb") if out_filename != "-" else sys.stdout.buffer
    # G = 
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

