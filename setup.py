from distutils.core import setup
from glob           import glob
from os.path        import abspath, dirname, join
from re             import sub
from sys            import exit

module_name = 'tori'
found_paths = glob(join(module_name, '*'))

found_paths.append(module_name)

packages = []

for found_path in found_paths:
    if '__'   in found_path: continue
    if '.pyc' in found_path: continue
    if '.py' in found_path: continue
    
    package = found_path
    package = sub('\.py', '', package)
    package = sub('/', '.', package)
    
    packages.append(package)

packages.sort()

setup(
    name         = 'Tori',
    version      = '2.0',
    description  = 'Lightweight Web Framework',
    author       = 'Juti Noppornpitak',
    author_email = 'juti_n@yahoo.co.jp',
    url          = 'http://shiroyuki.com/work/projects-tori',
    packages     = packages
)
