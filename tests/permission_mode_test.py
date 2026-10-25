import json
import os
import pathlib
import subprocess
import tempfile
import unittest

READER = (pathlib.Path(__file__).parents[1] / 'hooks/permission-mode.ts').read_text().split('String.raw`', 1)[1].split('`, path', 1)[0]


class PermissionModeTest(unittest.TestCase):
    def read_mode(self, text):
        with tempfile.TemporaryDirectory() as directory:
            source = pathlib.Path(directory) / 'session.jsonl'
            source.write_text(text)
            result = subprocess.run(['python3', '-c', READER, str(source), 'newest'], capture_output=True, text=True, check=True)
        self.assertEqual(result.stderr, '')
        return result.stdout.strip()

    def test_latest_field_wins_and_other_content_never_leaves_reader(self):
        records = [{'permissionMode': 'bypassPermissions', 'secret': 'do not expose'}, {'permissionMode': 'plan'}, {'unrelated': 'bypassPermissions'}, {'permissionMode': 'default'}]
        self.assertEqual(self.read_mode('\n'.join(map(json.dumps, records))), 'manual')

    def test_all_modes(self):
        for value, mode in [('bypassPermissions', 'bypass'), ('auto', 'auto'), ('acceptEdits', 'auto'), ('plan', 'plan'), ('default', 'manual')]:
            self.assertEqual(self.read_mode(json.dumps({'permissionMode': value})), mode)

    def test_unknown_latest_does_not_reuse_old_bypass(self):
        self.assertEqual(self.read_mode('{"permissionMode":"bypassPermissions"}\n{"permissionMode":"unsupported"}'), 'no report yet')

    def test_missing_unreadable_or_partial_records(self):
        self.assertEqual(self.read_mode('{"private":"nothing to report"}'), 'no report yet')
        self.assertEqual(self.read_mode('{"permissionMode":"plan"}\n{"unfinished":'), 'plan')
        result = subprocess.run(['python3', '-c', READER, '/missing/session.jsonl', 'newest'], capture_output=True, text=True, check=True)
        self.assertEqual(result.stdout.strip(), 'no report yet')
        self.assertEqual(result.stderr, '')

    def test_multiple_blocks_and_large_records(self):
        text = json.dumps({'permissionMode': 'auto'}) + '\n' + json.dumps({'private': 'x' * 140000}) + '\n' + json.dumps({'permissionMode': 'plan'})
        self.assertEqual(self.read_mode(text), 'plan')
        self.assertEqual(self.read_mode(text.rsplit('\n', 1)[0]), 'auto')

    def test_restart_uses_newest_session_in_the_same_cwd_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            old = pathlib.Path(directory) / 'old-session.jsonl'
            newest = pathlib.Path(directory) / 'new-session.jsonl'
            old.write_text('{"permissionMode":"bypassPermissions"}')
            newest.write_text('{"permissionMode":"plan"}')
            os.utime(old, (100, 100))
            os.utime(newest, (200, 200))
            result = subprocess.run(['python3', '-c', READER, str(old), 'newest'], capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), 'plan')
            exact = subprocess.run(['python3', '-c', READER, str(old), 'exact'], capture_output=True, text=True, check=True)
            self.assertEqual(exact.stdout.strip(), 'bypass')
            newest.write_text('{"unrelated":"no mode"}')
            result = subprocess.run(['python3', '-c', READER, str(old), 'newest'], capture_output=True, text=True, check=True)
            self.assertEqual(result.stdout.strip(), 'no report yet')


if __name__ == '__main__':
    unittest.main()
