import os
import json
import shutil
import hashlib
import glob
import pathlib

print('rpkg: starting task unpack_pkg')

pkgfile = 'MathEx.rbp'
tdir = 'mexet'

print('rpkg: unpack_pkg: unpack (main rbp)')

if os.path.exists(tdir) and os.path.isdir(tdir):
    shutil.rmtree(tdir)
os.mkdir(tdir)

os.system('tar xzvf ' + pkgfile + ' -C ' + tdir)

print('rpkg: verifying .SHASUM')

rshasum = ''
with open(tdir + '/pkg_code.prl', 'rb') as b:
    rshasum = hashlib.sha256(b.read()).hexdigest()

with open(tdir + '/.SHASUM', 'r') as f:
    if f.read() != rshasum:
        print('rpkg: verifying failed, invalid package')
        exit(-1)

print('rpkg: unpack_pkg: valid, unpacking pkg_code')

os.system('tar xzvf ' + tdir + '/pkg_code.prl -C ' + tdir)
os.system('tar xzvf ' + tdir + '/packed_rpl.rif -C ' + tdir)
os.system('tar xzvf ' + tdir + '/packed_js.rij -C ' + tdir)

print('rpkg: unpack_pkg: unpacking packed rpl code')
os.chdir(tdir)
for filename in os.listdir('.'):
    infilename = os.path.join('.', filename)
    if not os.path.isfile(infilename):
        continue
    if not infilename.endswith('.rplc'):
        continue
    newname = infilename[:-5] + '.rpl.gz'
    os.rename(infilename, newname)
    os.system('gzip -d ' + newname)
print('rpkg: unpack_pkg: unpacking packed js code')
for filename in os.listdir('.'):
    infilename = os.path.join('.', filename)
    if not os.path.isfile(infilename):
        continue
    if not infilename.endswith('.jsc'):
        continue
    newname = infilename[:-4] + '.js.gz'
    os.rename(infilename, newname)
    os.system('gzip -d ' + newname)

print('rpkg: unpack_pkg: removing unneeded files')
os.unlink('./pkg_code.prl')
os.unlink('./packed_rpl.rif')
os.unlink('./packed_js.rij')
os.unlink('./.SHASUM')
for filename in glob.glob('./*.rplc'):
    shutil.rmtree(filename)
for filename in glob.glob('./*.jsc'):
    shutil.rmtree(filename)
os.chdir('../')
print('rpkg: done')