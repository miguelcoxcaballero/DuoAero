from pathlib import Path
import json,shutil
W=Path(__file__).resolve().parent;OUT=W
s=(W/'english.template.html').read_text(encoding='utf-8-sig')
for key,value in {'__REFERENCE_CSS__':(W/'reference_path.css').read_text(encoding='utf-8'),'__BANK__':(W/'bank_en_final.json').read_text(encoding='utf-8').replace('</','<\\/'),'__SOUNDS__':(W/'audio_embedded.json').read_text(encoding='utf-8'),'__NODE__':json.dumps((W/'reference_node.svg').read_text(encoding='utf-8')),'__ENGINE__':(W/'english.app.js').read_text(encoding='utf-8-sig')}.items():s=s.replace(key,value)
s=s.replace(':root{',':root{--color-black:0,0,0;--color-duo-shine:215,255,184;--path-unit-character-color:#58cc02;')
p=OUT/'Aeroracha_Tecnologia_Aeroespacial.html';p.write_text(s,encoding='utf-8');print(p,p.stat().st_size)
shutil.copyfile(W/'bank_en_final.json',OUT/'Aerospace_Midterm1_1200_questions.json')
