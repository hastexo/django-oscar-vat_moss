from oscar_vat_moss import fields
from oscar.apps.address.abstract_models import AbstractShippingAddress
from oscar.apps.address.abstract_models import AbstractBillingAddress


class ShippingAddress(AbstractShippingAddress):
    vatin = fields.vatin()


class BillingAddress(AbstractBillingAddress):
    vatin = fields.vatin()


from oscar.apps.order.models import *  # noqa
