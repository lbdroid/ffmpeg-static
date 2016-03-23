#!/usr/bin/env python

import os

deleteList = ['compile', 'output', 'sourcegit', 'sourcetar', 'target']
for item in deleteList:
    os.system('rm -rf ./%s' % item)

