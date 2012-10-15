#!/usr/bin/env python

"""
Bencoded Entity Vewing, Editing, and Listing
"""

__all__ = ['BDict']

from bencode import bencode, bdecode
from fnmatch import fnmatch

def _btLookupR(bt_dict, result, path = []):
    if isinstance(bt_dict, dict):
        keys = bt_dict.keys()
        keys.sort()
        for k in keys:
            _btLookupR(bt_dict[k], result, path + [k])
        return
    elif isinstance(bt_dict, list):
        for k in range(len(bt_dict)):
            _btLookupR(bt_dict[k], result, path + [k])
        return
    else:
        if isinstance(bt_dict, str) and len(bt_dict)>32:
            try:
                bt_dict.decode('utf-8')
            except UnicodeDecodeError:
                result.append(('.'.join([str(p) for p in path]), '0x'+str(bt_dict[0:16]).encode('hex')+'... ('+str(len(bt_dict))+')'))
                return
            result.append(('.'.join([str(p) for p in path]), bt_dict))
            return
        result.append(('.'.join([str(p) for p in path]), bt_dict))
        return

class BDict(object):
    def __init__(self, fname, keep_fileguard = False):
        self._fname = fname
        self._keep_fileguard = keep_fileguard
        self._dict = None
        self.load()
    
    def __getitem__(self, key):
        return self._dict.__getitem__(key)

    def __setitem__(self, key, value):
        self._dict.__setitem__(key, value)
    
    def load(self):
        with open(self._fname, 'rb') as f:
            self._dict=bdecode(f.read())
    
    def save(self):
        if not self._keep_fileguard and '.fileguard' in self._dict:
            del self._dict['.fileguard']
        with open(self._fname, 'wb') as f:
            f.write(bencode(self._dict))
    
    def __repr__(self):
        return '<BTDict('+self.name+')>'

    def list(self):
        return self.lookup()

    def lookup(self, keys = ['*']):
        result = []
        _btLookupR(self._dict, result)
        return [item for item in result if any([fnmatch(item[0], key) for key in keys])]

    def set(self, pairs):
        for key, value in pairs:
            here = self._dict
            key = key.split('|')
            for subkey in key[0:-1]:
                print here.keys()
                here = here[subkey]
            here[key[-1]] = value
        self.save()
    
    def getName(self):
        return self._fname

    name = property(getName)
