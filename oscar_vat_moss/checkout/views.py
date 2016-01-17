from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView  # noqa
from django.contrib import messages

from oscar_vat_moss import vat

from . import assert_required_fields_set_correctly

# Make sure OSCAR_REQUIRED_ADDRESS_FIELDS is set correctly for VAT
# assessment
assert_required_fields_set_correctly()


class PaymentDetailsView(CorePaymentDetailsView):

    def build_submission(self, **kwargs):
        submission = super(PaymentDetailsView, self).build_submission(**kwargs)
        try:
            vat.apply_to(submission)
            # Recalculate order total to ensure we have a
            # tax-inclusive total
            submission['order_total'] = self.get_order_totals(
                submission['basket'], submission['shipping_charge'])
        except vat.VATAssessmentException as e:
            message = str(e)
            messages.error(self.request, message)
        return submission
