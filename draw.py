#!/usr/bin/env python3.1

SIZE = 36
CHANNELS = 3

def main():
    image_data = bytearray(CHANNELS * SIZE ** 2) # black "image"
    
    def light(position, color, opacity=1):
        if not all(0 <= p < SIZE for p in position):
            return # out of bounds
            
        color = bytearray(int(channel * opacity) for channel in color)
        
        for c in range(CHANNELS):
            i = int(CHANNELS * (position[0] + position[1] * SIZE) + c)
            image_data[i] = max(image_data[i], color[c])
    
    def speck(position, color):
        light(position, color)
        
        x, y = position
        
        light([ x, y - 1 ], color, .5)
        light([ x - 1, y ], color, .5)
        light([ x + 1, y ], color, .5)
        light([ x, y + 1 ], color, .5)

    import math
    
    theta = 0
    
    while theta < 2 * math.pi:
        x = SIZE / 2 + SIZE / 3 * math.cos(theta)
        y = SIZE / 2 + SIZE / 3 * math.sin(theta)
        speck([x, y], [255, 255, 255])

        theta += 0.5

    print("=" * SIZE)
    print("".join("-" if i else " " for i in image_data[1::CHANNELS]))
    
if __name__ == "__main__":
    main()
