import os
import shutil
import hashlib
import git
from git import RemoteProgress
from tqdm import tqdm
import requests
from urllib.request import urlopen
import json
from os.path import expanduser
import glob

class CloneProgress(RemoteProgress):

    def __init__(self):
        super().__init__()
        self.pbar = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()


class IndexUpdateTask:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def log(self, message):
        self.parent.log('index_update: ' + message)

    def exec(self):
        self.parent.log('starting task index_update')
        INDEX_URI = os.path.expanduser('~') + '/.rpkg/index/'

        if os.path.exists(INDEX_URI):
            # attempt to update
            shutil.rmtree(INDEX_URI)
        git.Repo.clone_from('https://github.com/c0repwn3r/rpkg-index',
                            INDEX_URI, branch='master', progress=CloneProgress())
        self.log('done')


class SourcePackageTask:
    def __init__(self, name, parent, package, version):
        self.name = name
        self.parent = parent
        self.package = package
        self.version = version

    def log(self, message):
        self.parent.log('source_pkg: ' + message)

    def exec(self):
        self.parent.log('starting task source_pkg')
        # worlds simplest task lmao
        self.url = 'https://rpkg.s3.amazonaws.com/' + \
            self.package + '-' + self.version + '.rbp'
        self.log('sourced package to ' + self.url)


class DownloadPackageTask:
    def __init__(self, name, parent, url, dwl_uri, shasum):
        self.name = name
        self.parent = parent
        self.url = url
        self.dwl_uri = dwl_uri
        self.shasum = shasum

    def log(self, message):
        self.parent.log('download_pkg: ' + message)

    def format_bytes(self, size):
        # 2**10 = 1024
        power = 2**10
        n = 0
        power_labels = {0: '', 1: 'kilo', 2: 'mega', 3: 'giga', 4: 'tera'}
        while size > power:
            size /= power
            n += 1
        return str(round(size)) + ' ' + power_labels[n]+'bytes'

    def download_from_url(self, url, dst):
        file_size = int(urlopen(url).info().get('Content-Length', -1))
        print('After this action, an additional ' + self.format_bytes(file_size) +
              ' of disk space will be used. Do you want to continue? [Y/n] ')
        if input().lower() == 'n':
            print('Cancelling')
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

    def exec(self):
        self.download_from_url(self.url, self.dwl_uri)

        self.log('downloaded, verifying')
        shasum = self.shasum
        with open(self.dwl_uri, 'rb') as f:
            rshasum = hashlib.sha256(f.read()).hexdigest()
            if rshasum != shasum:
                self.log('fail: package checksum (' + rshasum +
                         ') does not match expected shasum ' + shasum)
                exit(-1)


class UnpackPackageTask:
    def __init__(self, name, parent, rbp, dest):
        self.name = name
        self.parent = parent
        self.rbp = rbp
        self.dest = dest

    def log(self, message):
        self.parent.log('unpack_pkg: ' + message)

    def exec(self):
        tdir = self.dest
        pkgfile = self.rbp
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

        self.log('valid, unpacking pkg_code')

        os.system('tar xzvf ' + tdir + '/pkg_code.prl -C ' + tdir)
        os.system('tar xzvf ' + tdir + '/packed_rpl.rif -C ' + tdir)
        os.system('tar xzvf ' + tdir + '/packed_js.rij -C ' + tdir)

        self.log('unpacking packed rpl code')
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
            os.system('gzip -fd ' + newname)
        self.log('unpacking packed js code')
        for filename in os.listdir('.'):
            infilename = os.path.join('.', filename)
            if not os.path.isfile(infilename):
                continue
            if not infilename.endswith('.jsc'):
                continue
            newname = infilename[:-4] + '.js.gz'
            os.rename(infilename, newname)
            os.system('gzip -fd ' + newname)

        self.log('removing unneeded files')
        os.unlink('./pkg_code.prl')
        os.unlink('./packed_rpl.rif')
        os.unlink('./packed_js.rij')
        os.unlink('./.SHASUM')
        for filename in glob.glob('./*.rplc'):
            shutil.rmtree(filename)
        for filename in glob.glob('./*.jsc'):
            shutil.rmtree(filename)
        os.chdir(olddir)
        os.unlink(self.rbp)

class InstallPackageTask:
    def __init__(self, name, parent, package, version):
        self.name = name
        self.parent = parent
        self.package = package
        self.version = version

    def log(self, message):
        self.parent.log('install_pkg: ' + message)

    def exec(self):
        self.parent.log('starting task install_pkg')
        IndexUpdateTask("index_update", self).exec()
        # first, source the package
        self.log('sourcing package')
        fol1 = self.package[:2].lower()
        fol2 = self.package[2:4].lower()
        location = os.path.expanduser(
            '~') + '/.rpkg/index/' + fol1 + '/' + fol2 + '/' + self.package.lower() + '.json'
        INSTALL_DIR = os.path.expanduser(
            '~') + '/.rpkg/packages/' + self.package.lower() + '/'
        self.log('verifying that package exists')
        if not os.path.exists(location):
            self.log('fail: package does not exist')
            exit(-1)
        jsond = {}
        with open(location, 'r') as f:
            jsond = json.loads(f.read())
        if jsond['schema_version'] != 2:
            self.log('fail: schema_version is not 2, please update the package')
            exit(-1)
        if (self.version == 'latest'):
            for version in jsond['package_versions']:
                if version['version'] == jsond['package_version']:
                    self.version = version
            self.log('using version ' + self.version['version'])
        else:
            for version in jsond['package_versions']:
                if version['version'] == self.version:
                    self.version = version
            self.log('using version ' + self.version['version'])
        source = SourcePackageTask(
            "source_pkg", self, self.package, self.version['version'])
        source.exec()
        self.log('downloading package')
        dlocation = expanduser('~') + '/.rpkg/packages' + self.package
        dwl = DownloadPackageTask(
            'download_pkg', self, source.url, dlocation, self.version['shasum'])
        dwl.exec()
        self.log('unpacking package')
        up = UnpackPackageTask('unpack_pkg', self, dlocation, INSTALL_DIR)
        up.exec()
        self.log('done')


class RemovePackageTask:
    def __init__(self, name, parent, package):
        self.name = name
        self.parent = parent
        self.package = package

    def log(self, message):
        self.parent.log('remove_pkg: ' + message)


class UpgradeAllPackagesTask:
    def __init__(self, name, parent):
        self.name = name
        self.parent = parent

    def log(self, message):
        self.parent.log('upgrade_pkgs: ' + message)


class UpdatePackageTask:
    def __init__(self, name, parent, package, version):
        self.name = name
        self.parent = parent
        self.package = package
        self.version = version

    def log(self, message):
        self.parent.log('update_pkg: ' + message)


class RootTask:
    def __init__(self, version):
        self.version = version

    def log(self, message):
        print('rpkg: ' + message)

    def exec(self, task):
        task.exec()
        self.log('all tasks finished')
        self.log('done')
        exit()
