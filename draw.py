#!/usr/bin/env python3.1

SIZE = 512
CHANNELS = 3

def main():
    image_data = bytearray(CHANNELS * SIZE ** 2) # black "image"
    
    def light(position, color, opacity=1):
        print(position)
        if not all(0 <= p < SIZE for p in position):
            print("(denied)")
            return # out of bounds
            
        color = bytearray(int(255 - (255 - channel) * opacity) for channel in color)
        
        for c in range(CHANNELS):
            i = int(CHANNELS * (position[0] + position[1] * SIZE) + c)
            image_data[i] = max(image_data[i], color[i])
    
    def speck(position, color):
        light(position, color)
        light([ position[0],
                position[1] - 1 ], color, .5)
        light([ position[0] - 1,
                position[1] ], color, .5)
        light([ position[0] + 1,
                position[1] ], color, .5)
        light([ position[0],
                position[1] + 1 ], color, .5)

    import math
    
    theta = 0
    
    while theta < 2 * math.pi:
        x = SIZE / 2 + SIZE / 2 * math.cos(theta)
        y = SIZE / 2 + SIZE / 2 * math.sin(theta)
        speck([x, y], [255, 255, 255])

    print(image_data)
    
if __name__ == "__main__":
    main()
