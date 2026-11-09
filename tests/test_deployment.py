"""Version reporting and deployment verification, without network access."""
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from scripts.verify_deployment import wait_for_revision
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
