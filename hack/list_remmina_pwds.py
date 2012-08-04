#!/usr/bin/python
#-*- coding:utf8 -*-

import os
from Crypto.Cipher import DES3

HOME_DIR = os.path.join(os.path.expanduser('~'))
remmina_file = lambda x: os.path.join(HOME_DIR, '.remmina', x)


def get_configure(path):
    cfg = {}
    for line in file(path).read().split('\n'):
        if line and '=' in line:
            k, v = line.split('=', 1)
            cfg[k] = v
    return cfg


def get_cipher(pre_cfg):
    secret = pre_cfg['secret'].decode('base64')
    return DES3.new(secret[:24], DES3.MODE_CBC, secret[24:])


if __name__ == '__main__':
    pre_cfg = get_configure(remmina_file('remmina.pref'))
    for fname in os.listdir(remmina_file('')):
        if fname.endswith('.remmina'):
            cipher = get_cipher(pre_cfg)
            cfg = get_configure(remmina_file(fname))
            print fname, cfg['name'], cfg['username'],
            print cipher.decrypt(cfg['password'].decode('base64'))
