import os
import sys
import glob
import shutil

pyts = glob.glob('*.pyt')

if len(pyts) < 1:
    print('No python toolboxes found. Exiting.')
    sys.exit()
elif len(pyts) > 1:
    print('Multiple python toolboxes found. Exiting.')
    sys.exit()
else:
    pyt = pyts[0]
    src_py = pyt.replace('pyt','py')
    if not os.path.isfile(src_py):
        print('Source python file not found. Exiting.')
    else:
        # delete existing pyt
        os.remove(pyt)
        # copy source python file and replace pyt
        shutil.copy(src_py,pyt)
        print('Python toolbox updated.')
        sys.exit()
