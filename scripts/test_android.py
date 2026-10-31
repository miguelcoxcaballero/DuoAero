from build import *
for p in (ROOT/'tests/src').rglob('*.java'):p.write_text(p.read_text(encoding='utf-8-sig'),encoding='utf-8')
for d in ['testclasses','testdex']: (build/d).mkdir(exist_ok=True)
run([bt/('aapt2'+suffix),'link','-o',build/'tests.apk','--manifest','tests/AndroidManifest.xml','-I',jar])
run([java/('javac'+suffix),'--release','8','-encoding','UTF-8','-classpath',str(jar)+os.pathsep+str(build/'classes'),'-d',build/'testclasses',*list((ROOT/'tests/src').rglob('*.java'))])
run([java/('java'+suffix),'-cp',bt/'lib/d8.jar','com.android.tools.r8.D8','--lib',jar,'--min-api','26','--output',build/'testdex',*list((build/'testclasses').rglob('*.class'))])
with zipfile.ZipFile(build/'tests.apk','a') as z:
 for p in (build/'testdex').glob('*.dex'):z.write(p,p.name)
key=build/'debug.p12'
if not key.exists():run([java/('keytool'+suffix),'-genkeypair','-keystore',key,'-storepass','android','-keypass','android','-alias','debug','-dname','CN=DuoAero Test','-keyalg','RSA','-validity','100'])
def sign(src,out):run([java/('java'+suffix),'-jar',bt/'lib/apksigner.jar','sign','--ks',key,'--ks-pass','pass:android','--out',out,src])
sign(dist/'DuoAero-1.0.0-unsigned.apk',build/'debug.apk');sign(build/'tests.apk',build/'tests-signed.apk')
adb=sdk/'platform-tools'/('adb'+suffix)
run([adb,'wait-for-device'])
import time
for attempt in range(120):
 if subprocess.check_output([str(adb),'shell','getprop','sys.boot_completed'],text=True).strip()=='1':break
 time.sleep(2)
else: raise RuntimeError('Emulator did not finish booting')
run([adb,'install','-r',build/'debug.apk']);run([adb,'install','-r',build/'tests-signed.apk'])
p=subprocess.run([str(adb),'shell','am','instrument','-w','com.duoaero.tests/com.duoaero.EngineTest'],capture_output=True,text=True)
print(p.stdout);(build/'test-results.txt').write_text(p.stdout)
assert 'PASS:' in p.stdout and 'FAIL:' not in p.stdout,p.stdout+p.stderr
