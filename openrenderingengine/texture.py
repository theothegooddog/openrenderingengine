import numpy as np
from OpenGL import GL
from PIL import Image


class Texture:
    _bound_id = 0

    def __init__(self, image):
        """`image` is a file path or a PIL.Image."""
        if not isinstance(image, Image.Image):
            image = Image.open(image)
        image = image.convert("RGBA").transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        self._width, self._height = image.size
        data = np.asarray(image, dtype=np.uint8)

        self._id = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self._id)
        Texture._bound_id = self._id

        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, self._width, self._height, 0,
                        GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, data)
        GL.glGenerateMipmap(GL.GL_TEXTURE_2D)

    def delete(self):
        if Texture._bound_id == self._id:
            Texture._bound_id = 0
        GL.glDeleteTextures(1, [self._id])

    def bind(self, slot=0):
        if Texture._bound_id != self._id:
            GL.glActiveTexture(GL.GL_TEXTURE0 + slot)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self._id)
            Texture._bound_id = self._id

    def unbind(self):
        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        Texture._bound_id = 0

    @property
    def id(self):
        return self._id

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height
