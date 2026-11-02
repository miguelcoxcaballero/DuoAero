"""Exercise the exact native filename validator against every planned lesson."""
import json
import subprocess
import tempfile
from pathlib import Path
from runtime_config import ROOT, java

plan = json.loads((ROOT / 'app/assets/lesson_plan.json').read_text())
ids = [lesson['id'] for node in plan for lesson in node['lessons']]
assert '2.1-5-point-0-lesson-0' in ids and len(ids) == 100
with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    runner = folder / 'Check.java'
    runner.write_text('''package com.duoaero.nativebase;
public class Check {
 public static void main(String[] args) {
  for(String id: args) if(!NativeSessionId.valid(id)) throw new AssertionError(id);
  for(String id: new String[]{"", ".hidden", "..", "a..b", "../escape", "a/b", "a\\\\b", "a."})
   if(NativeSessionId.valid(id)) throw new AssertionError("Unsafe: "+id);
  if(NativeSessionId.valid(new String(new char[161]).replace('\\0', 'a'))) throw new AssertionError("too long");
 }
}''')
    subprocess.run([str(java('javac')), '-d', str(folder),
                    str(ROOT / 'native-base/src/com/duoaero/nativebase/NativeSessionId.java'),
                    str(runner)], check=True)
    subprocess.run([str(java('java')), '-cp', str(folder), 'com.duoaero.nativebase.Check', *ids], check=True)
print('PASS: all 100 lesson IDs and unsafe filename cases; Android submission still requires device acceptance.')
