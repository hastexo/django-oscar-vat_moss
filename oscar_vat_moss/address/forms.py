from oscar.apps.address.forms import UserAddressForm as CoreUserAddressForm
from django.utils.translation import ugettext_lazy as _
from oscar_vat_moss import vat


class UserAddressForm(CoreUserAddressForm):

    class Meta(CoreUserAddressForm.Meta):
        fields = CoreUserAddressForm.Meta.fields + ['vatin']

    def clean(self):
        """Perform necessary form verification."""
        data = super(UserAddressForm, self).clean()
        # The superclass has taken care of individual field
        # verification, applying field validators to the form
        # input. Now we need to compare fields to each other.

        # Grab the interesting fields from the form
        company = data.get('line1')
        city = data.get('line4')
        country = data.get('country')
        if country:
            country_code = data.get('country').code
        else:
            country_code = ''
        postcode = data.get('postcode')
        phone_number = data.get('phone_number')
        vatin = data.get('vatin')

        address_vat_rate = None
        phone_vat_rate = None

        # Do we have a VATIN? If so, the field validator will have
        # checked whether it is valid. Now we need to check whether it
        # agrees with the company name.
        if vatin:
            try:
                vat.lookup_vat_by_vatin(country_code, vatin, company)
            except vat.NonMatchingVATINException as n:
                self.add_error('line1', str(n))
                self.add_error('vatin', str(n))
            except vat.CountryInvalidForVATINException as c:
                self.add_error('country', str(c))
                self.add_error('vatin', str(c))
            except vat.VATINCountrySameAsStoreException:
                # The VATIN is valid, though we still have to charge
                # VAT as the VATIN is from the same country as the
                # store.
                #
                # TODO: It would be great if we could flag this to the
                # user via the messages framework.
                pass
            except Exception as e:
                self.add_error('vatin', str(e))

        # Get the tax rate for the city/country/postcode combination
        if city and country_code:
            try:
                address_vat_rate = vat.lookup_vat_by_city(country_code,
                                                          postcode,
                                                          city)
            except Exception as e:  # pragma: no cover
                # We don't hit this exception because of an invalid
                # postcode: that would already have been caught
                # by the field validator. Neither the superclass form
                # validator nor the tax lookup can determine whether
                # the postcode matches the city, either. So the only
                # reason why we'd get here is because VAT lookup
                # failed, presumably because the web service was
                # temporarily unavailable.
                message = _("Unable to determine the "
                            "applicable VAT rate for "
                            "your address: %s" % str(e))
                # Flag all possibly faulty fields with the same
                # message
                self.add_error('line4', message)
                self.add_error('country', message)
                self.add_error('postcode', message)

        # Get the tax rate for the phone number
        if phone_number:
            try:
                phone_vat_rate = vat.lookup_vat_by_phone_number(phone_number,
                                                                country_code)
            except Exception as e:  # pragma: no cover
                # We don't hit this exception because of an invalid
                # phone number: that would already have been caught by
                # the field validator. The only reason why we'd get
                # here is because VAT lookup failed, presumably
                # because the web service was temporarily unavailable.
                message = _("Unable to determine the "
                            "applicable VAT rate for "
                            "your phone number: %s" % str(e))
                # Flag all possibly faulty fields with the same
                # message
                self.add_error('country', message)
                self.add_error('phone_number', message)

        # Is one of the two rates still None? We can return now; no
        # need to check whether they agree (and confuse the user with
        # duplicate error messages)
        if None in [address_vat_rate, phone_vat_rate]:
            return

        # Does the address tax rate agree with the phone tax rate?
        if address_vat_rate != phone_vat_rate:
            message = _("Unable to determine the applicable VAT rate "
                        "based on address and phone information")
            self.add_error('line4', message)
            self.add_error('country', message)
            self.add_error('postcode', message)
            self.add_error('phone_number', message)
