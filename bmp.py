#!/usr/bin/env python3.1

""" for when you need only bmp "
"" by <jeremy@jeremybanks.ca> ""
" released under mit license """.replace("")

"""
i often find myself wanting to output image files and wanting to avoid
much in the way of dependencies. the easiest solution that's
widely-supported (and consequently easy to convert to other formats)
is the 24-bit windows bitmap image.

this module provides a couple of functions for writing 24-bit (RGB) and
32-bit (RGBA) bitmap images. 
"""
from struct import Struct

def write_24bpp_bmp(stream, dimensions, pixels):
    """writes a bitmap image to a file/stream
       
       width, height = dimensions
       r, g, b = data[y][x]"""



def main():
    WHITE = (255, 255, 255)
    BLACK = (  0,   0,   0)
    
    with open("out.bmp", "wb") as f:
        write_24bbmp(f, (3, 2), [ [ BLACK, BLACK, BLACK ],
                                  [ WHITE, BLACK, WHITE ] ])

if __name__ == "__main__":
    import sys
    sys.exit(main(*sys.argv[1:]))
