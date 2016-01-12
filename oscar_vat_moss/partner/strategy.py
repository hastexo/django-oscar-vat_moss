from django.conf import settings

from oscar.apps.partner import strategy

from oscar_vat_moss import vat

from decimal import Decimal as D
import logging


class DeferredVATSelector(object):
    """Selector that returns the DeferredVATStrategy.

    To use this selector directly:
    from oscar_vat_moss.apps.partner import DeferredVATSelector as Selector"""

    def strategy(self, request=None, user=None, **kwargs):
        return DeferredVATStrategy(request)


class PerUserVATSelector(object):
    """Selector that returns the PerUserVATStrategy.

    To use this selector directly:
    from oscar_vat_moss.apps.partner import PerUserVATSelector as Selector"""

    def strategy(self, request=None, user=None, **kwargs):
        return PerUserVATStrategy(request)


class DeferredVATStrategy(strategy.UseFirstStockRecord, strategy.DeferredTax,
                          strategy.StockRequired, strategy.Structured):
    """Strategy that defers tax assessment until checkout.

    With this strategy, your users always see a tax-free amount and
    taxes are added to their invoice on checkout.

    Requires that a CheckoutSessionMixin be added to your checkout
    app, which then applies taxes once the user has given their
    shipping address.
    """
    pass


class PerUserVATStrategy(strategy.UseFirstStockRecord, strategy.FixedRateTax,
                         strategy.StockRequired, strategy.Structured):
    """Strategy that applies a "fixed" VAT rate to your products.

    With this strategy, your users always see tax-included amounts for
    your home territory. After they register and give an address, they
    switch to their locally applicable tax rate."""

    def get_rate(self, product, stockrecord):
        """Fetches a tax rate, given a product and stockrecord"""

        # The strategy.Base superclass sets self.user only if the user
        # is authenticated
        try:
            return vat.lookup_vat_for_user(self.user)
        except:
            # Unable to look up user address or VAT rate, use defaults
            pass

        # We haven't been able to lookup a VAT rate for the user, use
        # store defaults instead. If all fails, revert to a tax rate of 0.
        try:
            return vat.lookup_vat_by_city(
                settings.VAT_MOSS_STORE_COUNTRY_CODE,
                settings.VAT_MOSS_STORE_POSTCODE,
                settings.VAT_MOSS_STORE_CITY)
        except NameError:
            logging.warn('Unable to set default VAT rate for store, '
                         'defaulting to 0.')
            return D('0.00')
