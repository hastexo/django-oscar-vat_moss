# DeferredVATCheckoutSessionMixin is the safer option,
# make that the default
from oscar_vat_moss.checkout.mixins import DeferredVATCheckoutSessionMixin

CheckoutSessionMixin = DeferredVATCheckoutSessionMixin
