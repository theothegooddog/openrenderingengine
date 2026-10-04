import numpy as np
import pytest
from PIL import Image

from openrenderingengine import Engine, transforms
from openrenderingengine.engine import Object


@pytest.fixture(scope="module")
def engine():
    try:
        e = Engine(64, 64, visible=False)
    except Exception as exc:  # no display / GL available
        pytest.skip(f"no OpenGL context: {exc}")
    yield e
    e.close()


def test_add_object_returns_object(engine):
    obj = engine.addObject()
    assert isinstance(obj, Object)
    assert obj in engine.objects
    engine.removeObject(obj)


def test_properties_roundtrip(engine):
    obj = engine.addObject()
    obj.Position = [1, 2, 3]
    obj.Rotation = (10, 20, 30)
    obj.Scale = 2
    assert obj.Position == (1.0, 2.0, 3.0)
    assert obj.Rotation == (10.0, 20.0, 30.0)
    assert obj.Scale == (2.0, 2.0, 2.0)
    with pytest.raises(ValueError):
        obj.Position = (1, 2)
    with pytest.raises(TypeError):
        obj.Texture = 42
    engine.removeObject(obj)


def test_texture_is_rendered(engine):
    obj = engine.addObject()
    obj.Texture = Image.new("RGB", (8, 8), (0, 255, 0))
    pixel = engine.screenshot().getpixel((32, 32))
    assert pixel[:3] == (0, 255, 0)

    obj.Texture = Image.new("RGB", (8, 8), (0, 0, 255))
    assert engine.screenshot().getpixel((32, 32))[:3] == (0, 0, 255)
    engine.removeObject(obj)


def test_position_moves_object(engine):
    obj = engine.addObject(Texture=Image.new("RGB", (4, 4), (255, 0, 0)))
    assert engine.screenshot().getpixel((32, 32))[:3] == (255, 0, 0)
    obj.Position = (10, 0, 0)
    assert engine.screenshot().getpixel((32, 32))[:3] == (0, 0, 0)
    engine.removeObject(obj)


def test_euler_matches_axis_rotation():
    m = transforms.euler((0, 90, 0))
    np.testing.assert_allclose(m[:3, :3] @ [1, 0, 0], [0, 0, -1], atol=1e-6)
