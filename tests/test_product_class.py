# -*- coding: utf-8 -*-
from django.test import TestCase

from oscar.core.compat import get_user_model
from oscar.core.loading import get_model

from oscar_vat_moss.catalogue.models import ProductClass

Country = get_model('address', 'country')


class TestProductClass(TestCase):

    model = ProductClass

    def setUp(self):
        self.product_class = self.model()
        self.product_class.name = 'Something'
        self.product_class.track_stock = True
        self.product_class.requires_shipping = True

    def test_digital_goods_default_none(self):
        self.assertIsNone(self.product_class.digital_goods)

    def test_digital_goods_default_treated_as_false(self):
        self.assertFalse(self.product_class.digital_goods)

    def test_can_set_digital_goods(self):
        # Just check that we can set this. There is no validation
        # here, so the only way this could fail would be if the field
        # weren't available
        self.product_class.digital_goods = True
        self.assertTrue(self.product_class.digital_goods)

