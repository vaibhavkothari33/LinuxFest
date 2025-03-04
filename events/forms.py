from django import forms
from .models import FormField
import json

class DynamicRegistrationForm(forms.Form):
    def __init__(self, *args, event=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        self.conditional_field_map = {}  # Store field relationships
        if event:
            self.add_form_fields()

    def add_form_fields(self):
        fields = self.event.form_fields.all().order_by('order')
        for field in fields:
            field_kwargs = {
                'label': field.label,
                'required': field.required,
                'help_text': field.help_text if hasattr(field, 'help_text') else '',
            }

            if field.field_type == 'text':
                field_kwargs['widget'] = forms.TextInput(attrs={'placeholder': field.placeholder or ''})
                form_field = forms.CharField(**field_kwargs)
            elif field.field_type == 'email':
                field_kwargs['widget'] = forms.EmailInput(attrs={'placeholder': field.placeholder or ''})
                form_field = forms.EmailField(**field_kwargs)
            elif field.field_type == 'number':
                field_kwargs['widget'] = forms.NumberInput(attrs={'placeholder': field.placeholder or ''})
                form_field = forms.IntegerField(**field_kwargs)
            elif field.field_type == 'choice':
                choices = [(choice, choice) for choice in field.get_choices()]
                field_kwargs['widget'] = forms.Select()
                field_kwargs['choices'] = [('', '-- Select --')] + choices
                form_field = forms.ChoiceField(**field_kwargs)
            elif field.field_type == 'date':
                field_kwargs['widget'] = forms.DateInput(attrs={'type': 'date'})
                form_field = forms.DateField(**field_kwargs)
            elif field.field_type == 'file':
                form_field = forms.FileField(**field_kwargs)
            else:
                form_field = forms.CharField(**field_kwargs)  # Default to CharField

            # Store the field instance on the form field for template access
            form_field.conditional_field = field.conditional_field
            form_field.conditional_value = field.conditional_value
            
            # Store conditional relationships for validation
            if field.conditional_field:
                self.conditional_field_map[f'field_{field.id}'] = {
                    'controlling_field': f'field_{field.conditional_field.id}',
                    'required_value': field.conditional_value,
                    'originally_required': field.required  # Store original required state
                }

            self.fields[f'field_{field.id}'] = form_field
    
    def _should_field_be_hidden(self, field_name, data):
        """Check if a field should be hidden based on its conditions"""
        if field_name not in self.conditional_field_map:
            return False

        condition = self.conditional_field_map[field_name]
        controlling_value = data.get(condition['controlling_field'])
        
        # If controlling field is empty or doesn't match required value, field should be hidden
        return not controlling_value or controlling_value != condition['required_value']

    def clean(self):
        """Custom clean method to handle conditional validation"""
        cleaned_data = super().clean()  # Get the parent's cleaned data
        
        if not cleaned_data:  # If parent validation failed, return empty dict
            return {}

        # Get visible fields data
        visible_data = {}
        for field_name, value in self.data.items():
            if not (field_name in self.fields and self._should_field_be_hidden(field_name, self.data)):
                visible_data[field_name] = value

        # Remove data for hidden fields
        for field_name in list(cleaned_data.keys()):
            if self._should_field_be_hidden(field_name, visible_data):
                del cleaned_data[field_name]
                # Also remove any validation errors for hidden fields
                if field_name in self._errors:
                    del self._errors[field_name]
        
        return cleaned_data  # Return the cleaned data explicitly

    def is_valid(self):
        """Override is_valid to handle conditional fields"""
        is_valid = super().is_valid()
        
        # If form is not valid, ensure we still have cleaned_data
        if not is_valid:
            self.cleaned_data = self.clean()
        
        return is_valid