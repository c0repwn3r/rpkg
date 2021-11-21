import os
import task
import git
import sys

RPKG_VERSION = '1.1.0-beta'
RPKG_BUILD =  git.Repo(search_parent_directories=True).head.object.hexsha

def print_help():
    print('Usage: rpkg <hsuirSU> [package[@version]]')
    print()
    print(' -- General --')
    print('    h/help     | Show this help screen.')
    print()
    print(' -- Package operations --')
    print('    s/source   | Source a package (get it\'s download URI).')
    print('    i/install  | Install a package, either latest or the specified version.')
    print('    r/remove   | Uninstall an installed package. Version information is ignored.')
    print('    u/update   | Update an installed package to the latest version.')
    print('    U/upgrade  | Updates all installed packages to the latest version.')
    print()
    print(' -- Repository operations --')
    print('    S/sync     | Updates the local rpkg package index.')
    print()
    print('rpkg - version 1.1.0-beta @ build ' + RPKG_BUILD)

rpkg = task.RootTask("1.1.0-beta")

if len(sys.argv) not in [2, 3]:
    print_help()
    exit()
elif sys.argv[1].lower()[0] == 'h':
    print_help()
    exit()

def c(short,long):
    l = sys.argv[1]
    if l.lower() == long or l == short:
        return True
    else:
        return False

def parse_pkg():
    pkgspec = sys.argv[2]
    pspl = []
    if '@' in pkgspec:
        pspl = pkgspec.split('@')
        return (pspl[0], pspl[1])
    else:
        return (pkgspec, 'latest')

if len(sys.argv) == 2:
    if c('U','upgrade'):
        rpkg.exec(task.UpgradeAllPackagesTask("upgrade_pkgs", rpkg))
        exit()
    elif c('S','sync'):
        rpkg.exec(task.IndexUpdateTask("sync_repo", rpkg))
        exit()
    else:
        print_help()
        exit()
elif len(sys.argv) == 3:
    if c('s','source'):
        (package, version) = parse_pkg()
        rpkg.exec(task.SourcePackageTask("source_pkg", rpkg, package, version))
    elif c('i','install'):
        (package, version) = parse_pkg()
        rpkg.exec(task.InstallPackageTask("install_pkg", rpkg, package, version))
    elif c('r','remove'):
        (package, version) = parse_pkg()
    elif c('u','update'):
        (package, version) = parse_pkg()
    else:
        print_help()
        exit()