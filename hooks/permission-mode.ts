// The subprocess returns only a normalized permissionMode; session text stays outside the pane.
export const permissionModeCommand = (path: string, discover = true) => ['python3', '-c', String.raw`
import json, pathlib, sys
modes = {'bypassPermissions': 'bypass', 'auto': 'auto', 'acceptEdits': 'auto', 'default': 'manual', 'plan': 'plan'}
try:
    hint = pathlib.Path(sys.argv[1])
    sessions = list(hint.parent.glob('*.jsonl')) if sys.argv[2] == 'newest' else []
    newest = max(sessions, key=lambda path: (path.stat().st_mtime_ns, path == hint), default=hint)
    with newest.open('rb') as source:
        source.seek(0, 2)
        position, pending = source.tell(), b''
        while position:
            size = min(position, 65536)
            position -= size
            source.seek(position)
            lines = (source.read(size) + pending).split(b'\n')
            pending = lines.pop(0)
            if not position:
                lines.insert(0, pending)
            for line in reversed(lines):
                if b'"permissionMode"' not in line:
                    continue
                try:
                    record = json.loads(line)
                except (ValueError, UnicodeError):
                    continue
                if isinstance(record, dict) and 'permissionMode' in record:
                    mode = record['permissionMode']
                    print(modes.get(mode, 'no report yet') if isinstance(mode, str) else 'no report yet')
                    sys.exit(0)
except OSError:
    pass
print('no report yet')
`, path, discover ? 'newest' : 'exact']
