

import argparse
import csv
import pathlib
import pandas as pd
import re

def validate_grossRangeFile(file,verbose):
    if verbose:
        print('validating gross range file: ', file)
    # define file format
    header = 'subsite,node,sensor,stream,parameters,qcConfig,source,notes'
    colNum = 8
    regexDict = {}
    regexDict[0] = re.compile('#*[0-9A-Za-z]{8}')
    regexDict[1] = re.compile('[0-9A-Za-z]{5}')
    regexDict[2] = re.compile('[0-9A-Za-z]{2}-[0-9A-Za-z]{9}')
    regexDict[3] = re.compile('[0-9a-z]+')
    regexDict[4] = re.compile('{\'inp\': \'.*\'}')
    regexDict[5] = re.compile('{\'qartod\': {\'gross_range_test\': {\'suspect_span\': \[-*[0-9]+\.*[0-9]*, -*[0-9]+\.*[0-9]*\], \'fail_span\': \[-*[0-9]+\.*[0-9]*, -*[0-9]+\.*[0-9]*\]}}}')
    regexDict[6] = re.compile('.*')
    regexDict[7] = re.compile('.*')

    fileContents = open(file, 'r')
    Lines = fileContents.readlines()
    firstline = Lines[0].rstrip()
    if firstline != header:
        missingColumns = [ele for ele in header.split(',') if ele not in firstline.split(',')]
        print('file header missing columns: ', missingColumns)
    for i in range(1,len(Lines)):
        cStr = Lines[i]
        line = [ '{}'.format(x) for x in list(csv.reader([cStr], delimiter=',', quotechar='"'))[0] ]
        if len(line) != (colNum):
            print('incorrect number of columns!', line)
        for j in range(0,len(line)):
            if not regexDict[j].match(line[j]):
                print('column not formatted correctly: ', line[j])
   


def validate_climatologyFile(file,verbose):
    if verbose:
        print('validating climatology file: ', file)
    # define file format
    header = 'subsite,node,sensor,stream,parameters,climatologyTable,source,notes'
    colNum = 8
    regexDict = {}
    regexDict[0] = re.compile('#*[0-9A-Za-z]{8}')
    regexDict[1] = re.compile('[0-9A-Za-z]{5}')
    regexDict[2] = re.compile('[0-9A-Za-z]{2}-[0-9A-Za-z]{9}')
    regexDict[3] = re.compile('[0-9a-z]+')
    regexDict[4] = re.compile('{\'inp\': \'.*\', \'tinp\': \'.*\', \'zinp\': \'.*\'}')
    regexDict[5] = re.compile('climatology_tables\/[0-9A-Za-z]{8}-[0-9A-Za-z]{5}-[0-9A-Za-z]{2}-[0-9A-Za-z]{9}-.*\.csv')
    regexDict[6] = re.compile('.*')
    regexDict[7] = re.compile('.*')

    fileContents = open(file, 'r')
    Lines = fileContents.readlines()
    firstline = Lines[0].rstrip()
    if firstline != header:
        missingColumns = [ele for ele in header.split(',') if ele not in firstline.split(',')]
        print('file header missing columns: ', missingColumns)
    for i in range(1,len(Lines)):
        cStr = Lines[i]
        line = [ '{}'.format(x) for x in list(csv.reader([cStr], delimiter=',', quotechar='"'))[0] ]
        if len(line) != (colNum):
            print('incorrect number of columns!', line)
        for j in range(0,len(line)):
            if not regexDict[j].match(line[j]):
                print('column not formatted correctly: ', line[j])
   


def validate_climatologyTable(file,verbose):
    if verbose:
        print('validating climatology Table file: ', file)
    # define file format
    header = ',"[1, 1]","[2, 2]","[3, 3]","[4, 4]","[5, 5]","[6, 6]","[7, 7]","[8, 8]","[9, 9]","[10, 10]","[11, 11]","[12, 12]"'
    colNum = 13
    
    fileContents = open(file, 'r')
    Lines = fileContents.readlines()
    firstline = Lines[0].rstrip()
    regexEntry = re.compile('[-*[0-9]+\.*[0-9]*, -*[0-9]+\.*[0-9]*]')
    # [nan, nan]
    regexNaN = re.compile('\[nan,\s*nan\]')
    if len(Lines) == 1:
        regexDepth = re.compile('[0, 0]')
    else:
        regexDepth = regexEntry
    if firstline != header:
        missingColumns = [ele for ele in header.split(',') if ele not in firstline.split(',')]
        print('error found in climatology Table file: ', file)
        print('file header missing columns: ', missingColumns)
    for i in range(1,len(Lines)):
        cStr = Lines[i]
        line = [ '{}'.format(x) for x in list(csv.reader([cStr], delimiter=',', quotechar='"'))[0] ]
        if len(line) != (colNum):
            print('parsing error in climatology Table file: ', file)
            print('incorrect number of columns!', line)
        
        if not regexDepth.match(line[0]):
            print('parsing error in climatology Table file: ', file)
            print('depth bracket not formtted corretly: ', line[0])
        for j in range(1,len(line)):
            if not regexEntry.match(line[j]):
                if not regexNaN.match(line[j]):
                    print(regexNaN.match(line[j]))
                    print('parsing error in climatology Table file: {}, line {}, column {}'.format(file,i,j))
                    print(line[j])
   


def parse_args():
    arg_parser = argparse.ArgumentParser(
        description='qartod file validator'
    )
    arg_parser.add_argument('--messages', type=str, default='errors')

    return arg_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.messages == 'verbose':
        verbose = True
    elif args.messages == 'errors':
        verbose = False

    qc_lookup_root = '../'
    qc_sensorTypes = ['ctdav','ctdbp','ctdgv','ctdmo','ctdpf','metbk','pco2a','pco2w','phsen','presf']
    qc_testFolderTypes = {'climatology_tables': validate_climatologyTable}

    # define the path
    currentDirectory = pathlib.Path(qc_lookup_root)

    for item in currentDirectory.iterdir():
        if item.is_file():
            print('unknown file in qartod root directory: ', item)
        elif item.is_dir():
            if item.stem not in qc_sensorTypes:
                print('unknown sensor type...skipping directory: ', item.stem)
            else:
                for subItem in item.iterdir():
                    if subItem.is_dir():
                        if subItem.stem not in qc_testFolderTypes.keys():
                            print('unknown test type: ', subItem.stem)
                        else:
                            for file in subItem.iterdir():
                                if file.is_file():
                                    qc_testFolderTypes[str(subItem.stem)](file,verbose)
                                else:
                                    print('unknown item in test table folder')
                        
                    if subItem.is_file():
                        gr_regex = re.compile('(%s)_qartod_gross_range_test_values.*'%subItem.parent.stem)
                        cl_regex = re.compile('(%s)_qartod_climatology_test_values.*'%subItem.parent.stem)
                        if gr_regex.match(str(subItem.stem)):
                            validate_grossRangeFile(subItem,verbose)
                        elif cl_regex.match(str(subItem.stem)):
                            validate_climatologyFile(subItem,verbose)
                        else:
                            print('unknown or misnamed file: ', subItem)
