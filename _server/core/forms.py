from django import forms
from .models import Location, Organization

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'hostility', 'neighboring_locations', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'location-name',
                'required': 'required',
                'placeholder': 'Enter location name',
            }),
            'hostility': forms.Select(attrs={
                'id': 'location-hostility',
                'required': 'required',
                'placeholder': 'Select Hostility Level',
            }),
            'neighboring_locations': forms.SelectMultiple(attrs={
                'id': 'location-neighbors',
                'multiple': 'multiple',
                'required': False,
            }),
            'description': forms.Textarea(attrs={
                'id': 'location-description',
                'placeholder': 'Enter a brief description',
            }),
        }

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name', 'location', 'hostility', 'related_organizations', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'organization-name',
                'required': 'required',
                'placeholder': 'Enter organization name',
            }),
            'hostility': forms.Select(attrs={
                'id': 'organization-hostility',
                'required': 'required',
                'placeholder': 'Select Hostility Level',
            }),
            'related_organizations': forms.SelectMultiple(attrs={
                'id': 'related-organizations',
                'multiple': 'multiple',
                'required': False,
            }),
            'description': forms.Textarea(attrs={
                'id': 'organization-description',
                'placeholder': 'Enter a brief description',
            }),
        }