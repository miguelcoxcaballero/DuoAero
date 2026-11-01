"""Check rejection boundaries and scalar equivalence in the symbol extension.

This executes the Java code packaged in the APK. It does not establish that
native touch controls or the original fragment callback work on a device.
"""
import subprocess
from runtime_config import WORK, JAR, java

source = WORK / 'SymbolicGradeCheck.java'
source.write_text('''
import java.util.*;
import com.duoaero.nativebase.NativeCourseBridge;
public class SymbolicGradeCheck {
 static int checked=0;
 static void check(boolean expected,String[] wanted,String...actual){
  boolean got=NativeCourseBridge.matchesFormulaTerms(Arrays.asList(wanted),Arrays.asList(actual));
  if(got!=expected)throw new AssertionError(Arrays.toString(actual));
  checked++;
 }
 public static void main(String[] args){
  String x="symbol:MULTIPLICATION",d="symbol:DIVISION",a="symbol:ADDITION";
  String[] pressure={"duoaero:ρ",x,"duoaero:R_a",x,"duoaero:T"};
  check(true,pressure,pressure);
  check(true,pressure,"duoaero:T",x,"duoaero:ρ",x,"duoaero:R_a");
  check(false,pressure,"duoaero:T",x,"duoaero:ρ",x,"duoaero:V");
  check(false,pressure,"duoaero:T",d,"duoaero:ρ",x,"duoaero:R_a");
  check(false,pressure,"duoaero:T",x,"duoaero:ρ");
  check(false,pressure,"duoaero:T",x,"duoaero:ρ",x,"duoaero:R_a",x,"duoaero:S");
  check(false,pressure,"duoaero:T",x,null,x,"duoaero:R_a");
  check(false,pressure,"duoaero:T",x,"duoaero:ρ",x,"duoaero:ρ");
  String[] ratio={"duoaero:C_L²",d,"duoaero:π e AR"};
  check(true,ratio,ratio);
  check(false,ratio,"duoaero:π e AR",d,"duoaero:C_L²");
  check(false,ratio,"duoaero:C_L²",x,"duoaero:π e AR");
  String[] term={"duoaero:V²"};
  check(true,term,"duoaero:V²");
  check(false,term,"duoaero:V");
  check(false,term,"duoaero:V²","duoaero:V");
  check(false,term);
  check(false,new String[]{});
  check(true,new String[]{"duoaero:m_OE",a,"duoaero:m_PL"},"duoaero:m_PL",a,"duoaero:m_OE");
  check(false,new String[]{"duoaero:m_OE",a,"duoaero:m_PL"},"duoaero:m_PL",x,"duoaero:m_OE");
  System.out.println("PASS: "+checked+" Java symbolic grading cases; UI remains a separate check");
 }
}
''', encoding='utf-8')
classpath = str(WORK / 'classes') + ':' + str(JAR)
subprocess.run([java('javac'), '-cp', classpath, '-d', WORK / 'classes', source], check=True)
subprocess.run([java('java'), '-cp', classpath, 'SymbolicGradeCheck'], check=True)
