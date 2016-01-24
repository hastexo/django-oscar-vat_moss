from oscar_vat_moss import fields
from oscar.apps.catalogue.abstract_models import AbstractProductClass


class ProductClass(AbstractProductClass):
    digital_goods = fields.digital_goods()

from oscar.apps.catalogue.models import *  # noqa
