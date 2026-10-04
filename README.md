# openrenderingengine
rendering engine for openphysicsengine

A Python port of [RIM](https://github.com/m-saliola/RIM) (C++/OpenGL 3.3) using `glfw`, `PyOpenGL`, `numpy` and `Pillow`.

## Install

```sh
pip install -e .
```

## Usage

```python
from PIL import Image
from openrenderingengine import Engine

engine = Engine(600, 600, "RIM")

cube = engine.addObject()                 # returns an Object (a cube by default)
cube.Position = (0, 0, 0)                 # world units
cube.Rotation = (0, 45, 0)                # Euler degrees, applied X then Y then Z
cube.Scale = 1.5                          # a number or (x, y, z)
cube.Texture = Image.open("crate.png")    # a PIL.Image, a file path, or None for white

def update(engine, dt):
    cube.Rotation = (0, engine.time * 45, 0)

engine.run(update)
```

You can also pass properties up front: `engine.addObject(Position=(1, 0, 0), Texture=img)`.
`add_object` / `remove_object` are snake_case aliases.

Other `Engine` members:

| | |
|---|---|
| `removeObject(obj)` | remove an object and free its texture |
| `objects` | list of objects in the scene |
| `CameraPosition` | camera position, default `(0, 0, 3)` looking down -Z |
| `FieldOfView` | vertical FOV in degrees, default 45 |
| `Background` | clear colour `(r, g, b, a)` in 0..1 |
| `screenshot()` | render a frame and return a `PIL.Image` (works with `visible=False`) |
| `step()` / `run(update)` | draw one frame / run the main loop |

Other meshes: `engine.addObject(mesh=openrenderingengine.plane(2.0))`, or build your own
`Mesh(vertices, indices)` with `(x, y, z, u, v)` per vertex.

The low-level RIM classes are ported too: `Shader`, `Texture`, `VertexArray`, `VertexBuffer`,
`VertexBufferLayout`, `IndexBuffer`.

## Example and tests

```sh
python examples/spinning_cube.py [image]
pytest            # on a headless machine: xvfb-run -a pytest
```
