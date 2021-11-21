import os
import json
import shutil
import hashlib
import glob

print('rpkg: task pack_pkg initiated')
print('rpkg: load_package: loading package from file')
pkg_name = 'MathEx'

package = {}

with open(pkg_name + '/module.json', 'r') as f:
    package = json.loads(f.read())

print('rpkg: load_package: done')
print('rpkg: creating work directory')
print('rpkg: make_temp_dir: making temporary directory')
if os.path.exists('./work/') and os.path.isdir('./work/'):
    shutil.rmtree('./work/')
os.mkdir('./work/')
os.mkdir('./work/rif/')
os.mkdir('./work/rij/')
print('rpkg: make_temp_dor: done')
print('rpkg: pack_pkg: packing .rpl scripts into packed_rpl.rif')
print('rpkg: pack_pkg: pack_rif: compressing')
for root, dirs, files in os.walk(pkg_name):
    for file in files:
        if file.endswith('.rpl'):
            path = os.path.join(root, file)
            print('rpkg: pack_pkg: pack_rif: pack_rpl: packing', file)
            print('rpkg: pack_pkg: pack_rif: pack_' + file + ': compressing')
            os.system('gzip -c ' + path + ' > ./work/rif/' + file + 'c')
            print('rpkg: pack_pkg: pack_rif: pack_' + file + ': done')
for file in glob.glob(r'./work/rif/*.rplc'):
    shutil.copy(file, '.')
os.system('tar czvf ./work/packed_rpl.rif ./*.rplc')
shutil.rmtree('./work/rif/')
for file in glob.glob(r'./*.rplc'):
    os.unlink(file)
print('rpkg: pack_pkg: pack_rif: done')
print('rpkg: pack_pkg: packing .js addons into packed_js.rij')
print('rpkg: pack_pkg: pack_rij: compressing')
for root, dirs, files in os.walk(pkg_name):
    for file in files:
        if file.endswith('.js'):
            path = os.path.join(root, file)
            print('rpkg: pack_pkg: pack_rij: pack_js: packing', file)
            print('rpkg: pack_pkg: pack_rij: pack_' + file + ': compressing')
            os.system('gzip -c ' + path + ' > ./work/rij/' + file + 'c')
            print('rpkg: pack_pkg: pack_rij: pack_' + file + ': done')
for file in glob.glob(r'./work/rij/*.jsc'):
    shutil.copy(file, '.')
os.system('tar czvf ./work/packed_js.rij ./work/rij/*.jsc')
shutil.rmtree('./work/rij/')
for file in glob.glob(r'./*.jsc'):
    os.unlink(file)
print('rpkg: pack_pkg: pack_rij: done')
print('rpkg: pack_pkg: packing .rxx files into pkg_code.prl')
print('rpkg: pack_pkg: pack_prl: compressing')
if os.path.exists('./work/packed_rpl.rif') and os.path.exists('./work/packed_js.rij'):
    shutil.copy('./work/packed_rpl.rif', '.')
    shutil.copy('./work/packed_js.rij', '.')
    os.system('tar czvf ./work/pkg_code.prl ./packed_rpl.rif ./packed_js.rij')
    os.unlink('./work/packed_rpl.rif')
    os.unlink('./work/packed_js.rij')
    os.unlink('./packed_rpl.rif')
    os.unlink('./packed_js.rij')
elif os.path.exists('./work/packed_rpl.rif'):
    shutil.copy('./work/packed_rpl.rif', '.')
    os.system('tar czvf ./work/pkg_code.prl ./work/packed_rpl.rif')
    os.unlink('./work/packed_rpk.rif')
    os.unlink('./packed_rpl.rif')
elif os.path.exists('./work/packed_js.rij'):
    print('error: invalid package! a package cannot contain only js')
    exit(-1)
print('rpkg: pack_pkg: pack_prl: done')
print('rpkg: pack_pkg: getting checksum and putting it into .SHASUM')
shasum = ''
print('rpkg: pack_pkg: shasum: calculating shasum')
with open('./work/pkg_code.prl', 'rb') as packed_code:
    shasum = hashlib.sha256(packed_code.read()).hexdigest()
print('rpkg: pack_pkg: shasum: writing shasum')
with open('./work/.SHASUM', 'w') as f:
    f.write(shasum)
print('rpkg: pack_pkg: shasum: verifying written shasum')
with open('./work/.SHASUM', 'r') as f:
    shasum = f.read()
with open('./work/pkg_code.prl', 'rb') as packed_code:
    tshasum = hashlib.sha256(packed_code.read()).hexdigest()
    if (tshasum != shasum):
        print('fail: hash verification failed: hash in SHASUM (' + shasum + ') does not match actual shasum ' + tshasum)
        exit(-1)
    else:
        print('rpkg: pack_pkg: shasum: verified shasum successfully')
print('rpkg: pack_pkg: shasum: done')
print('rpkg: pack_pkg: packing into rbp')
print('rpkg: pack_pkg: pack_rbp: compressing')
shutil.copy('./work/pkg_code.prl', '.')
shutil.copy('./work/.SHASUM', '.')
shutil.copy(pkg_name + '/module.json', '.')
os.system('tar czvf ' + pkg_name + '.rbp ./pkg_code.prl ./.SHASUM ./module.json')
print('./work/pkg_code.prl ./work/.SHASUM ' + pkg_name + '/module.json')
os.unlink('./work/.SHASUM')
os.unlink('./work/pkg_code.prl')
os.unlink('./pkg_code.prl')
os.unlink('./.SHASUM')
os.unlink('./module.json')
shutil.rmtree('./work/')
print('rpkg: pack_pkg: pack_rbp: done')
print('rpkg: pack_pkg: done')
print('rpkg: all tasks finished')
print('rpkg: done')