#!/usr/bin/env python3.1
"""
dubious math raster image module
--------------------------------

copyright jeremy banks <jeremy@jeremybanks.ca>
distributed under the mit license

this module is part of the dubious math library[1], but as it may be
useful independent of the rest of the library if is made available
seperately[2] and more freely[3].

[1]: http://jeremybanks.github.com/dubious/
[2]: http://github.com/jeremybanks/dubious/tree/raster
[3]: dubious math is distributed under the gpl 2.0
"""

try:
    from dubious import Object
except ImportError:
    class Object(object):
        """Provides the minimum of the dubious.Object interface required"""
        
        __init__    = lambda self, *a, **kw: self.initialize(*a, **kw)
        __getitem__ = lambda self, key: self.get_item(key)
        __setitem__ = lambda self, key, value: self.set_item(key, value)
        __call__    = lambda self, *a, **kw: self.call(*a, **kw)

from struct import Struct
import math

# Pens are applied on a per-channel basis.
PEN_REPLACE = lambda old, new: new
PEN_ADD     = lambda old, new: old + new
PEN_MIN     = lambda old, new: min(old, new)
PEN_MAX     = lambda old, new: max(old, new)
PEN_DIFF    = lambda old, new: abs(old - new)
PEN_XOR     = lambda old, new: old ^ new

class Raster(Object):
    color_fmt = Struct("B")
    default_fill = [ 0 ]
    
    default_pen = staticmethod(PEN_REPLACE)
    
    def initialize(self, width, height, fill=None, pen=None):
        if fill is None:
            fill = self.default_fill
        
        self.width = width
        self.height = height
        self.data = (width * height *
                     bytearray(self.color_fmt.pack(*fill)))
        self.pen = pen or self.default_pen
    
    def get_item(self, x_y):
        x, y = x_y
        
        if not(0 <= x < self.width and
               0 <= y < self.height):
            return None

        i = (y * self.width + x) * self.color_fmt.size
        
        return self.color_fmt.unpack(self.data[i:i + self.color_fmt.size])
    
    def set_item(self, x_y, color):
        x, y = x_y
        
        if not(0 <= x < self.width and
               0 <= y < self.height):
            return
        
        i = (y * self.width + x) * self.color_fmt.size
        
        self.data[i:i + self.color_fmt.size] = self.color_fmt.pack(*color)

    def dot(self, coordinates, color, opacity=1, pen=None, radius=.5):
        """Draws a dot/circle of the chosen radius. Default, .5, is just a point."""
        
        pen = pen or self.pen
        x, y = coordinates

        if (x + radius + 1 < 0 or
            x - radius - 1 > self.width or
            y + radius + 1 < 0 or
            y - radius - 1 > self.height):
            return # out of bounds
        
        offsets = range(math.floor(-radius) - 1,
                        math.ceil ( radius) + 2)

        offset_error = radius - (math.floor(-radius) - 1)
        
        x_int, x_frac = divmod(x, 1)
        y_int, y_frac = divmod(y, 1)
        
        for x_o in offsets:
            for y_o in offsets:
                distance = math.sqrt((x_o - x_frac) ** 2 +
                                     (y_o - y_frac) ** 2)
                
                if distance <= radius - .5:
                    self.point((x_int + x_o,
                                y_int + y_o), color, opacity, pen)
                elif distance < radius + .5:
                    self.point((x_int + x_o,
                                y_int + y_o), color, (opacity
                                                      * (radius - distance + .5)), pen)
    
                              # type # value # description
                              # ---- # ----- # -----------
WINDOWS_BITMAP_HEADER = Struct( "<"          # (struct little-endian indicator)
                                "2s" #    BM # "magic number" file type identifier
                                "I"  #       # file size (bytes)
                                "4s" #  jeba # reserved/unused
                                "I"  #    54 # bitmap data offset = self.size
                                             # (above is BMP header)
                                             # (below is DIB header)
                                "I"  #    40 # size of DIB header (bytes)
                                "i"  #       # width of image
                                "i"  #       # -height of image
                                "H"  #     1 # color planes used
                                "H"  # 24/32 # bit per pixel
                                "I"  #     0 # compression type used
                                "I"  #       # bitmap data size (bytes)
                                "i"  #     0 # horizontal resolution (pixels/metre)
                                "i"  #     0 # vertical resolution (pixels/metre)
                                "I"  #     0 # number of colors in of color palette
                                "I"  #     0 # number of "important" colors in color palette
                                )

# the color palette comes after the header if you have one, but as we
# haven't we go straight to the bitmap data. 24- and 32-bit are one
# byte per channel per pixel, so it's simply that, except:
# 
# - the rows are stored in reverse order (upside-down) by
#   default. instead of that we choose to specify our height as
#   negative, which has the same result.
# 
# - the bytes are ordered BGR instead of RGB, and BGRA instead of RGBA
# 
# - the number of bytes used by each row of the image must be padded
#   to a multiple of four

class Raster_24RGB(Raster):
    color_fmt = Struct("BBB")
    default_fill = 0, 0, 0
    
    def point(self, coordinates, color, opacity=1, pen=None):
        pen = pen or self.pen
        coordinates = [ int(_) for _ in coordinates ]
        
        previous = self[coordinates]
        
        if previous is None:
            return # OOB
        
        # colors may be given as floats (0 to 1)
        # or as integers (0 to 255)
        
        if opacity != 1:
            if isinstance(color[0], float):
                color = [ int(f * 255 * opacity)
                          for f, p in zip(color, previous) ]
            else:
                color = [ int(i * opacity)
                          for i, p in zip(color, previous) ]
        elif isinstance(color[0], float):
                color = [ int(f * 255) for f in color ]
        
        self[coordinates] = [ int(pen(current, old))
                              for current, old
                              in zip(color, previous) ]
    
    def write_bmp(self, file, offset=0):
        row_bytes = self.width * 3
       
        if row_bytes % 4 == 0:
            row_padding = 0
        else:
            row_padding = 4 - (row_bytes % 4)
        
        data_offset = WINDOWS_BITMAP_HEADER.size + offset
        data_size = self.height * (row_bytes + row_padding)
        file_size = data_size + WINDOWS_BITMAP_HEADER.size
        
        file.write(WINDOWS_BITMAP_HEADER.pack("BM",
                                              file_size,
                                              "jeba", # unused
                                              data_offset,
                                              40, # size of 2nd half of header
                                              self.width,
                                              -self.height,
                                              1, # color planes
                                              24, # bits per pixel
                                              0, # compression type
                                              data_size,
                                              0, # h-res, pixels/metre
                                              0, # v-res, pixels/metre
                                              0, # colors in palette
                                              0)) # important colors in palette

        for y in range(self.height):
            for x in range(self.width):
                BGR = reversed(self[x, y])
                file.write(bytes(BGR))
                
            for i in range(row_padding):
                file.write(b"\x00")

class RGBA_Gradient(object):
    def __init__(self, data):
        self.data = sorted(data)

    def __call__(self, point):
        # we just iterate the list to find ours;
        # it feels like we should be using a binary
        # search, but given the small size of our data
        # and the fact that a python function call
        # would probably take more resources than
        # iterating the list, we'll just do that.
        
        def get_first_index(point):
            first_index = 0
            
            for i, point_color in enumerate(self.data):
                p, c = point_color
                
                if p > point:
                    return first_index
                
                first_index = i
            else:
                return first_index
        
        first_index = get_first_index(point)
        first_point, first_color = self.data[first_index]
        
        # if perfect match or nothing follows
        if first_point == point or first_index + 1 == len(self.data):
            return first_color
        
        # otherwise...
        second_point, second_color = self.data[first_index + 1]

        if first_point == second_point:
            # partically covering an edge I don't touch
            
            first_balance = second_balance = 1/2
        else:
            first_balance = (point - first_point) / (second_point - first_point)
            second_balance = 1 - first_balance
            
            first_balance, second_balance = second_balance, first_balance # why?
        
        result = tuple( first_balance * first +
                        second_balance * second for first, second in zip(first_color,
                                                                         second_color) )
        
        return result

# fades out to purple on either end, runs the RGB spectrum between, so
# that all channels will be available at full opacity. this is so that
# i can take the min for each channel when painting a new color and
# have something which remains in the same point for the complete
# duration appear white.
                             # point,( r, g, b, a)
mah_spectrum = RGBA_Gradient([ (0/6, (  .5,  .0,  .5,  .0)),
                               (1/6, (  .0,  .0, 1.0, 1.0)),
                               (2/6, (  .0,  .5,  .5, 1.0)),
                               (3/6, (  .0, 1.0,  .0, 1.0)),
                               (4/6, (  .5,  .5,  .0, 1.0)),
                               (5/6, ( 1.0,  .0,  .0, 1.0)),
                               (6/6, (  .5,  .0,  .5,  .0)) ])

def main():
    import random
    
    size = 512
    image = Raster_24RGB(size, size, fill=[0, 0, 0], pen=PEN_MAX)
    theta = 0

    print("Image instantiated.")
    
    def generate_stars(raster):
        for n in range(100):
            x = random.random() * raster.width
            y = random.random() * raster.height

            p = (n + 1) / 100
            rc = lambda: random.random() * p + (1 - p)
            
            r, b, o = [ rc() for _ in range(3) ]
            g = min(r, b) # never dominate color
            
            raster.dot([x, y], [r, g, b], o, radius=.6 + random.random() * .5)
    
    print("Rendering background stars...")
    generate_stars(image)
    
    print("Rendering foreground objects...")
    while theta < 3 / 2 * math.pi:
        for _ in range(5):
            x = size / 2 + size * 2 / 5 * math.cos(theta + 4)
            y = size / 2 + size * 2 / 5 * math.sin(theta + 4)
            
            r, g, b, a = mah_spectrum(theta / (3 / 2 * math.pi))
            
            image.dot([x, y], [r, g, b], a, radius=size/42) # draw orbiting dot

            theta += .10

            
        image.dot([ size / 4,
                    size / 6 + size / 6 * 4 * theta / ( 3/2*math.pi) ],
                  [r,g,b], a, radius=size/32)
        
        opposite_theta = theta + math.pi
        
        planet_x = size / 2 + (size / 36) * math.cos(opposite_theta + 4)
        planet_y = size / 2 + (size / 36) * math.sin(opposite_theta + 4)
        
        image.dot([planet_x, planet_y], [r, g, b], a, radius=size/8) # draw planet
    
    print("Image generated.")
    
    with open("out.bmp", "wb") as o:
        image.write_bmp(o)
    
    print("Image written.")
    
    from subprocess import Popen
    
    print("Attempting to $(convert) image to png.")
    # identifies errors in our file
    Popen(["convert", "out.bmp", "out.png"]).communicate()

if __name__ == "__main__":
    import sys

    sys.exit(main(*sys.argv[1:]))
