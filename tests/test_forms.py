# coding=utf-8
from __future__ import print_function, unicode_literals

from django.test import TestCase
from oscar.core.compat import get_user_model
from oscar_vat_moss.address.forms import UserAddressForm
from oscar_vat_moss.dashboard.catalogue.forms import ProductClassForm
from oscar_vat_moss.address.models import Country

User = get_user_model()


class UserAddressFormTest(TestCase):

    def setUp(self):
        self.johndoe = get_user_model().objects.create_user('johndoe')
        self.hansmueller = get_user_model().objects.create_user('hansmueller')
        self.uk = Country.objects.create(
            iso_3166_1_a2='GB', name="UNITED KINGDOM")
        self.at = Country.objects.create(
            iso_3166_1_a2='AT', name="AUSTRIA")
        self.de = Country.objects.create(
            iso_3166_1_a2='DE', name="GERMANY")

    def test_empty_address(self):
        data = dict(user=self.johndoe)
        form = UserAddressForm(self.johndoe,
                               data)
        self.assertFalse(form.is_valid())

    def test_valid_address(self):
        # Is a valid address identified correctly?
        data = dict(
            user=self.johndoe,
            first_name="John",
            last_name="Doe",
            line1="123 No Such Street",
            line4="Brighton",
            postcode="BN1 6XX",
            country=self.uk.iso_3166_1_a2,
            phone_number='+44 1273 555 999',
        )
        form = UserAddressForm(self.johndoe,
                               data)
        self.assertTrue(form.is_valid())

    def test_missing_phone_number(self):
        # Is a valid address identified correctly?
        data = dict(
            user=self.johndoe,
            first_name="John",
            last_name="Doe",
            line1="123 No Such Street",
            line4="Brighton",
            postcode="BN1 6XX",
            country=self.uk.iso_3166_1_a2,
        )
        form = UserAddressForm(self.johndoe,
                               data)
        self.assertFalse(form.is_valid())

    def test_valid_vatin(self):
        # Is a valid VATIN identified correctly?
        data = dict(
            user=self.hansmueller,
            first_name="Hans",
            last_name="Müller",
            line1="hastexo Professional Services GmbH",
            line4="Wien",
            postcode="1010",
            country=self.at.iso_3166_1_a2,
            vatin='ATU66688202',
            phone_number='+43 1 555 9999',
        )
        form = UserAddressForm(self.hansmueller,
                               data)
        self.assertTrue(form.is_valid())

    def test_invalid_vatin(self):
        # Is an invalid VATIN identified correctly?
        data = dict(
            user=self.hansmueller,
            first_name="Hans",
            last_name="Müller",
            line1="hastexo Professional Services GmbH",
            line4="Wien",
            postcode="1010",
            country=self.at.iso_3166_1_a2,
            vatin='ATU99999999',
        )
        form = UserAddressForm(self.hansmueller,
                               data)
        self.assertFalse(form.is_valid())

    def test_vatin_wrong_country(self):
        # Is an invalid VATIN identified correctly?
        data = dict(
            user=self.hansmueller,
            first_name="Hans",
            last_name="Müller",
            line1="hastexo Professional Services GmbH",
            line4="Wien",
            postcode="1010",
            country=self.uk.iso_3166_1_a2,
            vatin='ATU66688202',
        )
        form = UserAddressForm(self.hansmueller,
                               data)
        self.assertFalse(form.is_valid())

    def test_non_matching_vatin(self):
        # Is a VATIN that is correct, but doesn't match the company
        # name, identified correctly?
        data = dict(
            user=self.hansmueller,
            first_name="Hans",
            last_name="Müller",
            line1="Example, Inc.",
            line4="Wien",
            postcode="1010",
            country=self.at.iso_3166_1_a2,
            vatin='ATU66688202',
        )
        form = UserAddressForm(self.hansmueller,
                               data)
        self.assertFalse(form.is_valid())

    def test_non_matching_country_and_phone_number(self):
        # Is an invalid combination of country and phone number
        # identified correctly?
        data = dict(
            user=self.hansmueller,
            first_name="Hans",
            last_name="Müller",
            line1="Example, Inc.",
            line4="Wien",
            postcode="1010",
            phone_number="+49 30 1234567",
            country=self.at.iso_3166_1_a2,
        )
        form = UserAddressForm(self.hansmueller,
                               data)
        self.assertFalse(form.is_valid())

    def test_non_matching_address_and_phone_number(self):
        # Is an invalid combination of postcode and phone area code,
        # where this information would be relevant for a VAT
        # exception, identified correctly?
        data = dict(
            user=self.hansmueller,
            first_name="Hans",
            last_name="Müller",
            line1="Example, Inc.",
            # Jungholz is a VAT exception area where German, not
            # Austrian, VAT rates apply
            line4="Jungholz",
            # Correct postcode for Jungholz
            postcode="6691",
            # Incorrect area code (valid number, but uses Graz area
            # code)
            phone_number="+43 316 1234567",
            country=self.at.iso_3166_1_a2,
        )
        form = UserAddressForm(self.hansmueller,
                               data)
        self.assertFalse(form.is_valid())


class ProductClassFormTest(TestCase):

    def test_empty_form(self):
        data = {}
        form = ProductClassForm(data)
        self.assertFalse(form.is_valid())

    def test_valid_if_digital_goods_false(self):
        data = { 'name': 'something',
                 'requires_shipping': False,
                 'digital_goods': False,
                 'track_stock': False }
        form = ProductClassForm(data)
        self.assertTrue(form.is_valid())

    def test_valid_if_digital_goods_true_and_requires_shipping_true(self):
        data = { 'name': 'something',
                 'requires_shipping': True,
                 'digital_goods': True,
                 'track_stock': False }
        form = ProductClassForm(data)
        self.assertTrue(form.is_valid())

    def test_valid_if_digital_goods_false_and_requires_shipping_true(self):
        data = { 'name': 'something',
                 'requires_shipping': True,
                 'digital_goods': False,
                 'track_stock': False }
        form = ProductClassForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_if_digital_goods_true_and_requires_shipping_false(self):
        data = { 'name': 'something',
                 'requires_shipping': False,
                 'digital_goods': True,
                 'track_stock': False }
        form = ProductClassForm(data)
        self.assertFalse(form.is_valid())
