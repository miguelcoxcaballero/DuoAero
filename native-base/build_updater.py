"""Compile the locked canonical updater, without changing its frozen sources."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from runtime_config import ROOT, WORK, JAR, BT, java, tool


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def fetch_dependency(item, destination):
    """Retry transient repository errors without caching incomplete artifacts."""
    partial = destination.with_name(destination.name + '.part')
    try:
        for attempt in range(3):
            try:
                urllib.request.urlretrieve(item['url'], partial)
                break
            except urllib.error.HTTPError as error:
                if attempt == 2 or (error.code not in (404, 429) and error.code < 500):
                    raise
            except urllib.error.URLError:
                if attempt == 2:
                    raise
            time.sleep(attempt + 1)
        if hashlib.sha256(partial.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Updater dependency checksum mismatch: '+item['file'])
        os.replace(partial, destination)
    finally:
        partial.unlink(missing_ok=True)


def build():
    run(os.sys.executable, ROOT/'vendor/inhouse-services-updater/verify.py', ROOT)
    target = WORK/'updater'
    dependencies = target/'dependencies'
    classes = target/'classes'
    for directory in (dependencies, classes, target/'shading', target/'dex', target/'flat'):
        directory.mkdir(parents=True, exist_ok=True)
    for item in json.loads((ROOT/'native-base/updater-dependencies.json').read_text()):
        file = dependencies/item['file']
        if not file.exists():
            fetch_dependency(item, file)
        if hashlib.sha256(file.read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Updater dependency checksum mismatch: '+item['file'])
    with zipfile.ZipFile(dependencies/'core.aar') as archive:
        (dependencies/'core.jar').write_bytes(archive.read('classes.jar'))
    sources = ROOT/'vendor/inhouse-services-updater/android'
    classpath = os.pathsep.join(map(str, [JAR, dependencies/'core.jar', dependencies/'kotlin-stdlib.jar', classes]))
    run(java('java'), '-cp', str(dependencies/'*'), 'org.jetbrains.kotlin.cli.jvm.K2JVMCompiler',
        '-no-stdlib', '-no-reflect', '-jvm-target', '1.8', '-classpath', classpath,
        '-d', classes, sources/'PhotosUpdateInstaller.kt', *sources.glob('*.java'))
    run(java('javac'), '--release', '8', '-encoding', 'UTF-8', '-cp', classpath,
        '-d', classes, *sources.glob('*.java'))
    with zipfile.ZipFile(target/'canonical.jar', 'w') as archive:
        for source in classes.rglob('*.class'):
            archive.write(source, source.relative_to(classes).as_posix())
    asm = os.pathsep.join(map(str, [dependencies/'asm.jar', dependencies/'asm-commons.jar', target/'shading']))
    run(java('javac'), '-cp', asm, '-d', target/'shading', ROOT/'scripts/ShadeDependencies.java')
    run(java('java'), '-cp', asm, 'ShadeDependencies', target/'updater-shaded.jar',
        target/'canonical.jar', dependencies/'core.jar', dependencies/'kotlin-stdlib.jar')
    run(java('java'), '-cp', BT/'lib/d8.jar', 'com.android.tools.r8.D8', '--lib', JAR,
        '--min-api', '29', '--output', target/'dex', target/'updater-shaded.jar')
    # Compile the canonical provider path XML independently; append its resource
    # entry to the original table later, keeping every original ID/value.
    paths = ROOT/'original/res/xml/inhouse_update_paths.xml'
    run(tool('aapt2'), 'compile', paths, '-o', target/'flat')
    (target/'AndroidManifest.xml').write_text('<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.duoaero.updaterresources"><application/></manifest>')
    run(tool('aapt2'), 'link', '-o', target/'paths.apk', '--manifest', target/'AndroidManifest.xml',
        '-I', JAR, *list((target/'flat').glob('*.flat')))
    with zipfile.ZipFile(target/'paths.apk') as archive:
        (target/'inhouse_update_paths.xml').write_bytes(archive.read('res/xml/inhouse_update_paths.xml'))
    return target


if __name__ == '__main__':
    print('Canonical updater compiled:', build())
