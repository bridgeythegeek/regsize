#!/usr/bin/env python3

__author__ = "Bridgey the Geek"
__date__ = "$13-Feb-2015 08:54:56$"

import argparse
import glob
import hashlib
import operator
import os
from Registry import Registry

class regsize:
    
    def __init__(self, hive_file, max):
    
        self.hive_file = hive_file
        self.max_tops = max
        self.reg = Registry.Registry(self.hive_file)
        self.tops = {}
        self.drop_cmi = self.reg.root().path().split('\\')[0][0:4] == 'CMI-'
    
    def check_key(self, key):
    
        for value in key.values():
            if self.is_tops(value):
                raw_len = value._vkrecord.data_length()
                if len(self.tops) > 0 and raw_len > min(self.tops.values()):
                    self.drop_smallest()
                self.tops[key.path() + '\\' + value.name()] = raw_len
        
        for subkey in key.subkeys():
            self.check_key(subkey)
    
    def analyse(self):
        
        print("[{0}]".format(self.hive_file))
        self.check_key(self.reg.root())
        
        for p, s in sorted(self.tops.items(), key=operator.itemgetter(1), reverse=True):
            p = '\\'.join(p.split('\\')[1:]) if self.drop_cmi else p
            print("{0:<9} {1}".format(s, p))
    
    def is_tops(self, value):
        
        if len(self.tops) < self.max_tops:
            return True
        
        my_size = len(value.raw_data())
        for size in self.tops.values():
            if my_size >= size:
                return True
    
    def drop_smallest(self):
        
        if len(self.tops) < self.max_tops:
            return
        
        self.tops = {k: v for k, v in self.tops.items() if v != min(self.tops.values())}

if __name__ == "__main__":
    
    argp = argparse.ArgumentParser()
    argp.add_argument('target', nargs='+', help='file to analyse. supports globbing: folder{0}*'.format(os.sep))
    argp.add_argument('--max', '-m', help='report the top MAX sizes', type=int, default=20)
    args = argp.parse_args()
    
    targets = []
    for t in args.target:
        if os.path.isfile(t):
            targets.append(t)
        else: # try and glob
            [targets.append(tmp) for tmp in glob.glob(t)]
            
    if len(targets) < 1:
        print("no valid files found. nothing to do.")
    else:
        for t in targets:
            analyser = regsize(t, args.max)
            analyser.analyse()
            
