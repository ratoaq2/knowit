from knowit.units import NullRegistry


def test_null_registry_is_falsey() -> None:
    registry = NullRegistry()
    assert not registry


def test_null_registry_can_define() -> None:
    registry = NullRegistry()
    registry.define('FPS = 1 * hertz')


def test_null_registry_attribute_is_a_scalar_1() -> None:
    registry = NullRegistry()
    assert registry.fps == 1
    assert registry.some_attribute == 1
