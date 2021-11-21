import os
import shutil
import hashlib
import git
from git import RemoteProgress
from tqdm import tqdm

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
        git.Repo.clone_from('https://github.com/c0repwn3r/rpkg-index', INDEX_URI, branch='master', progress=CloneProgress())
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
        IndexUpdateTask("index_update", self).exec()
        self.url = 'https://rpkg-index.c0repwn3r.repl.co/source/' + self.package + '/' + self.version
        self.log('sourced package to ' + self.url)

class DownloadPackageTask:
    def __init__(self, name, parent, url):
        self.name = name
        self.parent = parent
        self.url = url
        
    def log(self, message):
        self.parent.log('download_pkg: ' + message)

class UnpackPackageTask:
    def __init__(self, name, parent, rbp, dest):
        self.name = name
        self.parent = parent
        self.rbp = rbp
        self.dest = dest
        
    def log(self, message):
        self.parent.log('unpack_pkg: ' + message)

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
        # first, source the package
        self.log('sourcing package')
        source = SourcePackageTask("source_pkg", self, self.package, self.version)
        source.exec()


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