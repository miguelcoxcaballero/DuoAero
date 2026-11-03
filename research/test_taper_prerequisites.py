"""Models only: native fraction layout and teaching order are not accepted."""
import sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'native-base'))
from course_adapter import challenge
from prerequisite_validation import multi_symbol_prerequisite
from taper_prerequisites import prerequisites

qs=prerequisites()
assert len(qs)==28 and len({q['id'] for q in qs})==28
for i in range(0,len(qs),4):
    word,named,single,symbol=qs[i:i+4]
    assert [q['type'] for q in (word,named,single,symbol)]==['gap','formula_named','formula_named','formula_named']
    assert multi_symbol_prerequisite(symbol)
    for q in (word,named,single,symbol):
        challenge(q)
        assert all('\\\\' not in value for value in q.values() if isinstance(value,str))
        assert all('\\\\' not in value for values in q.values() if isinstance(values,list)
                   for value in values if isinstance(value,str))
    assert len(named['answer_blocks'])==len(symbol['answer_blocks'])
print('PASS: seven draft taper prerequisite models; vertical layout, lesson order and Android remain pending.')
