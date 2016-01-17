from __future__ import unicode_literals
from django.core.urlresolvers import reverse
from oscar.core.loading import get_model, get_class
from oscar.test import factories
from oscar.test.testcases import WebTestCase
from decimal import Decimal as D

Order = get_model('order', 'Order')
UserAddress = get_model('address', 'UserAddress')
GatewayForm = get_class('checkout.forms', 'GatewayForm')
Country = get_model('address', 'Country')


class CheckoutMixin(object):

    def create_digital_product(self):
        product_class = factories.ProductClassFactory(
            requires_shipping=False, track_stock=False)
        product = factories.ProductFactory(product_class=product_class)
        factories.StockRecordFactory(
            num_in_stock=None, price_excl_tax=D('12.00'), product=product)
        return product

    def add_product_to_basket(self, product=None):
        if product is None:
            product = factories.ProductFactory()
            factories.StockRecordFactory(
                num_in_stock=10, price_excl_tax=D('12.00'), product=product)
        detail_page = self.get(product.get_absolute_url())
        form = detail_page.forms['add_to_basket_form']
        form.submit()

    def add_voucher_to_basket(self, voucher=None):
        if voucher is None:
            voucher = factories.create_voucher()
        basket_page = self.get(reverse('basket:summary'))
        form = basket_page.forms['voucher_form']
        form['code'] = voucher.code
        form.submit()

    def enter_guest_details(self, email='guest@example.com'):
        index_page = self.get(reverse('checkout:index'))
        index_page.form['username'] = email
        index_page.form.select('options', GatewayForm.GUEST)
        return index_page.form.submit()

    def create_shipping_country(self):
        return factories.CountryFactory(
            iso_3166_1_a2='GB', is_shipping_country=True)

    def enter_shipping_address(self):
        self.create_shipping_country()
        address_page = self.get(reverse('checkout:shipping-address'))
        form = address_page.forms['new_shipping_address']
        form['first_name'] = 'John'
        form['last_name'] = 'Doe'
        form['line1'] = '1 Egg Road'
        form['line4'] = 'Shell City'
        form['postcode'] = 'N12 9RT'
        form.submit()

    def enter_shipping_method(self):
        self.get(reverse('checkout:shipping-method'))

    def place_order(self):
        payment_details = self.get(
            reverse('checkout:shipping-method')).follow().follow()
        preview = payment_details.click(linkid="view_preview")
        return preview.forms['place_order_form'].submit().follow()

    def reach_payment_details_page(self, is_guest=False):
        self.add_product_to_basket()
        if is_guest:
            self.enter_guest_details('hello@egg.com')
        self.enter_shipping_address()
        return self.get(
            reverse('checkout:shipping-method')).follow().follow()

    def ready_to_place_an_order(self, is_guest=False):
        payment_details = self.reach_payment_details_page(is_guest)
        return payment_details.click(linkid="view_preview")


class TestShippingAddressView(CheckoutMixin, WebTestCase):

    def setUp(self):
        super(TestShippingAddressView, self).setUp()
        self.user_address = factories.UserAddressFactory(
            user=self.user, country=self.create_shipping_country())

    def test_requires_login(self):
        response = self.get(reverse('checkout:shipping-address'), user=None)
        self.assertIsRedirect(response)

    def test_submitting_valid_form_adds_data_to_session(self):
        self.add_product_to_basket()
        page = self.get(reverse('checkout:shipping-address'))
        form = page.forms['new_shipping_address']
        form['first_name'] = 'Barry'
        form['last_name'] = 'Chuckle'
        form['line1'] = '1 King Street'
        form['line4'] = 'Gotham City'
        form['postcode'] = 'N1 7RR'
        form['phone_number'] = '+44 1273 555 999'
        response = form.submit()
        self.assertRedirectsTo(response, 'checkout:shipping-method')

        session_data = self.app.session['checkout_data']
        session_fields = session_data['shipping']['new_address_fields']
        self.assertEqual('Barry', session_fields['first_name'])
        self.assertEqual('Chuckle', session_fields['last_name'])
        self.assertEqual('1 King Street', session_fields['line1'])
        self.assertEqual('Gotham City', session_fields['line4'])
        self.assertEqual('N1 7RR', session_fields['postcode'])
