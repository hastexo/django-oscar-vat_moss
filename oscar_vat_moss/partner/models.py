from oscar.apps.address.abstract_models import AbstractPartnerAddress

from oscar_vat_moss import fields


class PartnerAddress(AbstractPartnerAddress):

    vatin = fields.vatin()


from oscar.apps.partner.models import * #noqa
