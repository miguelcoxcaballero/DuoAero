"""Verify diagnostic isolation and marker encoding, not native rendering."""
import base64,json,os,sys,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'native-base'))
from course_adapter import challenge
from wide_fraction_fixture import fixture

qs=fixture();assert len(qs)==4
wide=[q for q in qs if q.get('inline_latex')==['___','=','___*___*___/___*___']]
assert len(wide)==2
old=os.environ.pop('DUOAERO_WIDE_FRACTION_DIAGNOSTIC',None)
try:
    try:challenge(wide[0])
    except ValueError as error:assert 'isolated diagnostic' in str(error)
    else:raise AssertionError('Wide layout must be blocked without diagnostic flag')
    os.environ['DUOAERO_WIDE_FRACTION_DIAGNOSTIC']='1'
    for q in wide:
        encoded=challenge(q)['promptInputChallenge']['prompt']['body']['taggedTextElement']['text']
        marker='duoaero-latex:duoaero-gap:'
        assert encoded.startswith(marker)
        parts=json.loads(base64.b64decode(encoded[len(marker):]))
        assert parts.count('duoaero-product-fraction-32')==1
        assert len(q['answer_blocks'])==6
finally:
    if old is None:os.environ.pop('DUOAERO_WIDE_FRACTION_DIAGNOSTIC',None)
    else:os.environ['DUOAERO_WIDE_FRACTION_DIAGNOSTIC']=old
blocked=subprocess.run([sys.executable,str(root/'native-base/build.py')],
    env={**os.environ,'DUOAERO_PACKAGE':'com.duoaero','DUOAERO_WIDE_FRACTION_DIAGNOSTIC':'1'},
    capture_output=True,text=True)
assert blocked.returncode!=0 and 'isolated diagnostic only' in blocked.stderr
print('PASS: isolated 3-over-2 fraction markers decode; no native layout or interaction acceptance.')
