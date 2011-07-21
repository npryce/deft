
from functools import partial
import os
import csv
import yaml


class YamlFormat(object):
    @staticmethod
    def load(input):
        return yaml.safe_load(input)
    
    @staticmethod
    def save(obj, output):
        yaml.safe_dump(obj, output, default_flow_style=False)


class TextFormat(object):
    @staticmethod
    def load(input):
        return input.read()
    
    @staticmethod
    def save(text, output):
        return output.write(text)


class LinesFormat(object):
    def __init__(self, sequence_type):
        self.sequence_type = sequence_type
    
    def load(self, input):
        return self.sequence_type(input.read().splitlines())
    
    def save(self, lines, output):
        for line in lines:
            output.write(line)
            output.write("\n")


def write_table_as_text(features_table, out):
    if not features_table:
        return
    
    max_elts = partial(map, max)
    
    alignl = "{1:<{0}}".format
    alignr = "{1:>{0}}".format
    def align_for(v):
        return alignr if type(v) == int else alignl

    table = [map(str,t) for t in features_table]
    zeros = [0 for elt in features_table[0]]
    aligns = [align_for(v) for v in features_table[0]]
    col_widths = reduce(max_elts, [map(len,t) for t in table], zeros)
    col_formatters = map(partial, aligns, col_widths)
    formatted_table = [[col_formatters[i](row[i]) for i in range(len(row))] for row in table]
    lines = [" ".join(row) for row in formatted_table]
    
    for line in lines:
        out.write(line)
        out.write(os.linesep)


def write_table_as_csv(table, output):
    csv_output = csv.writer(output)
    csv_output.writerows(table)


def write_repr(thing, output):
    output.write(repr(thing))
