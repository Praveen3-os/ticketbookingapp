from django import forms
from .models import Booking, SupportTicket


class BookingForm(forms.Form):
    seats = forms.IntegerField(
        min_value=1, max_value=10, initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 10})
    )


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ['name', 'email', 'subject', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'you@email.com'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your issue…'}),
        }
