from oscar.apps.dashboard.catalogue.forms import ProductClassForm as CoreProductClassForm  # noqa
from django.utils.translation import ugettext_lazy as _


class ProductClassForm(CoreProductClassForm):

    class Meta(CoreProductClassForm.Meta):
        fields = CoreProductClassForm.Meta.fields + ['digital_goods']

    def clean(self):
        """Perform necessary form verification."""
        data = super(ProductClassForm, self).clean()
        # The superclass has taken care of individual field
        # verification, applying field validators to the form
        # input. Now we need to compare fields to each other.

        # Grab the interesting fields from the form
        requires_shipping = data.get('requires_shipping')
        digital_goods = data.get('digital_goods')

        # Oscar does enforce shipping addresses by default, whereas
        # billing addresses are normally not used. Since we rely on
        # user's addresses to calculate VAT on digital goods, just
        # force that digital goods must always require "shipping",
        # even though that might seem self-contradictory.
        if digital_goods and not requires_shipping:
            message = _("Digital goods must require shipping, "
                        "because tax assessment is dependent "
                        "on the consumer's (not the seller's) "
                        "location.")
            self.add_error('requires_shipping', message)
            self.add_error('digital_goods', message)
