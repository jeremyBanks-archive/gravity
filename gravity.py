#!/usr/bin/env python3.1
import itertools

class Vector(object):
    """A Vector value of any number of dimensions."""
    
    def __init__(self, components):
        self.components = list(components)

    @property
    def magnitude(self):
        return sum(x ** 2 for x in self.components) ** (1/2)
    
    @magnitude.setter
    def magnitude(self, value):
        self *= value / self.magnitude
    
    def __getitem__(self, index):
        return self.components[index]
    
    def __setitem__(self, index, value):
        self.components[index] = value
    
    def __add__(self, vector):
        return type(self)(a + b for (a, b) in itertools.zip_longest(self.components, vector.components, fillvalue=0))
    
    def __sub__(self, vector):
        return type(self)(a - b for (a, b) in itertools.zip_longest(self.components, vector.components, fillvalue=0))
    
    def __mul__(self, scalar):
        return type(self)(x * scalar for x in self.components)

    __rmul__ = __mul__
    
    def __truediv__(self, scalar):
        return type(self)(x / scalar for x in self.components)

    def __neg__(self):
        return type(self)(-x for x in self.components)

    def __iter__(self):
        return iter(self.components)

    def __bool__(self):
        return any(self)

    def __eq__(self, other):
        return self.components == other.components

    def __repr__(self):
        return "V({})".format(", ".join(repr(v) for v in self.components))

    # use shifts to repr rotations cw and ccw

def V(*components):
    """Shortcut for creating Vectors: V(x, y...) -> Vector((x, y...))"""
    
    return Vector(components)

from copy import copy, deepcopy

class Object(object):
    """A non-elastic frictionless sphere in a vaccum, ha."""
    
    def __init__(self, mass, displacement, velocity, radius=None, combining=True):
        self.mass = mass
        self.displacement = Vector(displacement)
        self.velocity = Vector(velocity)
        
        if radius is None:
            self.radius = 2 * self.mass ** (1/2)
        else:
            self.radius = radius

        self.combining = bool(combining)
    
    @classmethod
    def from_dict(cls, source_dict,
                  default_dict = { "m": 1, "d": [ 0, 0 ], "v": [ 0, 0 ],
                                   "radius": None, "combining": True }):
        input_dict = deepcopy(default_dict)
        input_dict.update(source_dict)
        return cls(input_dict["m"], input_dict["d"], input_dict["v"], input_dict["radius"], input_dict["combining"])

    def __repr__(self):
        return ("{.__name__}(mass={!r}, displacement={!r}, velocity={!r})"
                .format(type(self), self.mass, self.displacement, self.velocity))

def simulate(current, time_step, G=6.67428e-11):
    """From an initial situation, infinitely yield the following frames."""
    dt_per_frame = dt / frames
    
    while True:
        next = deepcopy(current)
        
        for object, other in itertools.combinations(current):
            displacement = other.displacement - object.displacement
            
            if displacement.magnitude > .5:
                acceleration_magnitude = G * other.mass / displacement.magnitude ** 2
                
                x_portion = displacement[0] / sum(abs(v) for v in displacement)
                y_portion = displacement[1] / sum(abs(v) for v in displacement)
                
                acceleration = V(x_portion * acceleration_magnitude,
                                 y_portion * acceleration_magnitude)
                
                object.velocity = new_object.velocity + acceleration * dt_per_frame
        
        for object in current:
            object.displacement += new_object.velocity * dt_per_frame
        
        # combing colliding combining objects
        for i, object in enumerate(next):
            if object is None or not object.combining: continue
            
            for j, other in enumerate(next[i + 1:]):
                if other is None or not other.combining: continue
                
                displacement = other.displacement - object.displacement
                
                if displacement.magnitude < min(object.radius, other.radius):
                    object_portion = object.mass / (object.mass + other.mass)
                    other_portion  = other.mass  / (other.mass + other.mass)
                    
                    combined_object = Object(object.mass + other.mass,
                                             object_portion * object.displacement + other_portion * other.displacement,
                                             object_portion * object.velocity     + other_portion * other.velocity,
                                             (object.radius ** 2 + other.radius ** 2) ** (1/2))
                    
                    next[i] = object = combined_object
                    next[i + 1 + j] = other = None
            
            if None in next:
                next = [ o for o in next if o is not None ]
        
        current = next

import random

def starify_raster(raster, n=200):
    """Draws background-ish "stars" on a Raster image."""
    
    for _ in range(n):
        x = random.random() * (raster.width + 4) - 2
        y = random.random() * (raster.height + 4) - 2
        
        r, g, b = [ .6 + .2 * random.random() + .2 * random.random() for _ in range(3) ]
        
        g = min(r, g, b) # ensure green is never above red or blue
        # maybe I could draw colours from a gradient instead, and use one limiting green by default?

        raster.dot([x, y], [r, g, b], random.random() * .7, radius=random.random())

import sys
import raster
import json

raster.Raster.starify = starify_raster

def main(in_filename="-", out_filename="-"):
    in_file  = open(in_filename,  "rt") if in_filename  != "-" else sys.stdin
    out_file = open(out_filename, "wb") if out_filename != "-" else sys.stdout.buffer
    
    # later I should add many more rendering control options to this, but this will do to start
    input_defaults = { "comment": None, # it's a comment, ignored
                       "dimensions": [ 1024, 512 ], # size of output image, and unzoomed view area in metres
                       "G": 6.67428e-11, # gravitational constant
                       "dt": 60 * 60 * 24 * 365, # duration in render in seconds
                       "frames": 501, # drawing "frames" to use
                       "ticks_per_frame": 20, # how many physics frames to use for each image frame
                       "objects": [], # objects in system we're rendering
                       "centre": [0, 0], # centre of view
                       "zoom": 1e-10 } # factor of magnification
    # todo: make values realistic
    
    with in_file, out_file:
        input_dict = deepcopy(input_defaults)
        input_dict.update(json.load(in_file))
        
        width, height = dimensions = input_dict["dimensions"]
        offset = V(width / 2 + .5, height / 2 + .5)
        
        frames = input_dict["frames"]
        frame_dt = input_dict["dt"] / ((input_dict["frames"] - 1) or 1)
        centre = Vector(input_dict["centre"])
        zoom = input_dict["zoom"]
        
        sys.stderr.write("Loading input system...\n")
        system = System(Object.from_dict(d) for d in input_dict["objects"])
        
        sys.stderr.write("Instantiating image...\n")
        image = raster.Raster_24RGB(width, height, fill=[0, 0, 0], pen=raster.PEN_MAX)
        sys.stderr.write("Rendering background \"stars\"...\n")
        image.starify(int((width * height) / 100))
        
        def callback(frame, old, new):
            if frame % input_dict["ticks_per_frame"] != 0:
                return
            
            r, g, b, a = raster.mah_spectrum(frame / (frames - 1) if frames > 1 else .5)
            sys.stderr.write("Calculuated, rendering frame {}...\r".format(frame))
            sys.stderr.flush()
            
            if a:
                for object in new:
                    dot_position = (object.displacement - centre) * zoom + offset
                    dot_radius = object.radius * zoom
                    
                    image.dot(dot_position, [r, g, b], a, radius=dot_radius)
        
        callback(0, None, system) # to draw input frame
        system = system.advanced(input_dict["dt"], input_dict["frames"] * input_dict["ticks_per_frame"], input_dict["G"], callback)

        sys.stderr.write("\n")
        sys.stderr.write("Writing image to file...")
        image.write_bmp(out_file)
    
if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))

