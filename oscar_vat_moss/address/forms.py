from oscar.apps.address.forms import UserAddressForm as CoreUserAddressForm

class UserAddressForm(CoreUserAddressForm):
    class Meta(CoreUserAddressForm.Meta):
        fields = CoreUserAddressForm.Meta.fields + ['vatin']
