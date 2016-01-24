from oscar.apps.checkout import session
from oscar_vat_moss import vat

from . import assert_required_fields_set_correctly

# Make sure OSCAR_REQUIRED_ADDRESS_FIELDS is set correctly for VAT
# assessment
assert_required_fields_set_correctly()


class DeferredVATCheckoutSessionMixin(session.CheckoutSessionMixin):

    def get_context_data(self, **kwargs):
        ctx = super(DeferredVATCheckoutSessionMixin,
                    self).get_context_data(**kwargs)

        # Oscar's checkout templates look for this variable which specifies to
        # break out the tax totals into a separate subtotal.
        ctx['show_tax_separately'] = True

        return ctx

    def build_submission(self, **kwargs):
        submission = super(DeferredVATCheckoutSessionMixin,
                           self).build_submission(**kwargs)

        assess_tax = (submission['shipping_method'] and
                      submission['shipping_address'] and
                      submission['shipping_address'].phone_number)
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
