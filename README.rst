oscar\_vat\_moss
================

Enables EU VATMOSS processing for the Oscar e-commerce system
-------------------------------------------------------------

.. image:: https://travis-ci.org/hastexo/django-oscar-vat_moss.svg?branch=master
   :target: https://travis-ci.org/hastexo/django-oscar-vat_moss

.. image:: https://codecov.io/github/hastexo/django-oscar-vat_moss/coverage.svg?branch=master
   :target: https://codecov.io/github/hastexo/django-oscar-vat_moss?branch=master
		    
This package enables e-commerce application based on Django Oscar to
assess and charge VAT (Value Added Tax) according to EU regulations.

It is based on
`django-oscar <https://github.com/django-oscar/django-oscar/>`_
and
`vat_moss-python <https://github.com/wbond/vat_moss-python>`_.

Installation
------------

For now, install with

::

    pip install https://github.com/hastexo/django-oscar-vat_moss/archive/master.zip

to get the latest master. There are no named releases yet, and the
package isn't yet on PyPI.

Use
---

To use, you must

-  Enable a pricing ``Strategy`` that uses the ``DeferredTax`` tax mixin

-  Add a ``CheckoutSessionMixin`` to your checkout session, so taxes can
   be applied when the customer's shipping address is known

-  Optionally extend your data model with a field accommodating your
   customer's VATIN (VAT Identification Number) if you want to enable
   VAT-free B2B transactions under the reverse charge system. If all
   your transactions are B2C, this last bit may be safely omitted.

Enabling a VAT-enabled pricing strategy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``oscar_vat_moss.partner.strategy.VATStrategy`` to your
``partner/strategy.py`` module, and update your ``Selector`` to use it
when appropriate:

.. code:: python

    # partner/strategy.py

    from oscar_vat_moss.partner.strategy import VATStrategy

    class Selector(object):
        def strategy(self, request=None, user=None, **kwargs):
            # Apply your strategy selection logic, where appropriate:
            return VATStrategy(request)

If you only want one selector and you **always** want to apply
``VATStrategy``, you may also simply use:

.. code:: python

    # partner/strategy.py

    from oscar_vat_moss.partner.strategy import *

Applying VAT on checkout
~~~~~~~~~~~~~~~~~~~~~~~~

Add ``oscar_vat_moss.checkout.session.CheckoutSessionMixin`` to your
``checkout/session.py`` module:

.. code:: python

    # checkout/session.py

    from oscar_vat_moss.checkout.session import CheckoutSessionMixin

Documentation
~~~~~~~~~~~~~~~~~~~~~~~~

Additional documentation can be found at
http://django-oscar-vat-moss.readthedocs.org/en/master/.
