import sys
import os
from Bio.Affy import CelFile
import csv
import json
#import numpy
#import re
#import datetime
#from pprint import pprint
#numpy.set_printoptions(threshold=numpy.nan)
#numpy.set_printoptions(threshold=300)

maxInt = sys.maxsize
decrement = True
while decrement:
    decrement = False
    try:
        csv.field_size_limit(maxInt)
    except OverflowError:
        maxInt = int(maxInt/10)
        decrement = True

if not os.path.exists('./json_temp'):
    os.makedirs('./json_temp')

cel_filenames = ['159834720_B', '597785396_B']

cel_results = {}
for cel_filename in cel_filenames:
    try:
        cel_results[cel_filename] = json.load(open('./json_temp/' + cel_filename + '.CEL.json'))
    except FileNotFoundError:
        with open('./input/' + cel_filename + '.CEL', 'rb') as handle:
            c = CelFile.read(handle)
            cel_results[cel_filename] = {}
            for i in range(c.nrows):
                cel_results[cel_filename][i] = {}
                for j in range(c.ncols):
                    cel_results[cel_filename][i][j] = c.intensities[i][j]
        with open('./json_temp/' + cel_filename + '.CEL.json', 'w', encoding='utf-8') as results:
            results.write(json.dumps(cel_results[cel_filename]))

try:
    cdf_results = json.load(open('./json_temp/HuEx-1_0-st-v2.text.cdf.json'))
except FileNotFoundError:
    cdf_results = {}
    with open('./input/HuEx-1_0-st-v2.text.cdf', 'r') as file:
        reader = csv.reader(file, delimiter='\t')
        counter = maxInt
        lower_limit = 7
        upper_limit_add = 4
        for line in reader:
            if not line:
                counter = 0
                continue
            if '_Block1]' in line[0]:
                counter = 0
                pid = line[0][len('[Unit'): -len('_Block1]')]
                cdf_results[pid] = {}
                cdf_results[pid]['x_coordinates'] = []
                cdf_results[pid]['y_coordinates'] = []
                cdf_results[pid]['sequences'] = []
                cdf_results[pid]['intensities'] = {}
            if counter == 4:
                upper_limit = int(line[0].split('=', 1)[1])
            if lower_limit < counter < (lower_limit + upper_limit_add):
                x_coord = str(line[0].split('=', 1)[1])
                y_coord = str(line[1])
                sequence = line[2]
                for cel_filename in cel_filenames:
                    intensity = cel_results[cel_filename][x_coord][y_coord]
                    if cel_filename not in cdf_results[pid]['intensities']:
                        cdf_results[pid]['intensities'][cel_filename] = []
                    cdf_results[pid]['intensities'][cel_filename].append(intensity)
                cdf_results[pid]['x_coordinates'].append(x_coord)
                cdf_results[pid]['y_coordinates'].append(y_coord)
                cdf_results[pid]['sequences'].append(sequence)
            counter += 1

    with open('./json_temp/HuEx-1_0-st-v2.text.cdf.json', 'w', encoding='utf-8') as results:
        results.write(json.dumps(cdf_results))

try:
    csv_results = json.load(open('./json_temp/HuEx-1_0-st-v2.na36.hg19.probeset.csv.json'))
except FileNotFoundError:
    csv_results = {}
    with open('./input/HuEx-1_0-st-v2.na36.hg19.probeset.csv', 'r') as f:
        reader = csv.reader(f)
        skip_meta_counter = 0
        iteration_counter = 0
        transcript_cluster_id = 0
        for row in reader:
            if skip_meta_counter < 23:
                skip_meta_counter += 1
                continue

            transcript_cluster_id = row[6]
            probeset_id = row[0]

            tid = str(transcript_cluster_id)
            pid = str(probeset_id)

            if pid not in cdf_results:
                continue

            if tid not in csv_results:
                csv_results[tid] = {}
            if pid not in csv_results[tid]:
                csv_results[tid][pid] = {}

            csv_results[tid][pid]['sequences'] = cdf_results[pid]['sequences']
            csv_results[tid][pid]['intensities'] = cdf_results[pid]['intensities']
            csv_results[tid][pid]['x_coordinates'] = cdf_results[pid]['x_coordinates']
            csv_results[tid][pid]['y_coordinates'] = cdf_results[pid]['y_coordinates']
            csv_results[tid][pid]['chromosome'] = row[1][-1:]
            if row[9] == '---':
                csv_results[tid][pid]['HGNC'] = ''
            else:
                csv_results[tid][pid]['HGNC'] = row[9].split('//')[1]

    with open('./json_temp/HuEx-1_0-st-v2.na36.hg19.probeset.csv.json','w', encoding='utf-8') as results:
        #results.write(json.dumps(csv_results, indent=4))
        results.write(json.dumps(csv_results))