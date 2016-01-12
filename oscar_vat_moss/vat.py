from decimal import Decimal as D
import re

import vat_moss.billing_address
import vat_moss.id
import vat_moss.phone_number
from vat_moss.errors import URLError
from vat_moss.errors import InvalidError, UndefinitiveError
from vat_moss.errors import WebServiceError, WebServiceUnavailableError

from oscar_vat_moss.util import u

VERIFICATIONS_NEEDED = 2


def apply_to(submission):
    rate = lookup_vat_for_submission(submission)

    for line in submission['basket'].all_lines():
        line_tax = calculate_tax(
            line.line_price_excl_tax_incl_discounts, rate)
        unit_tax = (line_tax / line.quantity).quantize(D('0.01'))
        line.purchase_info.price.tax = unit_tax

    # Note, we change the submission in place - we don't need to
    # return anything from this function
    shipping_charge = submission['shipping_charge']
    shipping_charge.tax = calculate_tax(shipping_charge.excl_tax,
                                        rate)


def lookup_vat_for_submission(submission):
    shipping_address = submission['shipping_address']
    return lookup_vat_for_address(shipping_address)


def lookup_vat_for_user(user):
    # If we have an address that is marked as the default
    # shipping address, we'll use that. Otherwise,
    # randomly use the first address.
    tax_address = user.addresses.order_by('-is_default_for_shipping')[0]
    return lookup_vat_for_address(tax_address)


def lookup_vat_for_address(address):
    # Use getattr here so we can default to empty string for
    # non-existing fields.
    company = getattr(address, 'line1', '')
    city = getattr(address, 'line4', '')
    country = getattr(address, 'country', '')
    postcode = getattr(address, 'postcode', '')
    phone_number = getattr(address, 'phone_number', '')
    vatin = getattr(address, 'vatin', '')

    try:
        return lookup_vat(company,
                          city,
                          country.code,
                          postcode,
                          phone_number,
                          vatin)
    except (URLError, WebServiceError, WebServiceUnavailableError):
        message = "Temporary error in VAT assessment"
        raise VATAssessmentUnavailableException(message)


def lookup_vat(company, city, country_code, postcode, phone_number, vatin):
    verifications = 0
    address_vat_rate = None
    phone_vat_rate = None

    if vatin:
        try:
            rate = lookup_vat_by_vatin(vatin, company)
            # TODO: Test if we have our own VATIN, and do apply VAT if
            # shipping country is the same as the store's own country.
            return rate
        except InvalidError:
            message = "Invalid VAT Identification Number (VATIN)"
            raise VATAssessmentException(message)

    if city and country_code:
        try:
            address_vat_rate = lookup_vat_by_city(country_code,
                                                  postcode,
                                                  city)
            verifications += 1
        except UndefinitiveError:
            # We'll try the next one
            pass

    if phone_number:
        try:
            phone_vat_rate = lookup_vat_by_phone_number(phone_number,
                                                        country_code)
            verifications += 1
        except UndefinitiveError:
            pass

    if verifications < VERIFICATIONS_NEEDED:
        message = "Insufficent information for VAT assessment"
        raise VATAssessmentException(message)

    if address_vat_rate != phone_vat_rate:
        message = "Unable to work out applicable VAT rate " \
                  "based on address and phone information"
        raise VATAssessmentException(message)

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


def lookup_vat_by_city(country_code=None, postcode=None, city=None):
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


class VATAssessmentUnavailableException(VATAssessmentException):
    pass


class NonMatchingVATINException(VATAssessmentException):

    def __init__(self, vatin, company_name):
        self.message = 'VATIN %s does not match company name %s' % \
                       (vatin, company_name)
        self.vatin = vatin
        self.company_name = company_name
