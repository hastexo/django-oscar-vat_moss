# EU VATMOSS support for the Oscar e-commerce framework

[VAT (Value Added Tax)](https://en.wikipedia.org/wiki/European_Union_value_added_tax)
is a tax typically collected on goods and services in the European
Union. Its rate varies by country, and there are
[numerous exceptions and special considerations](http://ec.europa.eu/taxation_customs/taxation/vat/how_vat_works/vat_on_services/index_en.htm)
related to its applicability and assessment.

Assessing VAT can be a tricky business, specifically if your store
sells digital goods. Since January 1, 2015, any business *selling* to
EU customers in business-to-consumer (B2C) transactions, regardless of
where the seller is located, must charge VAT as specified by the
applicable regulations in the jurisdiction of the customer *buying*
the service.

In addition, if your store also serves business-to-business (B2B)
transactions, your customers will expect to be able to pay VAT-free
under the Reverse Charge system. In order to enable them to do so, you
will are required to collect and verify your customer's
[VAT Identification Number (VATIN)](https://en.wikipedia.org/wiki/VAT_identification_number).

This extension enables the Oscar e-commerce framework for proper VAT
processing, including VAT for digital goods. It relies heavily on the
[Python `vat_moss` framework](https://github.com/wbond/vat_moss-python),
developed by [Will Bond](https://wbond.net/). It does *not* require a
paid subscription to an online VAT lookup service: the only external
service it does use (for VATIN verification) is the SOAP interface to
the European Commission's
[VAT Information Exchange System (VIES)](http://ec.europa.eu/taxation_customs/vies/),
which is available free of charge.


## Currently implemented features

This app is currently able to:

- obtain a customer's applicable VAT rate through their address and
  phone number
- collect a customer's VATIN and verify it against registered their
  registered company name and registration country
- apply the correct VAT rate to an order during checkout, if using a
  [DeferredTax](http://django-oscar.readthedocs.org/en/latest/_modules/oscar/apps/partner/strategy.html#DeferredTax)
  strategy
- display VAT-inclusive prices at correct VAT rates to logged-in
  users, if using a [FixedRateTax](http://django-oscar.readthedocs.org/en/latest/_modules/oscar/apps/partner/strategy.html#FixedRateTax) strategy
- create a zero-rate order if VATIN is given and has been properly
  verified (for B2B transactions)


## Pending features (not yet implemented)

This app currently does not:

- apply different VAT policies based on product type or category. It
  currently assumes that *all* your products use the same VAT
  strategy.
- automatically generate regulation-compliant invoices.
- automatically generate any aggregated information that you can
  easily use for a VATMOSS return.


## Requirements

This Oscar extension has been tested with Django 1.8 and Oscar
1.1. Django 1.9 support is planned for the Oscar 1.2 release. There
are no plans to support Django 1.7 or Oscar 1.0.

The [CI
infrastructure](https://travis-ci.org/hastexo/django-oscar-vat_moss)
currently runs all unit and integration tests on Python 2.7, 3.3, and
3.4, so all those Python versions should be considered supported.