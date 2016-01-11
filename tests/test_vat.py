import unittest
from decimal import Decimal as D
from oscar_vat_moss import vat


class AddressTest(unittest.TestCase):
    ADDRESSES = (
        # Submission dictionary      # Expected rate
        ({'line4': 'Vienna',
          'country': 'AT',
          'postcode': 1010},         D('0.20')),
        ({'line4': 'Berlin',
          'country': 'DE',
          'postcode': 10001},        D('0.19')),
        ({'line4': 'Jungholz',
          'country': 'AT',
          'postcode': 6691},         D('0.19')),
        ({'line4': 'Galway',
          'country': 'IE',
         },                          D('0.23')),
    )

    def test_vat_lookup_rate_by_address(self):
        for submission, expected_rate in self.ADDRESSES:
            result_rate = vat.lookup_vat(submission)
            self.assertEqual(result_rate,
                             expected_rate,
                             msg="Unexpected VAT rate returned for %s: %s" % (submission, result_rate))


class PhoneNumberTest(unittest.TestCase):
    PHONE_NUMBERS = (
        # Submission dictionary              # Expected rate
        ({'phone_number': '+43 1 234 5678',
         },                                  D('0.20')),
        ({'phone_number': '+49 170 12345',
         },                                  D('0.19')),
    )

    def test_vat_lookup_rate_by_phone(self):
        for submission, expected_rate in self.PHONE_NUMBERS:
            result_rate = vat.lookup_vat(submission)
            self.assertEqual(result_rate,
                             expected_rate,
                             msg="Unexpected VAT rate returned for %s: %s" % (submission, result_rate))
