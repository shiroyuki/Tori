''' App bootstrap '''

from os.path import abspath, dirname, join
from sys     import path

required_modules = ['Kotoba', 'Imagination', 'Tori']
app_path         = dirname(abspath(__file__))
base_mod_path    = abspath(join(app_path, '..', '..'))

for required_module in required_modules:
    mod_path = join(base_mod_path, required_module)
    path.append(mod_path)
