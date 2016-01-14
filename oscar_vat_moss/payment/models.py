from oscar_vat_moss import fields
from oscar.apps.address.abstract_models import AbstractBillingAddress

class BillingAddress(AbstractBillingAddress):
    vatin = fields.vatin()

from oscar.apps.payment.models import *  # noqa
