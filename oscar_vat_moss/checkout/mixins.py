from oscar.apps.checkout import session
from oscar_vat_moss import vat


class VATCheckoutSessionMixin(session.CheckoutSessionMixin):

    def get_context_data(self, **kwargs):
        ctx = super(VATCheckoutSessionMixin,
                    self).get_context_data(**kwargs)

        # Oscar's checkout templates look for this variable which specifies to
        # break out the tax totals into a separate subtotal.
        ctx['show_tax_separately'] = True

        return ctx

    def check_a_valid_shipping_address_is_captured(self):
        """Check that the just-captured shipping address is valid.

        There is one thing that we can't do through a normal field
        validator, and that is to check multiple form fields against
        one another. We have to that for VAT: check whether the phone
        country code matches the country, whether the phone area code
        matches the postcode (in case of a user living in a VAT
        exception territory), and whether or not any VATIN that the
        user entered matches the registered company name. So, we do
        that here.

        """
        super(VATCheckoutSessionMixin, self)
        shipping_address = self.get_shipping_address(
            basket=self.request.basket)
        try:
            vat.lookup_vat_for_address(shipping_address)
        except vat.VATAssessmentException as e:
            message = _("%s. Please try again." % str(e))
            raise exceptions.FailedPreCondition(
                url=reverse('checkout:shipping-address'),
                message=message
            )


class FixedRateVATCheckoutSessionMixin(VATCheckoutSessionMixin):

    def check_a_valid_shipping_address_is_captured(self):
        """Check that the just-captured shipping address is valid.

        Normally, this method is only used to perform a general
        shipping address check. With the FixedRateVATStrategy however,
        we rely on the default shipping address to figure out a user's
        applicable VAT rate. Therefore, when we are satisfied that the
        shipping address is valid, we also set it as the default for
        shipping. This will cause a minor nuisance for any user who
        doesn't expect that the default shipping address is simply the
        one used most recently, but in this case, the benefits
        outweigh the disadvantages.

        """
        # The superclass does the VAT validation check. Once that has
        # completed, we can set the shipping address to be the new
        # default.
        super(FixedRateVATCheckoutSessionMixin, self)

        shipping_address = self.get_shipping_address(
            basket=self.request.basket)
        shipping_address.is_default_for_shipping = True
        shipping_address.save()


class DeferredVATCheckoutSessionMixin(VATCheckoutSessionMixin):

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


# FixedRateVATCheckoutSessionMixin is the safer option,
# make that the default
CheckoutSessionMixin = FixedRateVATCheckoutSessionMixin
