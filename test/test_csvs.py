# OOIPLACEHOLDER
#
# Copyright 2018 Raytheon Co.

import io
import os
import unittest
from nose.plugins.attrib import attr

@attr('UNIT')
class GeneralUnitTest(unittest.TestCase):
    # declare the global validation objects
    _refdes = set()
    _units = set()
    _parameters = {}
    _types = {}

    def _getpath(self, filename):
        return os.path.join(os.path.dirname(__file__), filename)
    
    def setUp(self):
        # initialize the global objects once
        if not self._refdes:
            with io.open(self._getpath('refdes.txt'),mode='rt',encoding='iso-8859-1') as f:
                for line in f:
                    self._refdes.add(line.strip())
        if not self._units:
            self._units.add('') # empty value is valid
            with io.open(self._getpath('unit.txt'),mode='rt',encoding='iso-8859-1') as f:
                for line in f:
                    self._units.add(line.strip())
        if not self._parameters:
            with io.open(self._getpath('parameter.txt'),mode='rt',encoding='iso-8859-1') as f:
                for line in f:
                    parts = line.strip().split(':')
                    self._parameters[parts[0]] = parts[1]
        if not self._types:
            with io.open(self._getpath('type.txt'),mode='rt',encoding='iso-8859-1') as f:
                for line in f:
                    parts = line.strip().split(':')
                    self._types[parts[0]] = parts[1]

    def _get_parameters(self):
        return self._parameters

    def _get_ref_designators(self):
        return self._refdes

    def _get_types(self):
        return self._types

    def _get_units(self):
        return self._units

    def _is_empty_or_numeric(self, value):
        # if it's empty it's ok
        if len(value) == 0: return True
        # any integer or float value will succeed
        try:
            float(value)
        except ValueError:
            return False

        return True

    def _get_validation_collection(self):
        return {'ReferenceDesignator' : self._get_ref_designators(),
                'ParameterID_R'       : self._get_parameters(),
                'ParameterID_T'       : self._get_parameters(),
                '_Units'              : self._get_units(),
                '_DataLevel'          : ('','L0','L1','L2')
               }

    def _get_validation_positions(self):
        return {'_Array ID'    : (0,8),
                '_Platform ID' : (9,14),
                '_Instrument'  : (18,27)
               }

    def _validate_line(self, header, flds_to_validate, line):
        validation_coll = self._get_validation_collection()
        validation_pos = self._get_validation_positions()

        invalid = []
        parts = line.split('|')
        for index,part in enumerate(parts):
            if index in flds_to_validate:
                # the common fields validated by a collection of values
                #  (ReferenceDesignator, _ParameterID_R/T, _Units)
                if header[index] in validation_coll:
                    vcoll = validation_coll[header[index]]
                    if part not in vcoll:
                        invalid.append(header[index] + ': [' + part + ']')
                # the common fields validated by a portion of the ReferenceDesignator field
                elif header[index] in validation_pos:
                    beg,end = validation_pos[header[index]]
                    refdesidx = header.index('ReferenceDesignator')
                    if part != parts[refdesidx][beg:end]:
                        invalid.append(header[index] + ': [' + part + ']')
                # the global and gradient fields
                elif header[index] in ('GlobalRangeMin','GlobalRangeMax','GradientTest_mindx'):
                    if not self._is_empty_or_numeric(part):
                        invalid.append(header[index] + ': [' + part + ']')
                # the spike fields
                elif header[index] in ('SpikeTest_ACC','SpikeTest_N','SpikeTest_L'):
                    if not self._is_empty_or_numeric(part):
                        invalid.append(header[index] + ': [' + part + ']')
                # the stuck fields
                elif header[index] in ('StuckValueTest_ResolutionR','StuckValueTest_NumRepeatValues'):
                    if not self._is_empty_or_numeric(part):
                        invalid.append(header[index] + ': [' + part + ']')
                # the trend fields
                elif header[index] in ('TrendTest_TimeIntLengthDays','TrendTest_PolynomialOrder','TrendTest_nstd'):
                    if not self._is_empty_or_numeric(part):
                        invalid.append(header[index] + ': [' + part + ']')

        return invalid

    # ###########################################
    # verify the files needed for the tests exist
    # ###########################################

    # the PSVs are built from the CSVs in setuptest.sh to make them pipe-separated files
    # due to the "local" file using commas inside the fields of a handful of records

    def test_globalFileExists(self):
        self.assertTrue(os.path.exists(self._getpath('data_qc_global_range_values.psv')))

    def test_gradientFileExists(self):
        self.assertTrue(os.path.exists(self._getpath('data_qc_gradient_test_values.psv')))

    def test_localFileExists(self):
        self.assertTrue(os.path.exists(self._getpath('data_qc_local_range_values.psv')))

    def test_spikeFileExists(self):
        self.assertTrue(os.path.exists(self._getpath('data_qc_spike_test_values.psv')))

    def test_stuckFileExists(self):
        self.assertTrue(os.path.exists(self._getpath('data_qc_stuck_test_values.psv')))

    def test_trendFileExists(self):
        self.assertTrue(os.path.exists(self._getpath('data_qc_trend_test_values.psv')))

    # these files are generated within setuptest.sh from the asset-management
    # and preload-database repositories

    def test_parameterFileExistsAndIsPopulated(self):
        self.assertTrue(os.path.exists(self._getpath('parameter.txt')))
        parameters = self._get_parameters()
        self.assertTrue(len(parameters) > 0)

    def test_refdesFileExistsAndIsPopulated(self):
        self.assertTrue(os.path.exists(self._getpath('refdes.txt')))
        refdes = self._get_ref_designators()
        self.assertTrue(len(refdes) > 0)

    def test_typeFileExistsAndIsPopulated(self):
        self.assertTrue(os.path.exists(self._getpath('type.txt')))
        types = self._get_types()
        self.assertTrue(len(types) > 0)

    def test_unitFileExistsAndIsPopulated(self):
        self.assertTrue(os.path.exists(self._getpath('unit.txt')))
        units = self._get_units()
        self.assertTrue(len(units) > 0)

    def test_validateGlobalRangeFile(self):
        validfile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        flds_to_validate = None # established from 1st record

        with io.open(self._getpath('data_qc_global_range_values.psv'),mode='rt',encoding='iso-8859-1') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header is None:
                    header = line.split('|')
                    flds_to_validate = range(len(header)) # validate all fields
                    continue
                invalidlist = self._validate_line(header, flds_to_validate, line)
                if invalidlist:
                    validfile = False
                    print('Global record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidlist)
        self.assertTrue(validfile)

    def test_validateGradientTestFile(self):
        validfile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        flds_to_validate = list(range(3) + range(8,12)) # common fields
        flds_to_validate.append(5)                      # and GradientTest_mindx

        with io.open(self._getpath('data_qc_gradient_test_values.psv'),mode='rt',encoding='iso-8859-1') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    continue
                invalidlist = self._validate_line(header, flds_to_validate, line)
                if invalidlist:
                    validfile = False
                    print('Gradient record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidlist)
        self.assertTrue(validfile)

    def test_validateLocalRangeFile(self):
        validfile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        flds_to_validate = list(range(3) + range(8,12)) # common fields

        with io.open(self._getpath('data_qc_local_range_values.psv'),mode='rt',encoding='iso-8859-1') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    flds_to_validate = range(len(header)) # validate all fields
                    continue
                invalidlist = self._validate_line(header, flds_to_validate, line)
                if invalidlist:
                    validfile = False
                    print('Local record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidlist)
        self.assertTrue(validfile)

    def test_validateSpikeTestFile(self):
        validfile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        flds_to_validate = None # established from 1st record

        with io.open(self._getpath('data_qc_spike_test_values.psv'),mode='rt',encoding='iso-8859-1') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    flds_to_validate = range(len(header)) # validate all fields
                    continue
                invalidlist = self._validate_line(header, flds_to_validate, line)
                if invalidlist:
                    validfile = False
                    print('Spike record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidlist)
        self.assertTrue(validfile)

    def test_validateStuckTestFile(self):
        validfile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        flds_to_validate = None # established from 1st record

        with io.open(self._getpath('data_qc_stuck_test_values.psv'),mode='rt',encoding='iso-8859-1') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    flds_to_validate = range(len(header)) # validate all fields
                    continue
                invalidlist = self._validate_line(header, flds_to_validate, line)
                if invalidlist:
                    validfile = False
                    print('Stuck record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidlist)
        self.assertTrue(validfile)

    def test_validateTrendTestFile(self):
        validfile = True # file is valid until proven otherwise
        header = None # obtained from 1st record
        # the numbers of the fields in each data record needing validation
        flds_to_validate = None # established from 1st record

        with io.open(self._getpath('data_qc_trend_test_values.psv'),mode='rt',encoding='iso-8859-1') as f:
            for index,l in enumerate(f):
                line = l.strip() # drop the trailing newline
                # the 1st record contains the headers
                if header == None:
                    header = line.split('|')
                    flds_to_validate = range(len(header)) # validate all fields
                    continue
                invalidlist = self._validate_line(header, flds_to_validate, line)
                if invalidlist:
                    validfile = False
                    print('Trend record invalid ' + str(index+1) + ': ' + line)
                    print(' invalid fields: ', invalidlist)
        self.assertTrue(validfile)
