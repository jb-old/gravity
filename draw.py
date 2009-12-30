#!/usr/bin/env python3.1
import sys
import struct

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

        first_balance = (point - first_point) / (second_point - first_point)
        second_balance = 1 - first_balance

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
mah_spectrum = RGBA_Gradient([ (  0, (.5, 0,.5, 0)),
                               (1/6, ( 1, 0, 0, 1)),
                               (1/3, (.5,.5, 0, 1)),
                               (1/2, ( 0, 1, 0, 1)),
                               (2/3, ( 0,.5,.5, 1)),
                               (5/6, ( 0, 0, 1, 1)),
                               (  1, (.5, 0,.5, 0)) ])
BPP = 4 # bytes-per-pixel

def 24b_bmp_header(width, height):
    return b""

def main(size=36):
    if size % 4:
        size += size - (size % 4)
        # size rounded up to multiple of four
    
    image_data = bytearray(BPP * SIZE ** 2) # black bitmap data
    
    def lighten(position, color):
        if not all(0 <= p < SIZE for p in position):
            return # out of bounds
        
        r, g, b, a = color
        x, y = position
        
        # apply alpha as on black
        r, g, b = r * a, g * a, b * a
        
        for channel, value in enumerate((r, g, b)):
            i = int(BBP * (x + y * SIZE)) + channel)
            image_data[i] = max(image_data[i], value)
    
    def speck(position, rgb):
        full = rgb + (1  ,)
        half = rgb + (1/2,)
        qrtr = rgb + (1/4,)
        
        x, y = position
        
        light(position, full)
        light([ x, y - 1 ], half)
        light([ x - 1, y ], half)
        light([ x + 1, y ], half)
        light([ x, y + 1 ], half)
        light([ x - 1, y - 1], qrtr)
        light([ x - 1, y + 1], qrtr)
        light([ x + 1, y - 1], qrtr)
        light([ x + 1, y + 1], qrtr)

    import math
    
    theta = 0
    
    while theta < 2 * math.pi:
        x = SIZE / 2 + SIZE / 3 * math.cos(theta)
        y = SIZE / 2 + SIZE / 3 * math.sin(theta)
        speck([x, y], [255, 255, 255])

        theta += 0.5

    sys.stdout.write(24b_bmp_header(size, size))
    sys.stdout.write(image_data)
    
if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
