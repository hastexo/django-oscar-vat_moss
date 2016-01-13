import unittest
from decimal import Decimal as D
from oscar_vat_moss.partner.strategy import *  # noqa

from mock import Mock


class DeferredVATSelectorTest(unittest.TestCase):

    def test_selector(self):
        selector = DeferredVATSelector()
        strategy = selector.strategy()
        self.assertEqual(strategy.__class__,
                         DeferredVATStrategy)
        with self.assertRaises(AttributeError):
            strategy.getRate(None, None)


class PerUserVATSelectorTest(unittest.TestCase):

    def test_selector(self):
        selector = PerUserVATSelector()
        strategy = selector.strategy()
        self.assertEqual(strategy.__class__,
                         PerUserVATStrategy)
        self.assertTrue(hasattr(strategy, 'get_rate'))


class PerUserVATStrategyTest(unittest.TestCase):

    def test_valid_user(self):
        address = Mock()
        address.country = Mock()
        address.country.code = 'AT'
        address.line4 = 'Vienna'
        address.postcode = '1010'
        address.phone_number = '+43 1 234 5678'
        address.line1 = 'hastexo Professional Services GmbH'
        address.vatin = ''

        request = Mock()
        request.user = Mock()
        request.user.addresses = Mock()
        request.user.addresses.order_by = Mock(return_value=[address])
        request.user.is_authenticated = Mock(return_value=True)

        selector = PerUserVATSelector()
        strategy = selector.strategy(request=request)

        result_rate = strategy.get_rate(None, None)
        self.assertEqual(result_rate,
                         D('0.20'))

        address.vatin = 'ATU66688202'
        result_rate = strategy.get_rate(None, None)
        self.assertEqual(result_rate,
                         D('0.00'))
