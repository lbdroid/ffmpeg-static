#!/usr/bin/env python

import os

deleteList = ['compile', 'output', 'sourcetar', 'target', 'output.tar.xz']
#deleteList.append('sourcegit')
for item in deleteList:
    os.system('rm -rf ./%s' % item)

