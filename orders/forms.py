from django import forms
from .models import Order

PAKISTAN_PROVINCES = [
    ('', 'Select Province'),
    ('Punjab', 'Punjab'),
    ('Sindh', 'Sindh'),
    ('KPK', 'Khyber Pakhtunkhwa'),
    ('Balochistan', 'Balochistan'),
    ('Gilgit-Baltistan', 'Gilgit-Baltistan'),
    ('AJK', 'Azad Jammu & Kashmir'),
    ('Islamabad', 'Islamabad Capital Territory'),
]


class CheckoutForm(forms.ModelForm):
    province = forms.ChoiceField(
        choices=PAKISTAN_PROVINCES,
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'})
    )

    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'alt_phone', 'address', 'city', 'province', 'postal_code', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Your full name *',
                'autocomplete': 'name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Email address (for order confirmation)',
                'autocomplete': 'email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Phone number * (e.g. 0300-1234567)',
                'autocomplete': 'tel',
                'type': 'tel',
            }),
            'alt_phone': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Alternative number (optional)',
                'type': 'tel',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'rows': 2,
                'placeholder': 'House/Flat no., Street, Area *',
                'autocomplete': 'street-address',
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'City *',
                'autocomplete': 'address-level2',
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Postal code',
                'autocomplete': 'postal-code',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control form-control-lg',
                'rows': 2,
                'placeholder': 'Any special instructions? (optional)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['full_name'].required = True
        self.fields['phone'].required = True
        self.fields['address'].required = True
        self.fields['city'].required = True
        self.fields['province'].required = True
        self.fields['email'].required = False
        self.fields['alt_phone'].required = False
        self.fields['postal_code'].required = False
        self.fields['notes'].required = False
