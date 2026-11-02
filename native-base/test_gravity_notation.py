"""Check the reported gravity answer and its authored mathematical options."""
import json
from pathlib import Path
from rich_question import choice_blob, content

root=Path(__file__).resolve().parents[1]
bank=json.loads((root/'app/assets/questions.json').read_text())
q=next(q for q in bank if q['id']=='TH-2026-OTHER-1')
assert q['options'][q['answer']]=='g=g0(RE/(RE+h))²'
correct=content(q['rich_text']['options'][q['answer']],q['options'][q['answer']])
assert correct == r'g=g_0\left(\frac{R_E}{R_E+h}\right)^2'
assert len(q['rich_text']['options'])==len(q['options'])==4
blob=json.loads(choice_blob(q)['challengeBlob'])
assert json.dumps({'type':'text','value':r'\textstyle '+correct}) in blob['grading_function']
print('PASS: inverse-square gravity answer and authored LaTeX; Android rendering unverified.')
