from oscar.apps.partner import strategy, prices

class Selector(object):
    def strategy(self, request=None, user=None, **kwargs):
        return VATStrategy(request)

class VATStrategy(strategy.UseFirstStockRecord, strategy.DeferredTax,
                  strategy.StockRequired, strategy.Structured):
    pass
