"""Check that a bug report can be turned back into fixtures.

This closes the loop the reporting flow depends on: a user runs `knowit --bug-report`,
attaches the file, and the maintainer replays it as a test without ever getting the
media file.
"""

import importlib.util
import json
import os
import pathlib
import sys
import typing

import pytest
import yaml

from knowit.bugreport import build_report, dump_report


def _load_importer() -> typing.Any:
    """Load scripts/import_report.py, which is a dev script and not part of the package."""
    script = pathlib.Path(__file__).parent.parent / 'scripts' / 'import_report.py'
    spec = importlib.util.spec_from_file_location('import_report', script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules['import_report'] = module
    spec.loader.exec_module(module)
    return module


import_report_script = _load_importer()


@pytest.fixture
def report(options: dict[str, typing.Any]) -> dict[str, typing.Any]:
    return build_report(['tests/data/videos/test1.mkv'], options)


def test_strip_version_removes_only_the_version() -> None:
    # When
    result = import_report_script._strip_version({'provider': {'name': 'ffmpeg', 'version': {'a': 'b'}}})

    # Then
    assert result == {'provider': {'name': 'ffmpeg'}}


def test_import_report_writes_a_fixture_pair(
    report: dict[str, typing.Any],
    tmp_path: pathlib.Path,
) -> None:
    # When
    written = import_report_script.import_report(report, 'issue-1-example', data_root=str(tmp_path))

    # Then
    assert written
    for path in written:
        assert os.path.isfile(path)
    assert any(path.endswith('.json') for path in written)
    assert any(path.endswith('.yml') for path in written)


def test_imported_raw_fixture_is_pure_ascii(
    report: dict[str, typing.Any],
    tmp_path: pathlib.Path,
) -> None:
    # Given a fixture must read back the same under any locale
    written = import_report_script.import_report(report, 'issue-1-example', data_root=str(tmp_path))

    # Then
    for path in written:
        if path.endswith('.json'):
            assert pathlib.Path(path).read_bytes().isascii()


def test_imported_expected_fixture_has_no_provider_version(
    report: dict[str, typing.Any],
    tmp_path: pathlib.Path,
) -> None:
    # Given
    written = import_report_script.import_report(report, 'issue-1-example', data_root=str(tmp_path))

    # Then
    for path in written:
        if path.endswith('.yml'):
            expected = yaml.safe_load(pathlib.Path(path).read_text(encoding='utf-8'))
            assert 'version' not in (expected.get('provider') or {})


def test_import_report_does_not_overwrite_by_default(
    report: dict[str, typing.Any],
    tmp_path: pathlib.Path,
) -> None:
    # Given
    import_report_script.import_report(report, 'issue-1-example', data_root=str(tmp_path))

    # When
    written = import_report_script.import_report(report, 'issue-1-example', data_root=str(tmp_path))

    # Then
    assert written == []


def test_import_report_overwrites_when_asked(
    report: dict[str, typing.Any],
    tmp_path: pathlib.Path,
) -> None:
    # Given
    first = import_report_script.import_report(report, 'issue-1-example', data_root=str(tmp_path))

    # When
    second = import_report_script.import_report(report, 'issue-1-example', overwrite=True, data_root=str(tmp_path))

    # Then
    assert second == first


def test_import_report_numbers_several_files(
    options: dict[str, typing.Any],
    tmp_path: pathlib.Path,
) -> None:
    # Given
    several = build_report(['tests/data/videos/test1.mkv', 'tests/data/videos/test2.mkv'], options)

    # When
    written = import_report_script.import_report(several, 'issue-1-example', data_root=str(tmp_path))

    # Then
    assert any('issue-1-example-01.mkv' in path for path in written)
    assert any('issue-1-example-02.mkv' in path for path in written)


def test_main_rejects_a_file_that_is_not_a_report(tmp_path: pathlib.Path) -> None:
    # Given
    not_a_report = tmp_path / 'other.yml'
    not_a_report.write_text('hello: world\n', encoding='utf-8')

    # Then
    assert import_report_script.main([str(not_a_report)]) == 1


def test_main_imports_a_written_report(
    report: dict[str, typing.Any],
    tmp_path: pathlib.Path,
) -> None:
    # Given
    report_file = tmp_path / 'knowit-report.yml'
    report_file.write_text(dump_report(report), encoding='utf-8')
    data_root = tmp_path / 'data'

    # When
    code = import_report_script.main([str(report_file), '--issue', '220', '--data-root', str(data_root)])

    # Then
    assert code == 0
    written = sorted(path.name for path in data_root.rglob('*.json'))
    assert written
    for path in data_root.rglob('*.json'):
        json.loads(path.read_text(encoding='utf-8'))
