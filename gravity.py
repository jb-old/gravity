#!/usr/bin/env python3.1
from copy import copy, deepcopy
import itertools
import json
import random
import sys
import time

from vector import Vector, V, sqrt
import raster

class Object(object):
    """A non-elastic frictionless sphere in a vaccum, ha."""
    
    def __init__(self, mass, displacement, velocity, radius=None, combining=True):
        self.mass = mass
        self.displacement = Vector(displacement)
        self.velocity = Vector(velocity)
        
        if radius is None:
            self.radius = 2 * sqrt(self.mass)
        else:
            self.radius = radius

        self.combining = bool(combining)

    from_dict_defaults = { "m": 1, "d": [ 0, 0 ], "v": [ 0, 0 ],
                           "radius": None, "combining": True }
    
    @classmethod
    def from_dict(cls, source_dict):
        input_dict = deepcopy(cls.from_dict_defaults)
        input_dict.update(source_dict)
        return cls(input_dict["m"], input_dict["d"], input_dict["v"], input_dict["radius"], input_dict["combining"])

    def __repr__(self):
        return ("{.__name__}(mass={!r}, displacement={!r}, velocity={!r}, radius={!r}}, combining={!r})"
                .format(type(self), self.mass, self.displacement, self.velocity, self.radius, self.combining))

def simulate(current, time_step, G=6.67428e-11):
    """Yields an initial state and all following frames."""
    
    yield current
    
    while True:
        current = deepcopy(current)
        
        for object, other in itertools.combinations(current, 2):
            displacement = other.displacement - object.displacement
            
            if displacement.magnitude > .5:
                force_magnitude = G * object.mass * other.mass / displacement.magnitude ** 2

                # this is wrong. what I think it actually should be
                # is something like...
                # 
                # F_y = sqrt(force_magnitude ** 2
                #            / ((displacement[0] / displacement[1]) ** 2 + 1))
                # F_x = (displacement[x] / displacement[y]) * F_y
                #
                # Determined from F_x^2 + F_y^2 = |F|^2
                #             and F_x / F_y = delta_x / delta_y
                # 
                # See notebook 2010-Feb-14 note 2010-Feb-24#1.
                
                x_portion = displacement[0] / sum(abs(v) for v in displacement)
                y_portion = displacement[1] / sum(abs(v) for v in displacement)
                
                force = V(x_portion * force_magnitude,
                          y_portion * force_magnitude)
                
                object.velocity += force / object.mass * time_step
                other.velocity  -= force / other.mass  * time_step
        
        for object in current:
            object.displacement += object.velocity * time_step
        
        # combing colliding combining objects
        for i, object in enumerate(current):
            if object is None or not object.combining: continue
            
            for j, other in enumerate(current[i + 1:]):
                if other is None or not other.combining: continue
                
                displacement = other.displacement - object.displacement
                
                if displacement.magnitude < min(object.radius, other.radius):
                    object_portion = object.mass / (object.mass + other.mass)
                    other_portion  = other.mass  / (other.mass + other.mass)
                    
                    combined_object = Object(mass=object.mass + other.mass,
                                             displacement=object_portion * object.displacement + other_portion * other.displacement,
                                             velocity=object_portion * object.velocity + other_portion * other.velocity,
                                             radius=sqrt(object.radius ** 2 + other.radius ** 2))
                    
                    current[i] = object = combined_object
                    current[i + 1 + j] = other = None
        
        if None in current:
            current = [ o for o in current if o is not None ]
        
        yield current

def starify_raster(raster, n=None):
    """Draws background-ish "stars" on a Raster image."""
    
    if n is None:
        n = int((raster.width * raster.height) * 0.01)
    
    for _ in range(n):
        x = int(random.random() * (raster.width + 4) - 2)
        y = int(random.random() * (raster.height + 4) - 2)
        
        r, g, b = [ .2 + .4 * random.random() + .4 * random.random() for _ in range(3) ]
        
        g = min(r, g, b) # ensure green is never above red or blue
        # maybe I could draw colours from a gradient instead

        raster.dot([x, y], [r, g, b], random.random() * .7, radius=random.random())

raster.Raster.starify = starify_raster

def main(in_filename="-", out_filename="-"):
    in_file  = open(in_filename,  "rt") if in_filename  != "-" else sys.stdin
    out_file = open(out_filename, "wb") if out_filename != "-" else sys.stdout.buffer
    
    input_defaults = { "comment": None, # it's a comment, ignored
                       "dimensions": [ 1024, 1024 ], # size of output image, and unzoomed view area in metres
                       "G": 6.67428e-11, # gravitational constant
                       "dt": 60 * 60 * 24 * 365, # duration in render in seconds
                       "frames": 3001, # drawing "frames" to use
                       "objects": [], # objects in system we're rendering
                       "centre": [0, 0], # centre of view
                       "zoom": 1e-9 } # factor of magnification
    
    with in_file, out_file:
        start = time.time()
        
        input_dict = deepcopy(input_defaults)
        input_dict.update(json.load(in_file))
        
        width, height = dimensions = input_dict["dimensions"]
        offset = V(width / 2 + .5, height / 2 + .5)
        
        frame_count = input_dict["frames"]
        time_step = input_dict["dt"] / ((frame_count - 1) or 1)
        centre = Vector(input_dict["centre"])
        zoom = input_dict["zoom"]
        
        sys.stderr.write("Loading input system...\n")
        system = [ Object.from_dict(d) for d in input_dict["objects"] ]
        
        sys.stderr.write("Instantiating image...\n")
        image = raster.Raster_24RGB(width, height, fill=[0, 0, 0], pen=raster.PEN_MAX)
        
        sys.stderr.write("Rendering background stars...\n")
        image.starify()
        
        frames = itertools.islice(simulate(system, time_step, G=input_dict["G"]), frame_count)
        
        for f, objects in enumerate(frames):
            r, g, b, a = raster.mah_spectrum(f / (frame_count - 1) if frame_count > 1 else .5)
            sys.stderr.write("Calculuated, rendering frame {}...\r".format(f))
            sys.stderr.flush()
            
            if a:
                for object in objects:
                    dot_position = (object.displacement - centre) * zoom + offset
                    dot_radius = max(.5, object.radius * zoom)
                    
                    image.dot(dot_position, [r, g, b], a, radius=dot_radius)
        
        sys.stderr.write("\n")
        sys.stderr.write("Writing image to file...")
        sys.stderr.flush()
        image.write_bmp(out_file)
        sys.stderr.write("Complete. Total clock time elasped has been {:.1f}.\n".format(time.time))
    
if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))

