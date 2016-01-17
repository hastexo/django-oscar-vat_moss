from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

default_app_config = 'oscar_vat_moss.checkout.config.CheckoutConfig'

# In order to assess VAT based on address and phone number (we always
# need to record at least 2 bits of information to assess a customer's
# VAT status), we must make sure that the following address fields are
# marked as required:
VAT_REQUIRED_ADDRESS_FIELDS = ['city', 'country', 'line1', 'postcode',
                               'phone_number']


def assert_required_fields_set_correctly():
    # Reminder: for sets, the <= operator determines whether every
    # element in the first set is also present in the second set.
    if not (set(VAT_REQUIRED_ADDRESS_FIELDS) <=
            set(settings.OSCAR_REQUIRED_ADDRESS_FIELDS)):
        raise ImproperlyConfigured('Must enable at least %s '
                                   'in OSCAR_REQUIRED_ADDRESS_FIELDS' %
                                   VAT_REQUIRED_ADDRESS_FIELDS)
