import os

import glfw
import numpy as np
from OpenGL import GL
from PIL import Image

from . import mesh as meshes
from . import transforms
from .shader import Shader
from .texture import Texture

SHADER_DIR = os.path.join(os.path.dirname(__file__), "shaders")


def _vec3(value, name):
    try:
        x, y, z = value
        return (float(x), float(y), float(z))
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a sequence of 3 numbers, got {value!r}") from None


class Object:
    """A renderable object returned by `Engine.addObject()`.

    Position: (x, y, z) world units
    Rotation: (x, y, z) Euler angles in degrees, applied X, then Y, then Z
    Scale:    (x, y, z) multipliers
    Texture:  a PIL.Image, an image file path, or None for plain white
    """

    def __init__(self, engine, mesh):
        self._engine = engine
        self.Mesh = mesh
        self._position = (0.0, 0.0, 0.0)
        self._rotation = (0.0, 0.0, 0.0)
        self._scale = (1.0, 1.0, 1.0)
        self._texture_source = None
        self._texture = None
        self._texture_dirty = False
        self.Visible = True

    @property
    def Position(self):
        return self._position

    @Position.setter
    def Position(self, value):
        self._position = _vec3(value, "Position")

    @property
    def Rotation(self):
        return self._rotation

    @Rotation.setter
    def Rotation(self, value):
        self._rotation = _vec3(value, "Rotation")

    @property
    def Scale(self):
        return self._scale

    @Scale.setter
    def Scale(self, value):
        if isinstance(value, (int, float)):
            value = (value, value, value)
        self._scale = _vec3(value, "Scale")

    @property
    def Texture(self):
        return self._texture_source

    @Texture.setter
    def Texture(self, value):
        if value is not None and not isinstance(value, (Image.Image, str, os.PathLike)):
            raise TypeError(f"Texture must be a PIL.Image, a file path, or None, got {type(value).__name__}")
        if isinstance(value, (str, os.PathLike)):
            value = Image.open(value)
            value.load()
        # Always re-upload, so re-assigning an image you edited in place refreshes it
        self._texture_source = value
        self._texture_dirty = True

    @property
    def ModelMatrix(self):
        return (transforms.translate(self._position)
                @ transforms.euler(self._rotation)
                @ transforms.scale(self._scale))

    def _gpu_texture(self):
        if self._texture_dirty:
            if self._texture is not None:
                self._texture.delete()
                self._texture = None
            if self._texture_source is not None:
                self._texture = Texture(self._texture_source)
            self._texture_dirty = False
        return self._texture or self._engine._white_texture

    def _release(self):
        if self._texture is not None:
            self._texture.delete()
            self._texture = None

    def remove(self):
        self._engine.removeObject(self)


class Engine:
    def __init__(self, width=600, height=600, title="RIM", visible=True, background=(0.0, 0.0, 0.0, 1.0)):
        if not glfw.init():
            raise RuntimeError("Failed to initialize GLFW")

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)
        glfw.window_hint(glfw.VISIBLE, glfw.TRUE if visible else glfw.FALSE)

        self._window = glfw.create_window(width, height, title, None, None)
        if not self._window:
            glfw.terminate()
            raise RuntimeError("Failed to create GLFW window")

        glfw.make_context_current(self._window)
        glfw.set_framebuffer_size_callback(self._window, self._on_resize)

        GL.glEnable(GL.GL_DEPTH_TEST)

        self._shader = Shader(os.path.join(SHADER_DIR, "texture.vsh"), os.path.join(SHADER_DIR, "texture.fsh"))
        self._white_texture = Texture(Image.new("RGBA", (1, 1), (255, 255, 255, 255)))
        self._cube = meshes.cube()
        self._objects = []

        self.Background = background
        self.CameraPosition = (0.0, 0.0, 3.0)
        self.FieldOfView = 45.0

        fb_width, fb_height = glfw.get_framebuffer_size(self._window)
        self._on_resize(self._window, fb_width, fb_height)

    def _on_resize(self, window, width, height):
        GL.glViewport(0, 0, width, height)
        self._size = (max(width, 1), max(height, 1))

    # --- scene ---

    def addObject(self, mesh=None, Position=None, Rotation=None, Scale=None, Texture=None):
        """Add an object to the scene (a cube unless `mesh` is given) and return it."""
        obj = Object(self, mesh or self._cube)
        if Position is not None:
            obj.Position = Position
        if Rotation is not None:
            obj.Rotation = Rotation
        if Scale is not None:
            obj.Scale = Scale
        if Texture is not None:
            obj.Texture = Texture
        self._objects.append(obj)
        return obj

    add_object = addObject

    def removeObject(self, obj):
        self._objects.remove(obj)
        obj._release()

    remove_object = removeObject

    @property
    def objects(self):
        return list(self._objects)

    @property
    def time(self):
        return glfw.get_time()

    @property
    def should_close(self):
        return glfw.window_should_close(self._window)

    # --- rendering ---

    def render(self):
        """Draw one frame into the back buffer."""
        glfw.make_context_current(self._window)
        GL.glClearColor(*self.Background)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        width, height = self._size
        proj = transforms.perspective(self.FieldOfView, width / height, 0.1, 100.0)
        view = transforms.translate([-c for c in self.CameraPosition])

        self._shader.bind()
        self._shader.set_int("u_Texture", 0)
        self._shader.set_mat4("u_View", view)
        self._shader.set_mat4("u_Proj", proj)

        for obj in self._objects:
            if not obj.Visible:
                continue
            obj._gpu_texture().bind(0)
            self._shader.set_mat4("u_Model", obj.ModelMatrix)
            obj.Mesh.bind()
            GL.glDrawElements(GL.GL_TRIANGLES, obj.Mesh.index_count, GL.GL_UNSIGNED_INT, None)

    def screenshot(self):
        """Render a frame and return it as a PIL.Image (works with a hidden window)."""
        self.render()
        width, height = self._size
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 1)
        data = GL.glReadPixels(0, 0, width, height, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE)
        pixels = np.frombuffer(data, dtype=np.uint8).reshape(height, width, 4)
        return Image.fromarray(pixels[::-1].copy(), "RGBA")

    def step(self):
        """Render one frame, present it, and process window events."""
        self.render()
        glfw.swap_buffers(self._window)
        glfw.poll_events()

    def run(self, update=None):
        """Main loop. `update(engine, dt)` is called once per frame before drawing."""
        last = self.time
        while not self.should_close:
            now = self.time
            if update is not None:
                update(self, now - last)
            last = now
            self.step()
        self.close()

    def close(self):
        if self._window is None:
            return
        glfw.make_context_current(self._window)
        for obj in self._objects:
            obj._release()
        self._objects.clear()
        self._cube.delete()
        self._white_texture.delete()
        self._shader.delete()
        glfw.destroy_window(self._window)
        self._window = None
        glfw.terminate()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
