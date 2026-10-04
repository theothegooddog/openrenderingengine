"""Small replacement for the glm functions RIM uses. All matrices are row-major numpy arrays."""
import math

import numpy as np


def identity():
    return np.identity(4, dtype=np.float32)


def perspective(fov_y_degrees, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_y_degrees) / 2.0)
    m = np.zeros((4, 4), dtype=np.float32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2.0 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def translate(v):
    m = identity()
    m[:3, 3] = v
    return m


def scale(v):
    m = identity()
    m[0, 0], m[1, 1], m[2, 2] = v
    return m


def rotate(angle_degrees, axis):
    axis = np.asarray(axis, dtype=np.float64)
    axis = axis / np.linalg.norm(axis)
    x, y, z = axis
    a = math.radians(angle_degrees)
    c, s = math.cos(a), math.sin(a)
    t = 1.0 - c
    m = identity()
    m[:3, :3] = [
        [t * x * x + c,     t * x * y - s * z, t * x * z + s * y],
        [t * x * y + s * z, t * y * y + c,     t * y * z - s * x],
        [t * x * z - s * y, t * y * z + s * x, t * z * z + c],
    ]
    return m


def euler(rotation_degrees):
    """Rotation from (x, y, z) Euler angles in degrees, applied X, then Y, then Z."""
    rx, ry, rz = rotation_degrees
    return rotate(rz, (0, 0, 1)) @ rotate(ry, (0, 1, 0)) @ rotate(rx, (1, 0, 0))
