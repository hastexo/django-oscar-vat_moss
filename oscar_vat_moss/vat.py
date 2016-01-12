from decimal import Decimal as D
import re

from django.utils.translation import ugettext_lazy as _

import vat_moss.billing_address
import vat_moss.id
import vat_moss.phone_number

from oscar_vat_moss.util import u

VERIFICATIONS_NEEDED = 2


def apply_to(submission):
    rate = lookup_vat(submission)

    for line in submission['basket'].all_lines():
        line_tax = calculate_tax(
            line.line_price_excl_tax_incl_discounts, rate)
        unit_tax = (line_tax / line.quantity).quantize(D('0.01'))
        line.purchase_info.price.tax = unit_tax

    # Note, we change the submission in place - we don't need to
    # return anything from this function
    shipping_charge = submission['shipping_charge']
    shipping_charge.tax = calculate_tax(
        shipping_charge.excl_tax, rate)


def lookup_vat(submission):
    shipping_address = submission['shipping_address']
    # Use getattr here so we can default to empty string for
    # non-existing fields.
    city = getattr(shipping_address, 'line4', '')
    country = getattr(shipping_address, 'country', '')
    postcode = getattr(shipping_address, 'postcode', '')
    phone_number = getattr(shipping_address, 'phone_number', '')
    vatin = getattr(shipping_address, 'vatin', '')

    verifications = 0
    address_vat_rate = None
    phone_vat_rate = None

    if vatin:
        shipping_company = getattr(shipping_address, 'line1', '')
        rate = lookup_vat_by_vatin(vatin, shipping_company)
        # TODO: Test if we have our own VATIN, and do apply VAT if
        # shipping country is the same as the store's own country.
        return rate

    try:
        if city and country:
            address_vat_rate = lookup_vat_by_address(country.code,
                                                     postcode,
                                                     city)
            verifications += 1
    except:
        # We'll try the next one
        pass

    try:
        if phone_number:
            phone_vat_rate = lookup_vat_by_phone_number(phone_number,
                                                        country.code)
            verifications += 1
    except:
        pass

    if verifications < VERIFICATIONS_NEEDED:
        raise VATAssessmentException()

    if address_vat_rate != phone_vat_rate:
        raise VATAssessmentException()

    return address_vat_rate


def lookup_vat_by_vatin(vatin, company_name):
    # We already validated the VATIN through a form validator;
    # additional validation errors here shouldn't happen.
    (vatin_country,
     vatin_normalized,
     vatin_company) = vat_moss.id.validate(u(vatin))
    # Does the VATIN match the company name we've been given?
    #
    # This is effectively a case-insensitive startswith(), but the
    # regex should really be configurable.
    regex = "^%s" % vatin_company
    if not re.search(regex, company_name, re.I):
        raise NonMatchingVATINException(vatin,
                                        company_name)
    # We have a verified VATIN and it matches the company
    # name. Reverse charge applies.
    #
    return D('0.00')


def lookup_vat_by_address(country_code=None, postcode=None, city=None):
    # exception is a statutory VAT exception,
    # *not* a Python error!
    (rate,
     country,
     exception) = vat_moss.billing_address.calculate_rate(u(country_code),
                                                          u(postcode),
                                                          u(city))
    return rate


def lookup_vat_by_phone_number(phone_number=None, country_code=None):
    # exception is a statutory VAT exception,
    # *not* a Python error!
    (rate,
     country,
     exception) = vat_moss.phone_number.calculate_rate(u(phone_number),
                                                       u(country_code))
    return rate


def calculate_tax(price, rate):
    tax = price * rate
    return tax.quantize(D('0.01'))


class VATAssessmentException(Exception):
    pass


class NonMatchingVATINException(VATAssessmentException):

    def __init__(self, vatin, company_name):
        self.message = _('VATIN %s does not match company name %s' %
                         (vatin, company_name))
        self.vatin = vatin
        self.company_name = company_name

    def __str__(self):
        return self.message
