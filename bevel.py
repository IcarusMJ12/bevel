#!/usr/bin/env python

"""
Bencoded Entity Vewing, Editing, and Listing.
"""

__all__ = ['BDict']

from bencode import bencode, bdecode
from fnmatch import fnmatch

def _btLookupR(bt_dict, result, ks = '.', path = []):
    if isinstance(bt_dict, dict):
        keys = bt_dict.keys()
        keys.sort()
        for k in keys:
            _btLookupR(bt_dict[k], result, ks, path + [k])
        return
    elif isinstance(bt_dict, list):
        for k in range(len(bt_dict)):
            _btLookupR(bt_dict[k], result, ks, path + [k])
        return
    else:
        if isinstance(bt_dict, str) and len(bt_dict)>32:
            try:
                bt_dict.decode('utf-8')
            except UnicodeDecodeError:
                result.append((ks.join([str(p) for p in path]), '0x'+str(bt_dict[0:16]).encode('hex')+'... ('+str(len(bt_dict))+')'))
                return
            result.append((ks.join([str(p) for p in path]), bt_dict))
            return
        result.append((ks.join([str(p) for p in path]), bt_dict))
        return

class BDict(object):
    def __init__(self, fname, key_separator='.'):
        self._fname = fname
        self._dict = None
        self._ks = key_separator
        self.load()
    
    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def __setitem__(self, key, value):
        self._dict.__setitem__(key, value)
    
    def load(self):
        with open(self._fname, 'rb') as f:
            self._dict=bdecode(f.read())
    
    def dumps(self, keep_fileguard=False):
        if not keep_fileguard and '.fileguard' in self._dict:
            del self._dict['.fileguard']
        return bencode(self._dict)

    def save(self, filename=None, keep_fileguard=False):
        if not keep_fileguard and '.fileguard' in self._dict:
            del self._dict['.fileguard']
        with open(filename or self._fname, 'wb') as f:
            f.write(bencode(self._dict))
    
    def __repr__(self):
        return '<BDict('+self.name+')>'

    def list(self):
        return self.lookup()

    def lookup(self, keys = ['*']):
        result = []
        _btLookupR(self._dict, result, self._ks)
        return [item for item in result if any([fnmatch(item[0], key) for key in keys])]

    def delete(self, keys):
        for key in keys:
            here = self._dict
            key = key.split(self._ks)
            for subkey in key[0:-1]:
                try:
                    here = here[subkey]
                except TypeError:
                    here = here[int(subkey)]
            try:
                del here[key[-1]]
            except TypeError:
                del here[int(key[-1])]

    def set(self, pairs):
        for key, value in pairs:
            here = self._dict
            key = key.split(self._ks)
            for subkey in key[0:-1]:
                try:
                    here = here[subkey]
                except TypeError:
                    here = here[int(subkey)]
            try:
                here[key[-1]] = value
            except TypeError:
                here[int(key[-1])] = value
    
    def getName(self):
        return self._fname

    name = property(getName)
