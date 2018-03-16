# OOIPLACEHOLDER
#
# Copyright 2018 Raytheon Co.

import glob
import io
import os
import pandas as pd
import re
import unittest
from nose.plugins.attrib import attr


@attr('UNIT')
class GeneralUnitTest(unittest.TestCase):
    # declare misc global objects
    _encoding = 'utf-8'

    _validate_dictionary  = {} # populated in setUp
    _validation_positions = {'_Array ID': (0, 8),
                             '_Platform ID': (9, 14),
                             '_Instrument': (18, 27)
                            }

    # declare the global validation objects
    _reference_designators = set()
    _parameters = set()
    _units = set()

    @staticmethod
    def _get_path(file_name):
        return os.path.join(os.path.dirname(__file__), file_name)

    @staticmethod
    def _is_empty_or_numeric(value):
        # if it's empty it's ok
        if len(value) == 0: return True

        # any integer or float value will succeed
        try:
            float(value)
        except ValueError:
            return False

        return True

    def setUp(self):
        # initialize the global objects once
        if not self._reference_designators:
            for file_name in glob.glob("*_Deploy.csv"):
                file = pd.read_csv(self._get_path(file_name), encoding=self._encoding, na_filter=False)
                header = list(file)
                # the placement of this column varies from one CSV to another
                column_index = header.index('Reference Designator')
                # the "i" variable isn't used but is needed to catch the returned value
                for i,line in file.iterrows():
                    self._reference_designators.add(line[column_index])

        if not self._units:
            unit_regex = re.compile(r'INSERT INTO "unit" VALUES\(\d+,\'(.*)\'\)')
            with io.open(self._get_path('preload_database.sql'), mode='rt', encoding=self._encoding) as file:
                for line in file:
                    match_it = re.search(unit_regex, line)
                    if match_it:
                        self._units.add(match_it.group(1))
            self._units.add('') # empty value is valid

        if not self._parameters:
            # this regex extracts all the values after the initial numerical value
            param_regex = re.compile(r'INSERT INTO "parameter" VALUES\(\d+,\'(.*)\',.*')
            with io.open(self._get_path('preload_database.sql'), mode='rt', encoding=self._encoding) as file:
                for line in file:
                    match_it = re.search(param_regex, line)
                    if match_it:
                        # only the value up to the 1st tick-mark is needed
                        name = match_it.group(1).split("'")
                        self._parameters.add(name[0])

        if not self._validate_dictionary:
            _validate_dictionary = {'ReferenceDesignator': self._reference_designators,
                                    'ParameterID_R': self._parameters,
                                    'ParameterID_T': self._parameters,
                                    '_Units': self._units,
                                    '_DataLevel': ('', 'L0', 'L1', 'L2')
                                   }

    def _get_parameters(self):
        return self._parameters

    def _get_ref_designators(self):
        return self._reference_designators

    def _get_units(self):
        return self._units

    def _get_validation_dictionary(self):
        return self._validate_dictionary

    def _get_validation_positions(self):
        return self._validation_positions

    def _validate_line(self, header, fields_to_validate, line):
        validation_dictionary = self._get_validation_dictionary()
        validation_positions  = self._get_validation_positions()

        # If this remains empty the line is valid
        invalid_entries = []
        for index,column in enumerate(line):
            if index in fields_to_validate:
                # the common fields validated by a collection of values
                #  (ReferenceDesignator, _ParameterID_R/T, _Units)
                if header[index] in validation_dictionary:
                    validation_collection = validation_dictionary[header[index]]
                    if column not in validation_collection:
                        invalid_entries.append(header[index] + ': [' + column + ']')
                # the common fields validated by a portion of the ReferenceDesignator field
                elif header[index] in validation_positions:
                    begin,end = validation_positions[header[index]]
                    column_index = header.index('ReferenceDesignator')
                    if column != line[column_index][begin:end]:
                        invalid_entries.append(header[index] + ': [' + column + ']')
                # the global and gradient fields
                elif header[index] in ('GlobalRangeMin','GlobalRangeMax','GradientTest_mindx'):
                    if not self._is_empty_or_numeric(column):
                        invalid_entries.append(header[index] + ': [' + str(column) + ']')
                # the spike fields
                elif header[index] in ('SpikeTest_ACC','SpikeTest_N','SpikeTest_L'):
                    if not self._is_empty_or_numeric(column):
                        invalid_entries.append(header[index] + ': [' + str(column) + ']')
                # the stuck fields
                elif header[index] in ('StuckValueTest_ResolutionR','StuckValueTest_NumRepeatValues'):
                    if not self._is_empty_or_numeric(column):
                        invalid_entries.append(header[index] + ': [' + str(column) + ']')
                # the trend fields
                elif header[index] in ('TrendTest_TimeIntLengthDays','TrendTest_PolynomialOrder','TrendTest_nstd'):
                    if not self._is_empty_or_numeric(column):
                        invalid_entries.append(header[index] + ': [' + str(column) + ']')

        return invalid_entries

    def test_validate_global_range_file(self):
        valid_file = True # file is valid until proven otherwise
        # this gets the file's header line
        f = pd.read_csv(self._get_path('../data_qc_global_range_values.csv'),
                        encoding=self._encoding, na_filter=False)
        # this gets the file's header line
        header = list(f)
        # all the numbers of the fields in each data record needing validation
        fields_to_validate = range(len(header)) # validate all fields

        for index,line in f.iterrows():
            invalid_list = self._validate_line(header, fields_to_validate, line)
            # if it contains entries the file is invalid
            if invalid_list:
                valid_file = False
                print('Global record invalid ' + str(index+1) + ', ')
                print(' invalid fields: ', invalid_list)

        self.assertTrue(valid_file)

    def test_validate_gradient_test_file(self):
        valid_file = True # file is valid until proven otherwise
        # this gets the file's header line
        f = pd.read_csv(self._get_path('../data_qc_gradient_test_values.csv'),
                        encoding=self._encoding, na_filter=False)
        # this gets the file's header line
        header = list(f)
        # the numbers of the fields in each data record needing validation
        fields_to_validate = list(range(3) + range(8,12)) # validate common fields
        fields_to_validate.append(5)                      # and GradientTest_mindx

        for index,line in f.iterrows():
            invalid_list = self._validate_line(header, fields_to_validate, line)
            # if it contains entries the file is invalid
            if invalid_list:
                valid_file = False
                print('Gradient record invalid ' + str(index+1) + ', ')
                print(' invalid fields: ', invalid_list)

        self.assertTrue(valid_file)

    def test_validate_local_range_file(self):
        valid_file = True # file is valid until proven otherwise
        f = pd.read_csv(self._get_path('../data_qc_local_range_values.csv'),
                        encoding=self._encoding, na_filter=False)
        # this gets the file's header line
        header = list(f)
        # the numbers of the fields in each data record needing validation
        fields_to_validate = list(range(3) + range(8,12)) # validate common fields

        for index,line in f.iterrows():
            invalid_list = self._validate_line(header, fields_to_validate, line)
            # if it contains entries the file is invalid
            if invalid_list:
                valid_file = False
                print('Local record invalid ' + str(index+1) + ', ')
                print(' invalid fields: ', invalid_list)

        self.assertTrue(valid_file)

    def test_validate_spike_test_file(self):
        valid_file = True # file is valid until proven otherwise
        f = pd.read_csv(self._get_path('../data_qc_spike_test_values.csv'),
                        encoding=self._encoding, na_filter=False)
        # this gets the file's header line
        header = list(f)
        fields_to_validate = range(len(header)) # validate all fields

        for index,line in f.iterrows():
            invalid_list = self._validate_line(header, fields_to_validate, line)
            # if it contains entries the file is invalid
            if invalid_list:
                valid_file = False
                print('Spike record invalid ' + str(index+1) + ', ')
                print(' invalid fields: ', invalid_list)

        self.assertTrue(valid_file)

    def test_validate_stuck_test_file(self):
        valid_file = True # file is valid until proven otherwise
        f = pd.read_csv(self._get_path('../data_qc_stuck_test_values.csv'),
                        encoding=self._encoding, na_filter=False)
        # this gets the file's header line
        header = list(f)
        fields_to_validate = range(len(header)) # validate all fields

        for index,line in f.iterrows():
            invalid_list = self._validate_line(header, fields_to_validate, line)
            # if it contains entries the file is invalid
            if invalid_list:
                valid_file = False
                print('Stuck record invalid ' + str(index+1) + ', ')
                print(' invalid fields: ', invalid_list)

        self.assertTrue(valid_file)

    def test_validate_trend_test_file(self):
        valid_file = True # file is valid until proven otherwise
        f = pd.read_csv(self._get_path('../data_qc_trend_test_values.csv'),
                        encoding=self._encoding, na_filter=False)
        # this gets the file's header line
        header = list(f)
        fields_to_validate = range(len(header)) # validate all fields

        for index,line in f.iterrows():
            invalid_list = self._validate_line(header, fields_to_validate, line)
            # if it contains entries the file is invalid
            if invalid_list:
                valid_file = False
                print('Trend record invalid ' + str(index+1) + ', ')
                print(' invalid fields: ', invalid_list)

        self.assertTrue(valid_file)
