from django import forms
from .models import Location

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'hostility', 'neighboring_locations', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'location-name',
                'required': 'required',
            }),
            'hostility': forms.Select(attrs={
                'id': 'location-hostility',
                'required': 'required',
            }),
            'neighboring_locations': forms.SelectMultiple(attrs={
                'id': 'location-neighbors',
                'multiple': 'multiple',
            }),
            'description': forms.Textarea(attrs={
                'id': 'location-description',
            }),
        }