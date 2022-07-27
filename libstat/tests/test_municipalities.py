from data.municipalities import (
    municipality_code_from,
    municipality_code_from_county_code,
)
from libstat.tests import MongoTestCase


class TestMunicipalityCodeConversion(MongoTestCase):
    def test_converts_from_int_to_string(self):
        self.assertEqual("1203", municipality_code_from(1203))

    def test_converts_from_float_to_string(self):
        self.assertEqual("1203", municipality_code_from(1203.0))

    def test_converts_from_string_to_string(self):
        self.assertEqual("1203", municipality_code_from("1203"))

    def test_converts_zero_int(self):
        self.assertEqual("0000", municipality_code_from_county_code(0))

    def test_converts_zero_float(self):
        self.assertEqual("0000", municipality_code_from_county_code(0.0))

    def test_returns_none_for_empty_string(self):
        self.assertEqual(None, municipality_code_from_county_code(""))

    def test_returns_none_for_none(self):
        self.assertEqual(None, municipality_code_from_county_code(None))

    def test_pads_with_zeroes_when_int(self):
        self.assertEqual("0023", municipality_code_from(23))

    def test_pads_with_zeroes_when_float(self):
        self.assertEqual("0023", municipality_code_from(23.0))

    def test_pads_with_zeroes_when_string(self):
        self.assertEqual("0023", municipality_code_from("23"))

    def test_does_not_allow_codes_with_more_than_four_digits(self):
        self.assertRaises(ValueError, municipality_code_from, 14203)

    def test_does_not_allow_negative_codes(self):
        self.assertRaises(ValueError, municipality_code_from, -1234)


class TestCountyCodeConversion(MongoTestCase):
    def test_converts_from_int_to_string(self):
        self.assertEqual("1200", municipality_code_from_county_code(12))

    def test_converts_from_float_to_string(self):
        self.assertEqual("1200", municipality_code_from_county_code(12.0))

    def test_converts_from_string_to_string(self):
        self.assertEqual("1200", municipality_code_from_county_code("12"))

    def test_pads_with_zeroes_when_int(self):
        self.assertEqual("0400", municipality_code_from_county_code(4))

    def test_pads_with_zeroes_when_float(self):
        self.assertEqual("0400", municipality_code_from_county_code(4.0))

    def test_pads_with_zeroes_when_string(self):
        self.assertEqual("0400", municipality_code_from_county_code("04"))

    def test_does_not_allow_codes_with_more_than_two_digits(self):
        self.assertRaises(ValueError, municipality_code_from_county_code, 123)

    def test_does_not_allow_negative_codes(self):
        self.assertRaises(ValueError, municipality_code_from_county_code, -12)
