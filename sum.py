#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import re


class Filter(object):
    def is_bad(self, name, path):
        return False


class RegxFilter(Filter):
    def __init__(self, regx, match_path=True):
        self.regx = re.compile(regx)
        self.match_path = match_path

    def is_bad(self, name, path):
        if self.match_path:
            return self.regx.search(path) and True or False
        return self.regx.search(name) and True or False


class NameFilter(Filter):
    def __init__(self, name):
        self.name = name

    def is_bad(self, name, path):
        return name == self.name


class PathFilter(Filter):
    def __init__(self, path):
        self.name = path

    def is_bad(self, name, path):
        return path == self.path


class Item(object):
    _filters = []

    def __init__(self, path):
        self.path = path
        self.name = os.path.split(path)[-1]
        self.get_info()

    def __hash__(self):
        return hash(self.name)

    def get_info(self):
        pass

    @classmethod
    def is_bad(cls, name, path):
        for f in cls._filters:
            if f.is_bad(name, path):
                return True
        return False

    @classmethod
    def filter_regx(cls, *regxs):
        cls._filters.extend(map(lambda r: RegxFilter(r, os.sep in r), regxs))

    @classmethod
    def filter_name(cls, *ns):
        cls._filters.extend(map(lambda n: NameFilter(n), ns))

    @classmethod
    def filter_path(cls, *ps):
        cls._filters.extend(map(lambda p: PathFilter(p), ps))


class File(Item):
    def __init__(self, path):
        self.valid_lines = 0
        self.blank_lines = 0
        self.size = 0
        super(File, self).__init__(path)

    def get_info(self):
        data = file(self.path).read()
        self.size = len(data) / 1024.0
        lines = map(lambda l: l.strip(), data.split('\n'))
        self.valid_lines = reduce(lambda c, b: c + 1 if b else c, lines, 0)
        self.blank_lines = len(lines) - self.valid_lines

    def str(self, indent):
        fmt = '%%-%ds: %%4.1f KB, %%4d valid lines, %%4d blank lines' % indent
        return fmt % (self.name, self.size, self.valid_lines, self.blank_lines)


class Link(Item):
    def __init__(self, path):
        super(Link, self).__init__(path)
        self.real_path = os.path.realpath(path)

    def str(self, indent):
        fmt = '%%-%ds: link to %%s' % indent
        return fmt % (self.name, self.real_path)


class Dir(Item):
    def __init__(self, path):
        self.fs = set()
        self.dirs = set()
        super(Dir, self).__init__(path)

    def get_info(self):
        ns = os.listdir(self.path or '.')
        for name in ns:
            path = os.path.join(self.path, name)
            if self.is_bad(name, path):
                continue
            if os.path.islink(path):
                self.fs.add(Link(path))
            if os.path.isfile(path):
                self.fs.add(File(path))
            elif os.path.isdir(path):
                self.dirs.add(Dir(path))

    def table_lines(self, prefix='  '):
        lines = []
        count = len(self.fs) + len(self.dirs)
        get_prefix = lambda: (prefix + '└─') if count == 1 else (prefix + '├─')
        if len(self.fs):
            indent = max(map(lambda f: len(f.name), self.fs))
        for f in self.fs:
            lines.append(get_prefix() + f.str(indent))
            count -= 1
        for d in self.dirs:
            lines.append(get_prefix() + '%s:' % d.name)
            if count == 1:
                lines.extend(d.table_lines(prefix + '   '))
            else:
                lines.extend(d.table_lines(prefix + '│  '))
            count -= 1
        return lines

    def sum(self):
        fc = len(self.fs)
        size = sum(map(lambda f: f.size, self.fs))
        vl = sum(map(lambda f: f.valid_lines, self.fs))
        bl = sum(map(lambda f: f.blank_lines, self.fs))
        for d in self.dirs:
            s, c, v, b = d.sum()
            fc += c
            size += s
            vl += v
            bl += b
        return fc, size, vl, bl


if __name__ == '__main__':
    Item.filter_regx(r'\.pyc$')
    Item.filter_name('.git', '.gitignore', 'sum.py')
    d = Dir('')
    print '\n'.join(d.table_lines())
    print '%d files, %.1f KB, %d valid lines, %d blank lines' % d.sum()
