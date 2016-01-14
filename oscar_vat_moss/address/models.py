from oscar_vat_moss import fields
from oscar.apps.address.abstract_models import AbstractUserAddress

class UserAddress(AbstractUserAddress):
    vatin = fields.vatin()

from oscar.apps.address.models import *  # noqa
