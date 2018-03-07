# OOIPLACEHOLDER
#
# Copyright 2018 Raytheon Co.

import os
import unittest
from nose.plugins.attrib import attr

@attr('UNIT')
class GeneralUnitTest(unittest.TestCase):
    
    def _getPath(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)

    def _getParameters(self):
        parameters = {} # dictionary: key=name; value=data type number
        with open(self._getPath('parameter.txt'), mode='rt') as f:
            for line in f:
                parts = line.strip().split(':')
                parameters[parts[0]] = parts[1]
        return parameters

    def _getRefDesignators(self):
        refdes = set()
        with open(self._getPath('refdes.txt'), mode='rt') as f:
            for line in f:
                refdes.add(line.strip())
        return refdes

    def _getTypes(self):
        types = {} # dictionary: key=number; value=data type
        with open(self._getPath('type.txt'), mode='rt') as f:
            for line in f:
                parts = line.strip().split(':')
                types[parts[0]] = parts[1]
        return types

    def _getUnits(self):
        units = set()
        units.add('') # empty value is valid
        with open(self._getPath('unit.txt'), mode='rt') as f:
            for line in f:
                units.add(line.strip())
        return units

    def _isEmptyOrNumeric(self, value):
        # if it's empty it's ok
        if len(value) == 0: return True

        # remove leading minus sign if it exists
        if value[:1] == '-': value = value[1:]

        # if there's only one decimal point remove it
        if value.count('.') == 1:
            value = value[:value.index('.')] + value[value.index('.')+1:]

        return value.isdigit()

    def _getValidationCollection(self):
        units = self._getUnits()
        types = self._getTypes()
        parameters = self._getParameters()
        refdes = self._getRefDesignators()

        return {'ReferenceDesignator' : refdes, \
                'ParameterID_R'       : parameters, \
                'ParameterID_T'       : parameters, \
                '_Units'              : units, \
                '_DataLevel'          : ('','L0','L1','L2') \
               }

    def _getValidationPositions(self):
        return {'_Array ID'    : (0,8), \
                '_Platform ID' : (9,14), \
                '_Instrument'  : (18,27)
               }

    def _validateLine(self,header,fldsToValidate,line):
        validationColl = self._getValidationCollection()
        validationPos = self._getValidationPositions()

        invalid = []
        parts = line.split('|')
        for index,part in enumerate(parts):
            if index in fldsToValidate:
                # the common fields validated by a collection of values
                #  (ReferenceDesignator, _ParameterID_R/T, _Units)
                if header[index] in validationColl:
                    vcoll = validationColl[header[index]]
                    if part not in vcoll:
                        invalid.append(header[index] + ': [' + part + ']')
                # the common fields validated by a portion of the ReferenceDesignator field
                elif header[index] in validationPos:
                    beg,end = validationPos[header[index]]
                    refdesIdx = header.index('ReferenceDesignator')
                    if part != parts[refdesIdx][beg:end]:
                        invalid.append(header[index] + ': [' + part + ']')
                # the global and gradient fields
                elif header[index] in ('GlobalRangeMin','GlobalRangeMax','GradientTest_mindx'):
                    if (not self._isEmptyOrNumeric(part)):
                        invalid.append(header[index] + ': [' + part + ']')
                # the spike fields
                elif header[index] in ('SpikeTest_ACC','SpikeTest_N','SpikeTest_L'):
                    if (not self._isEmptyOrNumeric(part)):
                        invalid.append(header[index] + ': [' + part + ']')
                # the stuck fields
                elif header[index] in ('StuckValueTest_ResolutionR','StuckValueTest_NumRepeatValues'):
                    if (not self._isEmptyOrNumeric(part)):
                        invalid.append(header[index] + ': [' + part + ']')
                # the trend fields
                elif header[index] in ('TrendTest_TimeIntLengthDays','TrendTest_PolynomialOrder','TrendTest_nstd'):
                    if (not self._isEmptyOrNumeric(part)):
                        invalid.append(header[index] + ': [' + part + ']')

        return invalid

    # ###########################################
    # verify the files needed for the tests exist
    # ###########################################

    # the PSVs are built from the CSVs in setuptest.sh to make them pipe-separated files
    # due to the "local" file using commas inside the fields of a handful of records

    def test_globalFileExists(self):
        self.assertTrue(os.path.exists(self._getPath('data_qc_global_range_values.psv')))

    def test_gradientFileExists(self):
        self.assertTrue(os.path.exists(self._getPath('data_qc_gradient_test_values.psv')))

    def test_localFileExists(self):
        self.assertTrue(os.path.exists(self._getPath('data_qc_local_range_values.psv')))

    def test_spikeFileExists(self):
        self.assertTrue(os.path.exists(self._getPath('data_qc_spike_test_values.psv')))

    def test_stuckFileExists(self):
        self.assertTrue(os.path.exists(self._getPath('data_qc_stuck_test_values.psv')))

    def test_trendFileExists(self):
        self.assertTrue(os.path.exists(self._getPath('data_qc_trend_test_values.psv')))

    # these files are generated within setuptest.sh from the asset-management
    # and preload-database repositories

    def test_parameterFileExistsAndIsPopulated(self):
        self.assertTrue(os.path.exists(self._getPath('parameter.txt')))
        parameters = self._getParameters()
        self.assertTrue(len(parameters) > 0)

    def test_refdesFileExistsAndIsPopulated(self):
        self.assertTrue(os.path.exists(self._getPath('refdes.txt')))
        refdes = self._getRefDesignators()
        self.assertTrue(len(refdes) > 0)

    def test_typeFileExistsAndIsPopulated(self):
        self.assertTrue(os.path.exists(self._getPath('type.txt')))
        types = self._getTypes()
        self.assertTrue(len(types) > 0)

    def test_unitFileExistsAndIsPopulated(self):
        self.assertTrue(os.path.exists(self._getPath('unit.txt')))
        units = self._getUnits()
        self.assertTrue(len(units) > 0)

    def test_validateGlobalRangeFile(self):
        validFile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        fldsToValidate = None # established from 1st record

        with open(self._getPath('data_qc_global_range_values.psv'), mode='rt') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    fldsToValidate = range(len(header)) # validate all fields
                    continue
                invalidList = self._validateLine(header,fldsToValidate,line)
                if invalidList:
                    validFile = False
                    print('Global record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidList)
        self.assertTrue(validFile)

    def test_validateGradientTestFile(self):
        validFile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        fldsToValidate = list(range(3) + range(8,12)) # common fields
        fldsToValidate.append(5)                      # and GradientTest_mindx

        with open(self._getPath('data_qc_gradient_test_values.psv'), mode='rt') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    continue
                invalidList = self._validateLine(header,fldsToValidate,line)
                if invalidList:
                    validFile = False
                    print('Gradient record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidList)
        self.assertTrue(validFile)

    def test_validateLocalRangeFile(self):
        validFile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        fldsToValidate = list(range(3) + range(8,12)) # common fields

        with open(self._getPath('data_qc_local_range_values.psv'), mode='rt') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    fldsToValidate = range(len(header)) # validate all fields
                    continue
                invalidList = self._validateLine(header,fldsToValidate,line)
                if invalidList:
                    validFile = False
                    print('Local record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidList)
        self.assertTrue(validFile)

    def test_validateSpikeTestFile(self):
        validFile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        fldsToValidate = None # established from 1st record

        with open(self._getPath('data_qc_spike_test_values.psv'), mode='rt') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    fldsToValidate = range(len(header)) # validate all fields
                    continue
                invalidList = self._validateLine(header,fldsToValidate,line)
                if invalidList:
                    validFile = False
                    print('Spike record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidList)
        self.assertTrue(validFile)

    def test_validateStuckTestFile(self):
        validFile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        fldsToValidate = None # established from 1st record

        with open(self._getPath('data_qc_stuck_test_values.psv'), mode='rt') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    fldsToValidate = range(len(header)) # validate all fields
                    continue
                invalidList = self._validateLine(header,fldsToValidate,line)
                if invalidList:
                    validFile = False
                    print('Stuck record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidList)
        self.assertTrue(validFile)

    def test_validateTrendTestFile(self):
        validFile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        fldsToValidate = None # established from 1st record

        with open(self._getPath('data_qc_trend_test_values.psv'), mode='rt') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    fldsToValidate = range(len(header)) # validate all fields
                    continue
                invalidList = self._validateLine(header,fldsToValidate,line)
                if invalidList:
                    validFile = False
                    print('Trend record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidList)
        self.assertTrue(validFile)
