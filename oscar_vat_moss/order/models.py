from oscar_vat_moss import fields
from oscar.apps.address.abstract_models import AbstractShippingAddress


class ShippingAddress(AbstractShippingAddress):
    vatin = fields.vatin()


from oscar.apps.order.models import *  # noqa
