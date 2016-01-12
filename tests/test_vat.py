import unittest
from decimal import Decimal as D
from oscar_vat_moss import vat

class AddressTest(unittest.TestCase):
    ADDRESSES = (
        # Shipping address attributes  # Expected rate
        ({'line4': 'Vienna',
          'country': 'AT',
          'postcode': 1010},           D('0.20')),
        ({'line4': 'Berlin',
          'country': 'DE',
          'postcode': 10001},          D('0.19')),
        ({'line4': 'Jungholz',
          'country': 'AT',
          'postcode': 6691},           D('0.19')),
        ({'line4': 'Galway',
          'country': 'IE',
         },                            D('0.23')),
    )

    def test_lookup_vat_by_city(self):
        for addr, expected_rate in self.ADDRESSES:
            country_code = addr.get('country')
            postcode = addr.get('postcode')
            city = addr.get('line4')
            result_rate = vat.lookup_vat_by_city(country_code, postcode, city)
            self.assertEqual(result_rate,
                             expected_rate,
                             msg="Unexpected VAT rate returned for %s: %s" % (addr, result_rate))


class PhoneNumberTest(unittest.TestCase):
    PHONE_NUMBERS = (
        # Shipping address attributes dictionary  # Expected rate
        ({'phone_number': '+43 1 234 5678',
         },                                       D('0.20')),
        ({'phone_number': '+49 170 12345',
         },                                       D('0.19')),
    )

    def test_lookup_vat_by_phone_number(self):
        for num, expected_rate in self.PHONE_NUMBERS:
            phone_number = num.get('phone_number')
            country_code = num.get('country')
            result_rate = vat.lookup_vat_by_phone_number(phone_number, country_code)
            self.assertEqual(result_rate,
                             expected_rate,
                             msg="Unexpected VAT rate returned for %s: %s" % (num, result_rate))

class VATINTest(unittest.TestCase):
    VALID_VATINS = (
        # VATIN         # Company name
        ('ATU66688202', 'hastexo Professional Services GmbH'),
        ('ATU66688202', 'HASTEXO PROFESSIONAL SERVICES GMBH'),
        ('ATU66688202', 'hastexo Professional Services GmbH (Procurement Department)'),
        )
    INVALID_VATINS = (
        # VATIN         # Incorrect company name
        ('ATU66688202', 'Example, Inc.'),
        ('ATU66688202', 'hastexo'),
        )

    def test_matching_vatin(self):
        for vatin, name in self.VALID_VATINS:
            result_rate = vat.lookup_vat_by_vatin(vatin, name)
            self.assertEqual(result_rate, D('0.00'))

    def test_non_matching_vatin(self):
        for vatin, name in self.INVALID_VATINS:
            with self.assertRaises(vat.NonMatchingVATINException):
                result_rate = vat.lookup_vat_by_vatin(vatin, name)


class PhoneNumberAddressTest(unittest.TestCase):
    VALID_COMBINATIONS = (
        # Austria, regular rate
        ({ 'line4': 'Vienna',
           'country': 'AT',
           'postcode': 1010 },
         "+43 123 456 789",
         D('0.20')),
        # Germany, regular rate
        ({ 'line4': 'Berlin',
           'country': 'DE',
           'postcode': 10001 },
         "+49 123 456 789",
         D('0.19')),
        # Austria, VAT exception (phone area code matches postcode)
        ({'line4': 'Jungholz',
          'country': 'AT',
          'postcode': 6691},
         "+43 5676 123",
         D('0.19')),

    )

    INVALID_COMBINATIONS = (
        # Austrian location, German calling code
        ({ 'line4': 'Vienna',
           'country': 'AT',
           'postcode': 1010 },
         "+49 123 456 789"),
        # German location, Austrian calling code
        ({ 'line4': 'Berlin',
           'country': 'DE',
           'postcode': 10001 },
         "+43 123 456 789"),
        # Austrian location, non-matching area code
        ({'line4': 'Jungholz',
          'country': 'AT',
          'postcode': 6691},
         "+43 1 123 4567"),
    )

    def test_valid_combination(self):
        for addr, num, expected_rate in self.VALID_COMBINATIONS:
            country_code = addr.get('country')
            postcode = addr.get('postcode')
            city = addr.get('line4')

            result_rate = vat.lookup_vat(None,
                                         city,
                                         country_code,
                                         postcode,
                                         num,
                                         None)
            self.assertEqual(result_rate,
                             expected_rate)
        pass

    def test_invalid_combination(self):
        for addr, num in self.INVALID_COMBINATIONS:
            country_code = addr.get('country')
            postcode = addr.get('postcode')
            city = addr.get('line4')

            with self.assertRaises(vat.VATAssessmentException):
                result_rate = vat.lookup_vat(None,
                                             city,
                                             country_code,
                                             postcode,
                                             num,
                                             None)
