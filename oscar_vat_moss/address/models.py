from oscar.apps.address.abstract_models import AbstractUserAddress
from oscar_vat_moss import fields


class VATINUserAddress(AbstractUserAddress):

    vatin = fields.vatin()
