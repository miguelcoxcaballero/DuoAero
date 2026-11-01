"""Validate generated grading against every selection, including empty/multiple."""
import json
from pathlib import Path
import subprocess
from rich_question import choice_blob, content

root = Path(__file__).resolve().parents[1]
bank = json.loads((root / 'app/assets/questions.json').read_text(encoding='utf-8-sig'))
fixtures = []
for question in bank:
    if question['type'] != 'choice' or not question.get('rich_text'):
        continue
    blob = json.loads(choice_blob(question)['challengeBlob'])
    fixtures.append({'id': question['id'], 'code': blob['grading_function'],
                     'answer': question['answer'], 'count': len(question['options'])})
assert len(fixtures) >= 4
isa = next(q for q in bank if q['id'] == 'TA1-0182-F1')
isa_blob = json.loads(choice_blob(isa)['challengeBlob'])
assert r'p_{\mathrm{base}}' in isa_blob['shirt']['value']
assert r'\exp(-X)' in isa_blob['shirt']['value']
assert 'p_base' not in isa_blob['shirt']['value']

from formula_exercises import formula_challenge, prototypes
for question in prototypes() + [q for q in bank if q['type'] == 'formula_blocks']:
    prompt = formula_challenge(question)['promptInputChallenge']['prompt']
    feedback = prompt['gradingFeedbackSpecification']['staticFeedback']['gradingFeedback']
    assert feedback['taggedTextElement']['text'] == 'duoaero-latex:' + r'\textstyle ' + question['formula_latex']
    assert question['explanation'] not in feedback['taggedTextElement']['text']
script = r'''
const fixtures=JSON.parse(require('fs').readFileSync(0,'utf8'));
let checked=0;
for(const f of fixtures){
  const grade=new Function(f.code+'; return grade;')();
  for(let mask=0; mask<(1<<f.count); mask++){
    const variables={};
    for(let i=0;i<f.count;i++) variables['answer_'+i]={selected:!!(mask&(1<<i))};
    const result=grade(variables);
    if(result.isCorrect !== (mask===(1<<f.answer))) throw Error(f.id+': '+mask);
    if(!result.feedback.value || !result.displayAnswer.value) throw Error('Missing feedback');
    checked++;
  }
}
console.log(checked+' grading combinations passed');
'''
subprocess.run(['node', '-e', script], input=json.dumps(fixtures), text=True, check=True)
assert content([{'latex': r'\frac{L}{D}'}], '') == r'\frac{L}{D}'
try:
    content([{'latex': 'x', 'text': 'y'}], '')
except ValueError:
    pass
else:
    raise AssertionError('Ambiguous rich content accepted')
print('LaTeX preserved; ambiguous content rejected. Rendering still requires device QA.')
