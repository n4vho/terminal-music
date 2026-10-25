import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'bin/terminal-music'
loader = importlib.machinery.SourceFileLoader('terminal_music', str(SOURCE))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)


def archive(name='soloist', content=b'executable', kind=None):
    result = io.BytesIO()
    with tarfile.open(fileobj=result, mode='w:gz') as file:
        member = tarfile.TarInfo(name)
        if kind:
            member.type = kind
            member.linkname = '/etc/passwd'
            file.addfile(member)
        else:
            member.size = len(content)
            file.addfile(member, io.BytesIO(content))
    return result.getvalue()


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        for attr, relative in [('CONFIG', 'config'), ('DATA', 'data'), ('STATE', 'state'),
                               ('CACHE', 'cache'), ('KEY', 'config/api-key'),
                               ('SETTINGS', 'config/settings.json'),
                               ('SPOT_CONFIG', 'config/spotatui.yml'), ('SOLOIST_DATA', 'data/soloist')]:
            patcher = patch.object(m, attr, base / relative)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_config_disables_only_behavior_streaming(self):
        text = 'behavior:\n  enable_streaming: true\n  tick_rate: 250\ntheme:\n  preset: Cyan\n'
        result = m.streaming_disabled(text)
        self.assertIn('enable_streaming: false', result)
        self.assertIn('  tick_rate: 250\ntheme:', result)
        self.assertEqual(result, m.streaming_disabled(result))

    def test_config_adds_behavior_without_overwriting_other_sections(self):
        self.assertEqual(m.streaming_disabled('theme:\n  preset: Cyan\n'),
                         'theme:\n  preset: Cyan\nbehavior:\n  enable_streaming: false\n')

    def test_atomic_write_replaces_with_private_file(self):
        m.private_dirs()
        m.atomic_write(m.KEY, 'example-only')
        self.assertEqual(m.KEY.stat().st_mode & 0o777, 0o600)
        self.assertEqual(m.CONFIG.stat().st_mode & 0o777, 0o700)

    def test_extracts_only_executable_and_cannot_write_outside_destination(self):
        target = m.DATA / 'bin/soloist'
        m.install_archive(archive('../../soloist', b'valid'), 'soloist', target)
        self.assertEqual(target.read_bytes(), b'valid')
        self.assertEqual(target.stat().st_mode & 0o777, 0o755)
        self.assertFalse((Path(self.temp.name) / 'soloist').exists())

    def test_archive_symlink_is_rejected(self):
        with self.assertRaises(RuntimeError):
            m.install_archive(archive(kind=tarfile.SYMTYPE), 'soloist', m.DATA / 'soloist')

    def test_archive_missing_binary_is_rejected(self):
        with self.assertRaises(RuntimeError):
            m.install_archive(archive('wrong'), 'soloist', m.DATA / 'soloist')

    def test_download_requires_https(self):
        with self.assertRaises(RuntimeError):
            m.fetch('http://example.com/binary')

    def test_setup_without_tty_does_not_read_key(self):
        args = type('Args', (), {'reset_key': False, 'name': None})()
        with patch.object(m, 'install_players'), patch.object(m.sys.stdin, 'isatty', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'interactively'):
                m.setup(args)
        self.assertFalse(m.KEY.exists())

    def test_setup_stores_key_without_touching_original_config(self):
        args = type('Args', (), {'reset_key': False, 'name': 'Test Speaker'})()
        original = Path(self.temp.name) / 'original/spotatui/config.yml'
        original.parent.mkdir(parents=True)
        original.write_text('behavior:\n  enable_streaming: true\n')
        with patch.object(m, 'install_players'), patch.object(m.sys.stdin, 'isatty', return_value=True), \
             patch.object(m.getpass, 'getpass', return_value='test-only-key'), \
             patch.object(m, 'root', return_value=original.parent.parent):
            m.setup(args)
        self.assertIn('enable_streaming: true', original.read_text())
        self.assertIn('enable_streaming: false', m.SPOT_CONFIG.read_text())
        self.assertEqual(json.loads(m.SETTINGS.read_text())['device_name'], 'Test Speaker')
        self.assertEqual(m.KEY.read_text(), 'test-only-key\n')

    def test_existing_daemon_is_reused_without_launch(self):
        m.private_dirs()
        m.atomic_write(m.KEY, 'test-only-key')
        m.atomic_write(m.SETTINGS, '{}')
        with patch.object(m, 'running', return_value=True), patch.object(m.subprocess, 'Popen') as launch:
            m.start()
            launch.assert_not_called()

    def test_start_reports_early_expired_build_and_private_logs(self):
        m.private_dirs()
        m.atomic_write(m.KEY, 'test-only-key')
        m.atomic_write(m.SETTINGS, '{"device_name":"Test"}')
        with patch.object(m, 'running', return_value=False), patch.object(m, 'binary', return_value='/soloist'), \
             patch.object(m.subprocess, 'Popen') as launch:
            launch.return_value.poll.return_value = 10
            with self.assertRaisesRegex(RuntimeError, 'code 10'):
                m.start()
            self.assertIn('127.0.0.1:0', launch.call_args.args[0])
            self.assertEqual((m.STATE / 'soloist.log').stat().st_mode & 0o777, 0o600)

    def test_cli_help_and_paths_work_without_players_or_credentials(self):
        result = subprocess.run([str(SOURCE), '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('setup', result.stdout)
        result = subprocess.run([str(SOURCE), 'paths'], capture_output=True, text=True,
                                env={**os.environ, 'XDG_CONFIG_HOME': self.temp.name})
        self.assertEqual(result.returncode, 0)
        self.assertIn(self.temp.name, result.stdout)

    def test_checksum_failure_does_not_install_spotatui(self):
        def find(name):
            if name == 'soloist':
                return '/soloist'
            raise RuntimeError('missing')
        release = {'assets': [{'name': name, 'browser_download_url': 'https://example.com/' + name}
                             for name in ('spotatui-linux-x86_64.tar.gz', 'checksums.txt')]}
        with patch.object(m.platform, 'system', return_value='Linux'), \
             patch.object(m.platform, 'machine', return_value='x86_64'), \
             patch.object(m, 'binary', side_effect=find), patch.object(m.subprocess, 'run'), \
             patch.object(m, 'fetch', side_effect=[json.dumps(release).encode(), b'bad archive',
                                                  b'bad-hash  spotatui-linux-x86_64.tar.gz\n']):
            with self.assertRaisesRegex(RuntimeError, 'checksum'):
                m.install_players()
        self.assertFalse((m.DATA / 'bin/spotatui').exists())


if __name__ == '__main__':
    unittest.main()
