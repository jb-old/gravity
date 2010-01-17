#!/usr/bin/env python3.1
import json
from random import random

def r():
    return random() * 2 - 1

def gen_object():
    return { "m": 1,
             "d": [ r() * 200, r() * 200 ],
             "v": [ r(), r() ],
             "radius": 2 }

objects = [ gen_object() for _ in range(100) ]

d = { "dimensions": [ 1024, 1024 ],
      "zoom": 1,
      "G": 1,
      "dt": 600,
      "frames": 3001,
      "centre": [0, 0],
      "objects": objects }

print(json.dumps(d))
