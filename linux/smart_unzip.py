#!/usr/bin/env python
# -*- coding: utf-8 -*-

import zipfile
import chardet
import os
import sys
import argparse


def smart_unicode(s):
    try:
        if isinstance(s, str):
            return unicode(s, 'utf8')
        return unicode(s)
    except UnicodeDecodeError:
        det = chardet.detect(s)
        return s.decode(det['encoding'])


def unzip(z):
    for name in z.namelist():
        _name = smart_unicode(name)
        if name.endswith(os.sep):
            if not os.path.exists(_name):
                os.mkdir(_name)
        else:
            file(_name, 'wb').write(z.read(name))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='unzip tool, smart on encoding')
    parser.add_argument(dest='zipfile', metavar='file')

    args = parser.parse_args(sys.argv[1:])
    z = zipfile.ZipFile(args.zipfile)
    unzip(z)
