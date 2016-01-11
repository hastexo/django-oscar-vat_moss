from django.db.models.fields import CharField
from django.core import validators
from oscar.forms import fields

import vat_moss.id

# The longest VAT IDs are currently 2-letter country code + 15
# characters. Make the max_length 32 to be on the safe side.
DEFAULT_MAX_LENGTH=32

class VATINField(CharField):
    def __init__(self, verbose_name=None, name=None,
                 verify_exists=None, **kwargs):
        
        kwargs['max_length'] = kwargs.get('max_length', DEFAULT_MAX_LENGTH)
        CharField.__init__(self, verbose_name, name, **kwargs)
        validator = VATINValidator()
        self.validators.append(validator)

    def formfield(self, **kwargs):
        # As with CharField, this will cause VATIN validation to be performed
        # twice.
        defaults = {
            'form_class': fields.VATINField,
        }
        defaults.update(kwargs)
        return super(ExtendedURLField, self).formfield(**defaults)

    def deconstruct(self):
        """
        deconstruct() is needed by Django's migration framework
        """
        name, path, args, kwargs = super(VATINField, self).deconstruct()
        # We have a default value for max_length; remove it in that case
        if self.max_length == DEFAULT_MAX_LENGTH:
            del kwargs['max_length']
        return name, path, args, kwargs


class VATINValidator(validators.BaseValidator):
    def __call__(self, value):
        """Verify that a VATIN is valid and exists"""
        return self.validate_vatin(value)

    def validate_vatin(self, value):
        """Validate a VATIN and check that it exists.

        :raises: 
            ValidationError wrapping one of the following errors from
            vat_moss.id:
                ValueError - If the is not a string or is not in the
                format of two characters plus an identifier
                InvalidError - If the VAT ID is not valid
                WebServiceUnavailableError - If the VIES VAT ID
                service is unable to process the request - this is
                fairly common
                WebServiceError - If there was an error parsing the
                response from the server - usually this means
                something changed in the webservice
                urllib.error.URLError/urllib2.URLError - If there is
                an issue communicating with VIES or data.brreg.no
        """
        try:
            vat_moss.id.validate(value)
        except Exception as e:
            raise ValidationError(_(str(e)))
