"""Version reporting and deployment verification, without network access."""
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from scripts.verify_deployment import (
    SITE_URL,
    main,
    revision_visible,
    wait_for_revision,
)
from src.dashboard.components.version import get_git_revision

SHA = 'a' * 40


@patch('src.dashboard.components.version.subprocess.run')
def test_revision_uses_repository_directory(run):
    run.return_value = SimpleNamespace(stdout=SHA + '\n')
    root = Path(__file__).resolve().parents[1]
    assert get_git_revision(root) == SHA
    assert run.call_args.kwargs['cwd'] == root
    assert run.call_args.kwargs['timeout'] == 2


@pytest.mark.parametrize('output', ['', 'main', 'invalid', 'a' * 39])
@patch('src.dashboard.components.version.subprocess.run')
def test_invalid_revision_is_unknown(run, output):
    run.return_value = SimpleNamespace(stdout=output)
    assert get_git_revision() == 'desconocida'


@pytest.mark.parametrize('error', [OSError(), subprocess.TimeoutExpired('git', 2)])
@patch('src.dashboard.components.version.subprocess.run')
def test_git_unavailable_does_not_break_dashboard(run, error):
    run.side_effect = error
    assert get_git_revision() == 'desconocida'


def fake_frame(url, text, *, title='streamlitApp', src='/~/+/'):
    frame = Mock()
    frame.url = url
    frame.frame_element.return_value.get_attribute.side_effect = lambda name: {
        'title': title, 'src': src,
    }[name]
    frame.get_by_text.side_effect = lambda marker, exact: SimpleNamespace(
        is_visible=lambda: exact and marker == text,
    )
    return frame


def fake_page(*frames, direct_text=''):
    main = fake_frame(SITE_URL, direct_text)
    return SimpleNamespace(main_frame=main, frames=[main, *frames])


def test_revision_visible_on_direct_page():
    assert revision_visible(fake_page(direct_text=f'Versión desplegada: {SHA}'), SHA)


def test_revision_visible_in_authorized_app_frame():
    frame = fake_frame(SITE_URL + '~/+/', f'Versión desplegada: {SHA}')
    assert revision_visible(fake_page(frame), SHA)


@pytest.mark.parametrize(('url', 'title', 'src', 'text'), [
    ('https://qjmnz4vd2y07.statuspage.io/embed/frame', 'streamlitApp',
     'https://qjmnz4vd2y07.statuspage.io/embed/frame', f'Versión desplegada: {SHA}'),
    (SITE_URL + '~/+/', 'status', '/~/+/', f'Versión desplegada: {SHA}'),
    (SITE_URL + '~/+/', 'streamlitApp', '/~/+/', f'Versión desplegada: {SHA[:-1]}b'),
    (SITE_URL + 'other', 'streamlitApp', '/other', f'Versión desplegada: {SHA}'),
    (SITE_URL + '~/+/', 'streamlitApp', 'https://evil.example/~/+/', f'Versión desplegada: {SHA}'),
])
def test_revision_rejects_untrusted_frame_or_wrong_marker(url, title, src, text):
    assert not revision_visible(fake_page(fake_frame(url, text, title=title, src=src)), SHA)


def test_revision_still_loading_is_not_a_match():
    assert not revision_visible(fake_page(fake_frame('about:blank', '')), SHA)


def test_probe_does_not_reload_while_app_is_starting(monkeypatch):
    page = Mock()
    browser = Mock()
    browser.new_page.return_value = page
    playwright = Mock()
    playwright.chromium.launch.return_value = browser
    context = Mock(__enter__=Mock(return_value=playwright), __exit__=Mock())
    module = SimpleNamespace(Error=RuntimeError, sync_playwright=lambda: context)
    monkeypatch.setitem(sys.modules, 'playwright.sync_api', module)
    monkeypatch.setenv('EXPECTED_SHA', SHA)

    def check_twice(probe, expected):
        assert not probe(expected)
        assert probe(expected)

    with patch('scripts.verify_deployment.wait_for_revision', side_effect=check_twice), \
         patch('scripts.verify_deployment.revision_visible', side_effect=[False, True]), \
         patch('scripts.verify_deployment.time.monotonic', side_effect=[0, 1]):
        main()
    assert page.goto.call_count == 1
    browser.close.assert_called_once()


def test_verifier_waits_for_exact_revision():
    now = [0.0]
    probe = Mock(side_effect=[False, True])
    wait_for_revision(probe, SHA, timeout=10, interval=1,
                      clock=lambda: now[0], sleep=lambda n: now.__setitem__(0, now[0] + n))
    assert probe.call_count == 2
    probe.assert_called_with(SHA)


def test_old_revision_cannot_pass_verification():
    now = [0.0]
    probe = Mock(return_value=False)
    with pytest.raises(TimeoutError):
        wait_for_revision(probe, SHA, timeout=2, interval=1,
                          clock=lambda: now[0], sleep=lambda n: now.__setitem__(0, now[0] + n))
    assert probe.call_count == 2


@pytest.mark.parametrize('value', ['', 'main', 'a' * 39, 'x' * 40])
def test_verifier_rejects_invalid_commit(value):
    probe = Mock()
    with pytest.raises(ValueError):
        wait_for_revision(probe, value)
    probe.assert_not_called()
