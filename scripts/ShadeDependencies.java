import java.io.*;
import java.util.*;
import java.util.zip.*;
import org.objectweb.asm.*;
import org.objectweb.asm.commons.*;
/** Relocate build dependencies, leaving canonical updater source untouched. */
public final class ShadeDependencies {
 public static void main(String[] args)throws Exception {
  Remapper map=new Remapper(){public String map(String name){return name.startsWith("androidx/")||name.startsWith("kotlin/")?"com/inhouse/shadow/"+name:name;}};
  Set<String> seen=new HashSet<>();
  try(ZipOutputStream out=new ZipOutputStream(new FileOutputStream(args[0]))){
   for(int i=1;i<args.length;i++)try(ZipFile in=new ZipFile(args[i])){
    Enumeration<? extends ZipEntry> entries=in.entries();
    while(entries.hasMoreElements()){
     ZipEntry entry=entries.nextElement();String name=entry.getName();
     if(!name.endsWith(".class")||name.startsWith("META-INF/")||name.equals("module-info.class"))continue;
     byte[] bytes;try(InputStream stream=in.getInputStream(entry)){bytes=stream.readAllBytes();}
     ClassReader reader=new ClassReader(bytes);ClassWriter writer=new ClassWriter(0);
     // UI host references belong to the original APK. Only updater dependencies
     // use the relocated AndroidX/Kotlin copies to avoid ABI collisions.
     reader.accept(new ClassRemapper(writer,reader.getClassName().startsWith("com/duoaero/")?new Remapper(){}:map),0);
     name=map.map(reader.getClassName())+".class";
     if(!seen.add(name))throw new IllegalStateException("Duplicate class "+name);
     out.putNextEntry(new ZipEntry(name));out.write(writer.toByteArray());out.closeEntry();
    }
   }
  }
 }
}
