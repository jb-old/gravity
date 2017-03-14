#!/usr/bin/env python3
import json
from random import random

def r():
    return random() * 2 - 1

N = 100
d_max = 200
v_max = 1

def gen_object():
    return { "m": 1,
             "d": [ r() * d_max, r() * d_max ],
             "v": [ r() * v_max, r() * v_max ],
             "radius": 2 }

print(json.dumps({ "dimensions": [ 1024, 1024 ],
                   "zoom": 1,
                   "G": 1,
                   "dt": 600,
                   "frames": 3001,
                   "centre": [0, 0],
                   "objects": [ gen_object() for _ in range(N) ] }))
