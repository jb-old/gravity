#!/usr/bin/env python3.1

SIZE = 512
CHANNELS = 3

def main():
    image_data = bytearray(CHANNELS * SIZE ** 2) # black "image"
    
    def light(position, color, opacity=1):
        if any(not (0 <= p < SIZE) for p in position):
            return # out of bounds
            
        color = [255 - (255 - channel) * opacity for channel in color]
        
        for c in CHANNELS:
            i = CHANNELS * (position[0] + position[1] * SIZE) + c
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
        print(int(abs(math.sin(theta)) * 20) * "-")
        theta += .1
    
if __name__ == "__main__":
    main()
