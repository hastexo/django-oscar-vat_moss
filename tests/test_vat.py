from django.test import TestCase
from django.test.utils import override_settings
from decimal import Decimal as D
from oscar_vat_moss import vat

from mock import Mock

class AddressTest(TestCase):
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


class PhoneNumberTest(TestCase):
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

class VATINTest(TestCase):
    VALID_VATINS = (
        # Country code  # VATIN        # Company name
        ('AT',          'ATU66688202', 'hastexo Professional Services GmbH'),
        ('AT',          'ATU66688202', 'HASTEXO PROFESSIONAL SERVICES GMBH'),
        ('AT',          'ATU66688202', 'hastexo Professional Services GmbH (Procurement Department)'),
        )
    INVALID_VATINS = (
        # Country code  # VATIN        # Company name
        ('AT',          'ATU66688202', 'Example, Inc.'),
        ('AT',          'ATU66688202', 'hastexo'),
        ('DE',          'ATU66688202', 'hastexo Professional Services GmbH'),
        )

    @override_settings(VAT_MOSS_STORE_COUNTRY_CODE='DE')
    def test_matching_vatin_reverse_charge(self):
        # We'll pretend we're a store in Germany here, so we can do
        # reverse-charge to Austria
        for country_code, vatin, name in self.VALID_VATINS:
            result_rate = vat.lookup_vat_by_vatin(country_code, vatin, name)
            self.assertEqual(result_rate, D('0.00'))

    @override_settings(VAT_MOSS_STORE_COUNTRY_CODE='AT')
    def test_matching_vatin_no_reverse_charge(self):
        # If however we're in Austria, then we do need to charge VAT
        # regardless of a valid VATIN, and we can't get a VAT rate
        # from the VATIN alone.
        for country_code, vatin, name in self.VALID_VATINS:
            with self.assertRaises(vat.VATINCountrySameAsStoreException):
                result_rate = vat.lookup_vat_by_vatin(country_code, vatin, name)

    def test_non_matching_vatin(self):
        for country_code, vatin, name in self.INVALID_VATINS:
            with self.assertRaises(vat.VATAssessmentException):
                result_rate = vat.lookup_vat_by_vatin(country_code, vatin, name)


class PhoneNumberAddressTest(TestCase):
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

class UserTest(TestCase):

    @override_settings(VAT_MOSS_STORE_COUNTRY_CODE='AT')
    def test_valid_user_no_reverse_charge(self):
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = ''
        user = Mock()
        user.addresses = Mock()
        user.addresses.order_by = Mock(return_value=[address])

        # No VATIN? Standard rate applies.
        result_rate = vat.lookup_vat_for_user(user)
        self.assertEqual(result_rate,
                         D('0.20'))

        # Do they have a VATIN? Doesn't matter if they're in the same
        # country as the store; VAT still applies.
        address.vatin = 'ATU66688202'
        result_rate = vat.lookup_vat_for_user(user)
        self.assertEqual(result_rate,
                         D('0.20'))

    @override_settings(VAT_MOSS_STORE_COUNTRY_CODE='DE')
    def test_valid_user_reverse_charge(self):
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = ''
        user = Mock()
        user.addresses = Mock()
        user.addresses.order_by = Mock(return_value=[address])

        # No VATIN, different country? Standard rate applies.
        result_rate = vat.lookup_vat_for_user(user)
        self.assertEqual(result_rate,
                         D('0.20'))

        # Valid VATIN, different country? Reverse charge applies.
        address.vatin = 'ATU66688202'
        result_rate = vat.lookup_vat_for_user(user)
        self.assertEqual(result_rate,
                           D('0.00'))


    def test_invalid_user(self):
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+49 911 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = ''
        user = Mock()
        user.addresses = Mock()
        user.addresses.order_by = Mock(return_value=[address])

        with self.assertRaises(vat.VATAssessmentException):
            result_rate = vat.lookup_vat_for_user(user)

        address.vatin = 'ATU66688999'
        with self.assertRaises(vat.VATAssessmentException):
            result_rate = vat.lookup_vat_for_user(user)


class SubmissionTest(TestCase):

    @override_settings(VAT_MOSS_STORE_COUNTRY_CODE='AT')
    def test_valid_submission_no_reverse_charge(self):
        basket = Mock()
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = ''

        submission = { 'basket': basket,
                       'shipping_address': address }

        result_rate = vat.lookup_vat_for_submission(submission)
        self.assertEqual(result_rate,
                         D('0.20'))

        # Do they have a VATIN? Doesn't matter if they're in the same
        # country as the store; VAT still applies.
        address.vatin = 'ATU66688202'
        result_rate = vat.lookup_vat_for_submission(submission)
        self.assertEqual(result_rate,
                         D('0.20'))

    @override_settings(VAT_MOSS_STORE_COUNTRY_CODE='DE')
    def test_valid_submission_reverse_charge(self):
        basket = Mock()
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = ''

        submission = { 'basket': basket,
                       'shipping_address': address }

        result_rate = vat.lookup_vat_for_submission(submission)
        self.assertEqual(result_rate,
                         D('0.20'))

        # We're pretending we're a store in Germany. Then we can do
        # reverse charge.
        address.vatin = 'ATU66688202'
        result_rate = vat.lookup_vat_for_submission(submission)
        self.assertEqual(result_rate,
                         D('0.00'))
        # However, if we're using an empty VATIN, the regular VAT
        # rate applies again.
        address.vatin = ''
        address.line1 = 'HASTEXO PROFESSIONAL SERVICES GMBH'
        result_rate = vat.lookup_vat_for_submission(submission)
        self.assertEqual(result_rate,
                         D('0.20'))


    def test_invalid_submission(self):
        basket = Mock()
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = 'ATU66688999'

        submission = { 'basket': basket,
                       'shipping_address': address }

        expected_rate = D('0.20')

        with self.assertRaises(vat.VATAssessmentException):
            result_rate = vat.lookup_vat_for_submission(submission)

        address.vatin = 'ATU66688202'
        address.line1 = 'hastexo'
        with self.assertRaises(vat.VATAssessmentException):
            result_rate = vat.lookup_vat_for_submission(submission)

        address.vatin = ''
        address.line1 = 'hastexo Professional Services GmbH'
        address.phone_number = '+49 9 999 9999'
        with self.assertRaises(vat.VATAssessmentException):
            result_rate = vat.lookup_vat_for_submission(submission)


class ApplyTest(TestCase):

    def test_basket_with_tax(self):
        basket = Mock()
        line = Mock()
        line.line_price_excl_tax_incl_discounts = D('100.00')
        line.purchase_info = Mock()
        line.purchase_info.price = Mock()
        line.quantity = 1
        basket.all_lines = Mock(return_value=[line])
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.vatin = ''
        shipping_charge = Mock()
        shipping_charge.excl_tax = D('10.00')

        submission = { 'basket': basket,
                       'shipping_address': address,
                       'shipping_charge': shipping_charge }

        vat.apply_to(submission)
        self.assertEqual(shipping_charge.tax, D('2.00'))
        self.assertEqual(line.purchase_info.price.tax, D('20.00'))

    @override_settings(VAT_MOSS_STORE_COUNTRY_CODE='AT')
    def test_basket_with_vatin_no_reverse_charge(self):
        basket = Mock()
        line = Mock()
        line.line_price_excl_tax_incl_discounts = D('100.00')
        line.purchase_info = Mock()
        line.purchase_info.price = Mock()
        line.quantity = 1
        basket.all_lines = Mock(return_value=[line])
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = 'ATU66688202'
        shipping_charge = Mock()
        shipping_charge.excl_tax = D('10.00')

        submission = { 'basket': basket,
                       'shipping_address': address,
                       'shipping_charge': shipping_charge }

        # Even if they've given us a VATIN, if they're in the same
        # country as the store, VAT still applies.
        vat.apply_to(submission)
        self.assertEqual(shipping_charge.tax, D('2.00'))
        self.assertEqual(line.purchase_info.price.tax, D('20.00'))

    @override_settings(VAT_MOSS_STORE_COUNTRY_CODE='DE')
    def test_basket_with_vatin_reverse_charge(self):
        basket = Mock()
        line = Mock()
        line.line_price_excl_tax_incl_discounts = D('100.00')
        line.purchase_info = Mock()
        line.purchase_info.price = Mock()
        line.quantity = 1
        basket.all_lines = Mock(return_value=[line])
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = 'ATU66688202'
        shipping_charge = Mock()
        shipping_charge.excl_tax = D('10.00')

        submission = { 'basket': basket,
                       'shipping_address': address,
                       'shipping_charge': shipping_charge }

        # We're pretending we're a store in Germany. Then we can do
        # reverse charge.
        vat.apply_to(submission)
        self.assertEqual(shipping_charge.tax, D('0.00'))
        self.assertEqual(line.purchase_info.price.tax, D('0.00'))
