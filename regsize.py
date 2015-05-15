#!/usr/bin/env python

import argparse
import glob
import math
import operator
import os
from Registry import Registry


class RegSize:
    """
    Main functionality of script. Parses the hive, finding the largest values based on the size of their data.
    """

    def __init__(self, hive_file, max_sizes, do_ent):

        self.hive_file = hive_file
        self.max_sizes = max_sizes
        self.do_ent = do_ent
        self.reg = Registry.Registry(self.hive_file)
        self.tops = {}
        self.drop_cmi = self.reg.root().path().split('\\')[0][0:4] == 'CMI-'

    def check_key(self, key):

        for value in key.values():
            if self.is_tops(value):
                raw_len = len(value.raw_data())
                if len(self.tops) > 0 and raw_len > min(self.tops.values()):
                    self.drop_smallest()
                self.tops[key.path() + '\\' + value.name()] = raw_len

        for subkey in key.subkeys():
            self.check_key(subkey)

    def analyse(self):

        print('[{}]'.format(self.hive_file))
        self.check_key(self.reg.root())

        for p, s in sorted(self.tops.items(), key=operator.itemgetter(1), reverse=True):
            if self.drop_cmi:
                p = '\\'.join(p.split('\\')[1:])
            if self.do_ent:
                key = self.reg.open('\\'.join(p.split('\\')[1:-1]))
                print('{0:<6} {1:.5f} {2}'.format(s, calc_shannon(key.value(p.split('\\')[-1]).raw_data()), p))
            else:
                print('{0:<9} {1}'.format(s, p))

    def is_tops(self, value):

        if len(self.tops) < self.max_sizes:
            return True

        my_size = len(value.raw_data())
        for size in self.tops.values():
            if my_size >= size:
                return True

    def drop_smallest(self):

        if len(self.tops) < self.max_sizes:
            return

        self.tops = {k: v for k, v in self.tops.items() if v != min(self.tops.values())}


def calc_shannon(data):
    """
    Calculates the Shannon entropy of data. The closer to 8, the higher the entropy.
    :param data: Calculate the Shannon entropy of this data
    :return: A float between 0 and 8
    """

    byte_array = map(ord, data)
    data_size = len(byte_array)

    # calculate the frequency of each byte value
    byte_count = [0 for b in xrange(256)]
    for b in byte_array:
        byte_count[b] += 1
    byte_freq = []
    for c in byte_count:
        byte_freq.append(float(c) / data_size)

    # Shannon entropy
    ent = 0.0
    for freq in byte_freq:
        if freq > 0:
            ent += freq * math.log(freq, 2)
    return ent * -1


if __name__ == '__main__':

    argp = argparse.ArgumentParser()
    argp.add_argument('target', nargs='+', help='file to analyse. supports globbing: folder{0}*'.format(os.sep))
    argp.add_argument('--max', '-m', help='report the top MAX sizes', type=int, default=20)
    argp.add_argument('--no-ent', '-E', help='show Shannon entropy (0-8)', action='store_true')
    args = argp.parse_args()

    targets = []
    for t in args.target:
        if os.path.isfile(t):
            targets.append(t)
        else:  # try and glob
            [targets.append(tmp) for tmp in glob.glob(t)]

    if len(targets) < 1:
        print('no valid files found. nothing to do.')
    else:
        for t in targets:
            analyser = RegSize(t, args.max, False if args.no_ent else True)
            analyser.analyse()
