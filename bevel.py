#!/usr/bin/env python

"""
Bencoded Entity Vewing, Editing, and Listing.
"""

__all__ = ['BEnt', 'tokenize']

from bencode import bencode, bdecode
from fnmatch import fnmatch
from string import printable

PRINTABLES = set(printable)
UNPRINTABLES = '\r\n\x0b\x0c'

def tokenize(s, separators):
    result = []
    current = ''
    escaped = False
    for i in xrange(len(s)):
        if escaped:
            escaped = False
            current += s[i]
        elif s[i] == '\\':
            escaped = True
        elif s[i] in separators:
            result.append(current)
            current = ''
        else:
            current += s[i]
    result.append(current)
    return result

def _isPrintable(s):
    for c in s:
        if c not in PRINTABLES:
            return False
    return True

def _makePrintable(s, separators):
    assert('\\' not in separators)
    s=s.replace('\\', '\\\\')
    for c in separators:
        s = s.replace(c, '\\'+c)
    for c in UNPRINTABLES:
        s = s.replace(c, c.__repr__()[1:-1])
    return s

def _btLookupR(bt_ent, result, ks = '.', separator = '', path = [], max_length = 16):
    if isinstance(bt_ent, dict):
        keys = bt_ent.keys()
        keys.sort()
        for k in keys:
            _btLookupR(bt_ent[k], result, ks,separator, path + [_makePrintable(k, ks+separator) if isinstance(k, str) else k], max_length=max_length)
        return
    elif isinstance(bt_ent, list):
        for k in range(len(bt_ent)):
            _btLookupR(bt_ent[k], result, ks, separator, path + [_makePrintable(k, ks+separator) if isinstance(k, str) else k], max_length=max_length)
        return
    else:
        if isinstance(bt_ent, str):
            if _isPrintable(bt_ent):
                bt_ent = _makePrintable(bt_ent, ks+separator)
            else:
                result.append((ks.join([str(p) for p in path]), '0x'+str(bt_ent[0:max_length if max_length>=0 else len(bt_ent)]).encode('hex')+'... ('+str(len(bt_ent))+')'))
                return
        result.append((ks.join([str(p) for p in path]), bt_ent))
        return

class BEnt(object):
    def __init__(self, fname, key_separator='.', separator=''):
        self._fname = fname
        self._ent = None
        self._ks = key_separator
        self._separator = separator
        self.load()
    
    def __getitem__(self, key):
        return self._ent.__getitem__(key)

    def __setitem__(self, key, value):
        self._ent.__setitem__(key, value)
    
    def load(self):
        with open(self._fname, 'rb') as f:
            self._ent=bdecode(f.read())
    
    def dumps(self, keep_fileguard=False):
        if not keep_fileguard and isinstance(self._ent, dict) and '.fileguard' in self._ent:
            del self._ent['.fileguard']
        return bencode(self._ent)

    def save(self, filename=None, keep_fileguard=False):
        if not keep_fileguard and isinstance(self._ent, dict) and '.fileguard' in self._ent:
            del self._ent['.fileguard']
        with open(filename or self._fname, 'wb') as f:
            f.write(bencode(self._ent))
    
    def __repr__(self):
        return '<BEnt('+self.name+')>'

    def list(self, max_length = 16):
        return self.lookup(max_length=max_length)

    def lookup(self, keys = ['*'], max_length=16):
        result = []
        _btLookupR(self._ent, result, self._ks, self._separator, max_length=max_length)
        return [item for item in result if any([fnmatch(item[0], key) for key in keys])]

    def delete(self, keys):
        for key in keys:
            here = self._ent
            key = tokenize(key, self._ks)
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
            here = self._ent
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
        return _makePrintable(self._fname, self._ks+self._separator)

    name = property(getName)
