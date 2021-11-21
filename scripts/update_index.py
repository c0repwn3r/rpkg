import os
import shutil
import hashlib
import git
from git import RemoteProgress
from tqdm import tqdm

print('rpkg: task update_index started')
print('rpkg: update_index: updating rpkg index')
class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()
    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()

INDEX_URI = os.path.expanduser('~') + '/.rpkg/index/'

if os.path.exists(INDEX_URI):
    # attempt to update
    shutil.rmtree(INDEX_URI)
git.Repo.clone_from('https://github.com/c0repwn3r/rpkg-index', INDEX_URI, branch='master', progress=CloneProgress())
print('rpkg: update_index: done')
print('rpkg: all tasks finished')
print('rpkg: done')