from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from oscar.apps.checkout import session, exceptions
from oscar_vat_moss import vat


class CheckoutSessionMixin(session.CheckoutSessionMixin):

    def build_submission(self, **kwargs):
        submission = super(CheckoutSessionMixin, self).build_submission(
            **kwargs)

        assess_tax = (submission['shipping_method']
                      and submission['shipping_address']
                      and submission['shipping_address'].phone_number)
        if assess_tax:
            try:
                vat.apply_to(submission)
                # Recalculate order total to ensure we have a
                # tax-inclusive total
                submission['order_total'] = self.get_order_totals(
                    submission['basket'], submission['shipping_charge'])
            except vat.VATAssessmentException:
                pass
        return submission

    def check_a_valid_shipping_address_is_captured(self):
        super(CheckoutSessionMixin, self)
        shipping_address = self.get_shipping_address(
            basket=self.request.basket)
        try:
            vat.lookup_vat_for_shipping_address(shipping_address)
        except vat.VATAssessmentException as e:
            message = _("%s. Please try again." % str(e))
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:shipping-address'),
                message=message
            )

    def get_context_data(self, **kwargs):
        ctx = super(CheckoutSessionMixin, self).get_context_data(**kwargs)

        # Oscar's checkout templates look for this variable which specifies to
        # break out the tax totals into a separate subtotal.
        ctx['show_tax_separately'] = True

        return ctx
