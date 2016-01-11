from oscar.apps.address import models
from django.utils.translation import ugettext_lazy as _

from . import fields


class AbstractShippingAddress(models.AbstractShippingAddress):
    vatin = fields.VATINField(
        _('VAT Identification Number (VATIN)'),
        blank=True,
        help_text=_('Required if you are associated with a business '
                    'registered for VAT in the European Union.'))
