import os
import shutil
import hashlib
import json
import requests
from tqdm import tqdm
import glob
import pathlib
from urllib.request import urlopen

print('rpkg: task install_pkg started')

package = 'MathEx@latest'
ps = []
pkg = ''
ver = ''

if '@' in package:
    ps = package.split('@')
    if len(ps) != 2:
        print('rpkg: error: invalid package specification')
        exit(-1)
    pkg = ps[0]
    ver = ps[1]
else:
    pkg = package
    ver = 'latest'

import update_index # update the repo index

INDEX_URI = os.path.expanduser('~') + '/.rpkg/index/'

# get pkg repo location
fol1 = pkg[:2].lower()
fol2 = pkg[2:4].lower()
location = INDEX_URI + fol1 + '/' + fol2 + '/' + pkg.lower() + '.json'

INSTALL_DIR = os.path.expanduser('~') + '/.rpkg/packages/' + pkg.lower() + '/'

print('rpkg: install_pkg: checking index to verify package exists')
if not os.path.exists(location):
    print('fail: package does not exist')
    exit(-1)
print('rpkg: install_pkg: loading', location)
print('rpkg: install_pkg: checking to make sure version exists')
jsond = {}
with open(location, 'r') as f:
    jsond = json.loads(f.read())
if jsond['schema_version'] != 2:
    print('fail: schema_version is not 2, please update the package')
    exit(-1)
if (ver == 'latest'):
    for version in jsond['package_versions']:
        if version['version'] == jsond['package_version']:
            ver = version
    print('rpkg: install_pkg: using version', ver['version'])
else:
    for version in jsond['package_versions']:
        if version['version'] == ver:
            ver = version
    print('rpkg: install_pkg: using version', ver['version'])

print('rpkg: install_pkg: downloading packed image')
SOURCE_URL = 'https://rpkg-index.c0repwn3r.repl.co/source/' + pkg + '/' + ver['version']
DWL_URI = INSTALL_DIR + '/' + pkg + '-' + ver['version'] + '.rbp'
if os.path.exists(INSTALL_DIR):
    shutil.rmtree(INSTALL_DIR)
if not os.path.exists(os.path.expanduser('~') + '/.rpkg/packages/'):
    os.mkdir(os.path.expanduser('~') + '/.rpkg/packages/')
os.mkdir(INSTALL_DIR)
import requests
from tqdm import tqdm

def download_from_url(url, dst):
    file_size = int(urlopen(url).info().get('Content-Length', -1))
    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size:
        return file_size
    header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
    pbar = tqdm(
        total=file_size, initial=first_byte,
        unit='B', unit_scale=True, desc=url.split('/')[-1])
    req = requests.get(url, headers=header, stream=True)
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size

download_from_url(SOURCE_URL, DWL_URI)

print('rpkg: install_pkg: downloaded, unpacking')

print('rpkg: starting task unpack_pkg')

pkgfile = DWL_URI
tdir = INSTALL_DIR

print('rpkg: unpack_pkg: unpack (main rbp)')

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
olddir = os.getcwd()
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
os.chdir(olddir)
os.unlink(DWL_URI)
print('rpkg: done')