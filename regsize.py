#!/usr/bin/env python

import argparse
import csv
import glob
import math
import os
import sys
from collections import namedtuple
from operator import attrgetter
from Registry import Registry


class RegSize:
    """
    Main functionality of script. Parses the hive, finding the largest values based on the size of their data.
    """

    def __init__(self, hive_file, max_sizes, do_ent, as_csv):

        self.KeyValue = namedtuple('KeyValue', 'key value size')
        self.hive_file = hive_file
        self.max_sizes = max_sizes
        self.do_ent = do_ent
        self.as_csv = as_csv
        self.reg = Registry.Registry(self.hive_file)
        self.tops = []

    def check_key(self, key):

        min_size = 0
        try:            
            for value in key.values():
                if self.is_tops(value):
                    raw_len = len(value.raw_data())
                    if len(self.tops) > 0:
                        min_size = min(self.tops, key=attrgetter('size')).size
                    if raw_len > min_size:
                        self.drop_smallest(min_size)
                    self.tops.append(self.KeyValue(key.path(), value.name(), raw_len))
        except Registry.RegistryParse.ParseException as parseEx:
            print "ParseException: {}".format(parseEx)
            print key.path()

        try:
            for subkey in key.subkeys():
                self.check_key(subkey)
        except Registry.RegistryParse.ParseException as parseEx:
            print "ParseException: {}".format(parseEx)
            print key.path()

    def analyse(self):

        if not self.as_csv:
            print('[{}]'.format(self.hive_file))

        self.check_key(self.reg.root())

        if self.as_csv:
            self.to_csv()
        else:
            self.to_text()

    def is_tops(self, value):

        if len(self.tops) < self.max_sizes:
            return True

        my_size = len(value.raw_data())
        for k, v, s in self.tops:
            if my_size >= s:
                return True

    def drop_smallest(self, min_size):

        if len(self.tops) < self.max_sizes:
            return

        self.tops = [kv for kv in self.tops if kv.size != min_size]

    def to_text(self):

        if self.do_ent:
            for path, value, size in sorted(self.tops, key=attrgetter('size'), reverse=True):
                path = '\\'.join(path.split('\\')[1:])
                key = self.reg.open(path)
                print('{:<9} {:.5f} {}\\{}'.format(size, calc_shannon(key.value(value).raw_data()), path, value))
        else:
            for path, value, size in sorted(self.tops, key=attrgetter('size'), reverse=True):
                path = '\\'.join(path.split('\\')[1:])
                print('{:<9} {}\\{}'.format(size, path, value))

    def to_csv(self):

        csv_writer = csv.writer(sys.stdout, quotechar='"')

        if self.do_ent:
            csv_writer.writerow(['hivefile', 'size', 'entropy', 'key'])
            for path, value, size in sorted(self.tops, key=attrgetter('size'), reverse=True):
                path = '\\'.join(path.split('\\')[1:])
                key = self.reg.open(path)
                csv_writer.writerow([self.hive_file, size, calc_shannon(key.value(value).raw_data()), path+'\\'+value])
        else:
            csv_writer.writerow(['hivefile', 'size', 'key'])
            for path, value, size in sorted(self.tops, key=attrgetter('size'), reverse=True):
                path = '\\'.join(path.split('\\')[1:])
                csv_writer.writerow([self.hive_file, size, path+'\\'+value])


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
    argp.add_argument('--no-ent', '-E', help='don\'t calculate the Shannon entropy', action='store_true')
    argp.add_argument('--csv', '-c', help='output in CSV format', action='store_true')
    args = argp.parse_args()

    targets = []
    for t in args.target:
        if os.path.isfile(t):
            targets.append(t)
        else:  # try and glob
            [targets.append(tmp) for tmp in glob.glob(t) if os.path.isfile(tmp)]

    if len(targets) < 1:
        print('no valid files found. nothing to do.')
    else:
        for t in targets:
            analyser = RegSize(t, args.max, False if args.no_ent else True, args.csv)
            analyser.analyse()