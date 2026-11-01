"""Assert device-service observations, without claiming physical output quality."""
import json
import os
from pathlib import Path
import re

root=Path(os.environ.get('DUOAERO_EVIDENCE','/tmp/duoaero-evidence'))
audio=(root/'audio-observation.txt').read_text()
haptics=(root/'vibration-observation.txt').read_text()
players=re.findall(r'new player piid:(\d+) uid/pid:\d+/\d+ package:com\.duoaero\.nativebase type:android\.media\.SoundPool',audio)
starts=sum(len(re.findall(r'player piid:'+re.escape(player)+r' event:started\b',audio)) for player in set(players))
vibrations=[line for line in haptics.splitlines() if 'com.duoaero.nativebase (uid=' in line and 'finished' in line and 'performHapticFeedback' in line]
assert starts>=15, f'Only {starts} original app SoundPool starts observed'
assert len(vibrations)>=15, f'Only {len(vibrations)} original app haptic completions observed'
report={'original_app_soundpool_starts':starts,'original_app_haptic_completions':len(vibrations),
        'scope':'Android emulator audio/vibration service events during native lesson; audible quality and physical sensation on a phone remain unverified.'}
(root/'device-effects-result.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS:',json.dumps(report))
