from django import forms
from .models import Location, Organization, Character

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
            'location': forms.Select(attrs={
                'id': 'location',
                'required': False,
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

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ['name', 'race', 'class_field', 'level', 'location', 'hostility', 'related_organizations', 'related_characters', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'id': 'organization-name',
                'required': 'required',
                'placeholder': 'Enter organization name',
            }),
            'race' : forms.TextInput(attrs={
                'id' : 'race-name',
                'required' : 'required',
                'placeholder' : 'Race name',
            }),
            'class_field' : forms.TextInput(attrs={
                'id' : 'class-name', #CLASSES
                'required' : 'required',
                'placeholder' : 'Class select',
            }),
            'level' : forms.NumberInput(attrs={
                'id' : 'level-number', #CLASSES
                'required' : 'required',
                'placeholder' : 'What level are you?',
            }),
            'location': forms.Select(attrs={
                'id': 'location',
                'required': False,
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
            'related_characters' : forms.SelectMultiple(attrs={
                'id' : 'characters',
                'required' : False,
                'placeholder' : 'What is your character connected to?',
            }),
            'description': forms.Textarea(attrs={
                'id': 'organization-description',
                'required' : 'required',
                'placeholder': 'Enter a brief description',
            }),
        }