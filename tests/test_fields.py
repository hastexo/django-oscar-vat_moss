import unittest
from decimal import Decimal as D
from oscar_vat_moss.fields import *  # noqa
from django.core.exceptions import ValidationError


class VATINValidatorTest(unittest.TestCase):
    VALID_VATINS = (
        # VATIN         # Company name
        ('ATU66688202', 'hastexo Professional Services GmbH'),
        ('ATU66688202', 'HASTEXO PROFESSIONAL SERVICES GMBH'),
        ('ATU66688202', 'hastexo Professional Services GmbH (Procurement Department)'),
        )
    INVALID_VATINS = (
        # VATIN         # Incorrect company name
        ('ATU66688999', 'Example, Inc.'),
        ('ATU99999999', 'Acme, Inc'),
        )

    def test_valid_vatin(self):
        validator = VATINValidator(None)
        for vatin, name in self.VALID_VATINS:
            # Just ensure this doesn't fail
            validator.validate_vatin(vatin)
            # validator is also callable
            validator(vatin)

    def test_invalid_vatin(self):
        validator = VATINValidator(None)
        for vatin, name in self.INVALID_VATINS:
            with self.assertRaises(ValidationError):
                validator.validate_vatin(vatin)

            with self.assertRaises(ValidationError):
                # validator is also callable
                validator(vatin)


class VATINFieldTest(unittest.TestCase):
    
    def test_default_properties(self):
        field = VATINField()
        validator_classes = [ v.__class__ for v in field.validators ]
        self.assertTrue(VATINValidator in validator_classes)
        self.assertEqual(field.max_length, DEFAULT_MAX_LENGTH)

    def test_convenience_method(self):
        field = vatin()
        validator_classes = [ v.__class__ for v in field.validators ]
        self.assertTrue(VATINValidator in validator_classes)
        self.assertEqual(field.max_length, DEFAULT_MAX_LENGTH)
        self.assertEqual(field.name,'vatin')
        self.assertTrue(field.blank)

    def test_formfield(self):
        field = vatin()

        # Just ensure this doesn't fail
        formfield = field.formfield()

    def test_deconstruct(self):
        field = vatin()

        name, path, args, kwargs = field.deconstruct()
        self.assertEqual(name, 'vatin')
