from django import forms
from .models import PlantHealth, UserPlant

class PlantHealthForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Make sure the list of dropdown is only the user's plants
            self.fields['plant_id'].queryset = UserPlant.objects.filter(user=self.user)

    # Defining fields to be shown
    class Meta:
        model = PlantHealth
        fields = ['plant_id', 'height', 'observation', 'image']


class UserPlantForm(forms.ModelForm):
    # Defining form fields to be shown
    class Meta:
        model = UserPlant
        fields = ['nickname', 'common_name', 'thumbnail']