# -*- coding: utf-8 -*-
from django.test import TestCase

from oscar.core.compat import get_user_model
from oscar.core.loading import get_model

from oscar_vat_moss.address.models import UserAddress
from oscar_vat_moss.partner.models import PartnerAddress
from oscar_vat_moss.order.models import ShippingAddress, BillingAddress

Country = get_model('address', 'country')


class TestUserAddress(TestCase):

    model = UserAddress

    def setUp(self):
        self.johndoe = get_user_model().objects.create_user('johndoe')
        self.uk = Country.objects.create(
            iso_3166_1_a2='GB', name="UNITED KINGDOM")
        self.address = self.model()
        self.address.user = self.johndoe
        self.address.first_name = "John"
        self.address.last_name = "Doe"
        self.address.line1 = "123 No Such Street"
        self.address.line4 = "Brighton"
        self.address.postcode = "BN1 6XX"
        self.address.country = self.uk

    def test_takes_vatin(self):
        # Just check that we can set this. There is no validation
        # here, so the only way this could fail would be if the field
        # weren't available
        self.address.vatin = 'GB99999999'


class TestShippingAddress(TestUserAddress):
    model = ShippingAddress


class TestBillingAddress(TestUserAddress):
    model = BillingAddress


class TestPartnerAddress(TestUserAddress):
    model = PartnerAddress
