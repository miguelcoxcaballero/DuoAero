"""The slot observer is inert outside explicitly enabled diagnostics."""
import subprocess,tempfile
from pathlib import Path
from runtime_config import ROOT,java
with tempfile.TemporaryDirectory() as tmp:
 p=Path(tmp)
 (p/'pp3.java').write_text('public class pp3 { public String getId(){ return "synthetic-a"; } }')
 (p/'qp3.java').write_text('public class qp3 { public String getId(){ return "synthetic-b"; } }')
 (p/'SlotGuard.java').write_text('''import java.util.*; import com.duoaero.nativebase.NativeSlotProbe;
public class SlotGuard { public static void main(String[] a) {
 if(NativeSlotProbe.isEnabled())throw new AssertionError("observer defaults on");
 NativeSlotProbe.capture(Arrays.asList(new pp3()));
 if(NativeSlotProbe.snapshot()!=null)throw new AssertionError("observer active before opt-in");
 NativeSlotProbe.enable();if(!NativeSlotProbe.isEnabled())throw new AssertionError("observer did not enable");NativeSlotProbe.capture(Arrays.asList(new pp3()));
 String first=NativeSlotProbe.snapshot();if(first==null||!first.startsWith("pp3:"))throw new AssertionError("missing capture");
 NativeSlotProbe.capture(Arrays.asList(new qp3()));
 if(first.equals(NativeSlotProbe.snapshot()))throw new AssertionError("changed state not captured");
} }''')
 subprocess.run([str(java('javac')),'-d',str(p),str(ROOT/'native-base/src/com/duoaero/nativebase/NativeSlotProbe.java'),str(p/'pp3.java'),str(p/'qp3.java'),str(p/'SlotGuard.java')],check=True)
 subprocess.run([str(java('java')),'-cp',str(p),'SlotGuard'],check=True)
print('PASS: slot observer is inactive until diagnostic opt-in and then observes a changed synthetic slot.')
