import os

def ginput(msg, default):
    n = input(msg)
    if (n == '' or n == ' '):
        return default
    else:
        return n

print('RPL++ package init utility script - use latest from rpkg/scripts/init_pkg.py!')
name = input('What is the package called? ')
if os.path.exists(name) and os.path.isdir(name):
    print('error: directory already exists')
    exit(-1)
version = ginput('What is the package version? [1.0.0] ', '1.0.0')
description = ginput('What is the package description? [] ', '')
authors = ginput('What is the package author? [rpkg] ', 'rpkg')
pl = ginput('What is the SPDX identifier of the license? [MIT] ', 'MIT')
entry = ginput('What is the entry point of the 

