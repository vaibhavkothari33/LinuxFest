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

            # Store the field instance and conditional info
            form_field.field_instance = field
            form_field.conditional_field = field.conditional_field
            form_field.conditional_value = field.conditional_value
            form_field.originally_required = field.required
            
            # Store conditional relationships for validation
            if field.conditional_field:
                self.conditional_field_map[f'field_{field.id}'] = {
                    'controlling_field': f'field_{field.conditional_field.id}',
                    'required_value': field.conditional_value,
                    'originally_required': field.required
                }

            self.fields[f'field_{field.id}'] = form_field
    
    def _should_field_be_hidden(self, field_name, data):
        """Check if a field should be hidden based on its conditions"""
        if field_name not in self.conditional_field_map:
            return False

        condition = self.conditional_field_map[field_name]
        controlling_field = condition['controlling_field']
        required_value = condition['required_value']
        controlling_value = data.get(controlling_field, '')
        
        # Field should be shown if controlling field matches required value
        return controlling_value != required_value

    def clean(self):
        cleaned_data = super().clean()
        
        # Get a copy of the submitted data for condition checking
        data = self.data.copy() if hasattr(self, 'data') else {}
        
        # Check each field for conditional validation
        for field_name, field in self.fields.items():
            # If field has conditions
            if hasattr(field, 'conditional_field') and field.conditional_field:
                controlling_field_name = f'field_{field.conditional_field.id}'
                controlling_value = data.get(controlling_field_name)
                
                # If controlling field matches the condition
                if controlling_value == field.conditional_value:
                    # Field should be visible and validated
                    if field.originally_required and not cleaned_data.get(field_name):
                        self.add_error(field_name, 'This field is required.')
                else:
                    # Field should be hidden and not validated
                    if field_name in cleaned_data:
                        del cleaned_data[field_name]
                        if field_name in self._errors:
                            del self._errors[field_name]
        
        return cleaned_data