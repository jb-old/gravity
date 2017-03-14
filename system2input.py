#!/usr/bin/env python3
from copy import copy, deepcopy
from gravity import V#ector
from math import pi as PI
import json
import sys

def system_to_input(system):
    """generates input for gravity.py from a dictionary representing an orbital system"""
    
    if len(system) != 1:
        raise ValueError("Input system must have a single root body.")
    
    result_objects = []
    
    def add_objects(objects, position_orbiting=V(0, 0), velocity_orbiting=V(0, 0)):
        for name, object_dict in objects.items():
            object = { "comment": name,
                       "m": object_dict["mass"],
                       "radius": object_dict["mean radius"] }
            if "orbit" in object_dict:
                object.update({ "v": V(0, object_dict["orbit"]["semi-major axis"] * 2 * PI / object_dict["orbit"]["period"]) + velocity_orbiting,
                                "d": V(object_dict["orbit"]["semi-major axis"] * (1 - object_dict["orbit"]["eccentricity"]), 0) + position_orbiting })
            else:
                object["v"] = V(0, 0)
                object["d"] = deepcopy(position_orbiting)
            
            # this is pretty far from accurate at the moment
            
            result_objects.append(object)

            if "satellites" in object_dict:
                add_objects(object_dict["satellites"], object["d"], object["v"])
    
    add_objects(system)
    
    return { "objects": result_objects }

def main(in_filename="-", out_filename="-"):
    in_file  = open(in_filename,  "rt") if in_filename  != "-" else sys.stdin
    out_file = open(out_filename, "wt") if out_filename != "-" else sys.stdout
    
    with in_file, out_file:
        in_dict = json.load(in_file)
        out_dict = system_to_input(in_dict)
        json.dump(out_dict, out_file, indent=2, default=list)

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
