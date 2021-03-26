from knowit.units import NullRegistry


def test_null_registry_is_falsey():
    registry = NullRegistry()
    assert not registry


def test_null_registry_can_define():
    registry = NullRegistry()
    registry.define('FPS = 1 * hertz')


def test_null_registry_attribute_is_a_scalar_1():
    registry = NullRegistry()
    assert registry.fps == 1
    assert registry.some_attribute == 1
