"""Port of RIM's main.cpp: a textured cube spinning about (1, 2, 1), plus a few extra objects."""
import sys

from PIL import Image, ImageDraw

from openrenderingengine import Engine


def checkerboard(size=256, squares=8):
    image = Image.new("RGB", (size, size), "white")
    draw = ImageDraw.Draw(image)
    step = size // squares
    for y in range(squares):
        for x in range(squares):
            if (x + y) % 2:
                draw.rectangle([x * step, y * step, (x + 1) * step - 1, (y + 1) * step - 1], fill=(220, 60, 60))
    return image


engine = Engine(600, 600, "RIM")

cube = engine.addObject()
cube.Texture = Image.open(sys.argv[1]) if len(sys.argv) > 1 else checkerboard()

small = engine.addObject(Position=(1.2, 0.8, -1.0), Scale=0.4, Texture=checkerboard(64, 4))


def update(engine, dt):
    t = engine.time
    cube.Rotation = (t * 25, t * 50, t * 25)
    small.Rotation = (0, t * 90, 0)


engine.run(update)
