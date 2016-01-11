from decimal import Decimal as D

import vat_moss.billing_address
import vat_moss.id
import vat_moss.phone_number


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
    # Use dict.get here so we default to None for non-existing fields
    city = submission.get('line4')
    country = submission.get('country')
    postcode = submission.get('postcode')
    phone_number = submission.get('phone_number')
    vatin = submission.get('vatin')

    verifications = 0
    address_vat_rate = None
    phone_vat_rate = None

    # We already validated the VATIN through a form validator;
    # additional errors here shouldn't happen.
    if vatin:
        (vatin_country,
         vatin_normalized,
         vatin_company) = vat_moss.id.validate(unicode(vatin))

    # TODO: check here whether or not the returned company name
    # matches the billing address.

    # TODO: Set effective tax rate to zero IFF VATIN verifies and the
    # country doesn't match the store's own country.

    try:
        if city and country:
            address_vat_rate = lookup_vat_by_address(country,
                                                     postcode,
                                                     city)
            verifications += 1
    except:
        # We'll try the next one
        pass

    try:
        if phone_number:
            phone_vat_rate = lookup_vat_by_phone_number(phone_number,
                                                        country)
            verifications += 1
    except:
        pass

    # TODO: Raise an error if we don't have 2 verifications

    # TODO: Verify here that the calculated rates actually match
    return address_vat_rate or phone_vat_rate


def lookup_vat_by_address(country=None, postcode=None, city=None):
    # exception is a statutory VAT exception,
    # *not* a Python error!
    (rate,
     country,
     exception) = vat_moss.billing_address.calculate_rate(to_unicode(country),
                                                          to_unicode(postcode),
                                                          to_unicode(city))
    return rate


def lookup_vat_by_phone_number(phone_number=None, country=None):
    # exception is a statutory VAT exception,
    # *not* a Python error!
    (rate,
     country,
     exception) = vat_moss.phone_number.calculate_rate(to_unicode(phone_number),
                                                       to_unicode(country))
    return rate


def calculate_tax(price, rate):
    tax = price * rate
    return tax.quantize(D('0.01'))


def to_unicode(s):
    # vat_moss wants all strings in Unicode, or None if a string isn't
    # included in the submission
    return None if s is None else unicode(s)
