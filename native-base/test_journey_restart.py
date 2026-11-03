"""Check persistence after the unseeded native journey, without changing progress."""
import json
import os
import subprocess
import time
from pathlib import Path

PACKAGE = 'com.duoaero.nativebase'
OUT = Path(os.environ['DUOAERO_EVIDENCE'])
IDS = [f'second-partial-{topic}-lesson-{index}'
       for topic, count in [('3.1', 3), ('3.2', 2), ('3.3', 2)]
       for index in range(count)]

def adb(*args):
    return subprocess.check_output(['adb', *args], timeout=60)

def read_proofs():
    results = []
    for identifier in IDS:
        path = f'files/duoaero-course/local-test/submissions/{identifier}.json'
        result = json.loads(adb('shell', 'run-as', PACKAGE, 'cat', path))
        assert result.get('completedOnce') is True, identifier
        results.append(result)
    return results

before = read_proofs()
adb('shell', 'am', 'force-stop', PACKAGE)
adb('shell', 'am', 'start', '-W', '-n', PACKAGE + '/com.duolingo.splash.LaunchActivity')
time.sleep(15)
after = read_proofs()
assert before == after, 'Completion records changed across app restart'
(OUT / 'journey-restart.png').write_bytes(adb('exec-out', 'screencap', '-p'))
(OUT / 'journey-restart-result.txt').write_text(
    'PASS: seven completion records retained after force-stop and relaunch; '
    'does not establish real account synchronization or visual path state.\n')
print((OUT / 'journey-restart-result.txt').read_text(), end='')
