from os import mkdir
from os.path import isdir
if isdir('cache') == True:
    print('yes')
else:
    mkdir('cache')
    print('no')