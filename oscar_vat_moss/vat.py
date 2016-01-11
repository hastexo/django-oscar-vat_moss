from decimal import Decimal as D

import vat_moss.billing_address
import vat_moss.id
import vat_moss.phone_number

from oscar_vat_moss.util import u


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
    # Use getattr here so we can default to None for non-existing fields
    city = getattr(shipping_address, 'line4', None)
    country = getattr(shipping_address, 'country', None)
    postcode = getattr(shipping_address, 'postcode', None)
    phone_number = getattr(shipping_address, 'phone_number', None)
    vatin = getattr(shipping_address, 'vatin', None)

    verifications = 0
    address_vat_rate = None
    phone_vat_rate = None

    # We already validated the VATIN through a form validator;
    # additional errors here shouldn't happen.
    if vatin:
        (vatin_country,
         vatin_normalized,
         vatin_company) = vat_moss.id.validate(u(vatin))

    # TODO: check here whether or not the returned company name
    # matches the billing address.

    # TODO: Set effective tax rate to zero IFF VATIN verifies and the
    # country doesn't match the store's own country.

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

    # TODO: Raise an error if we don't have 2 verifications

    # TODO: Verify here that the calculated rates actually match
    return address_vat_rate or phone_vat_rate


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
