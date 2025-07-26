# Need to import knowit to check if it changes the default behavior of pyyaml
import yaml


def test_unchanged_pyyaml() -> None:
    ret = yaml.safe_load('value: 0.5')
    assert isinstance(ret, dict)
    assert "value" in ret
    assert ret["value"] == 0.5
