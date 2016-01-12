from oscar.apps.partner import strategy


class Selector(object):
    def strategy(self, request=None, user=None, **kwargs):
        return DeferredVATStrategy(request)


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
