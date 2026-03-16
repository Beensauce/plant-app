from django.db import models
from django.contrib.auth.models import User
from PIL import Image # External library to open images

# Create your models here.
class UserPlant(models.Model):
    thumbnail = models.ImageField(upload_to='plant_thumbnail', blank=True, verbose_name='Image')
    common_name = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    last_watered = models.DateTimeField(auto_now=True)
    api_plant_id = models.CharField(max_length=100, blank=True) 
    scientific_name = models.CharField(max_length=100, blank=True)  # From API

    # Fields to store fetched care information
    care_watering = models.TextField(blank=True, help_text="Watering instructions from API")
    care_light = models.TextField(blank=True, help_text="Light requirements from API")
    care_soil = models.TextField(blank=True, help_text="Soil preferences from API")
    plant_description = models.TextField(blank=True, help_text="General description from API")
    toxicity_info = models.TextField(blank=True, help_text="Toxicity information from API")
    
    def __str__(self):
        return f"{self.nickname or self.common_name} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # Saving image first to access it on the server

        if self.thumbnail: # If the object has a picture (thumbnail)
            img = Image.open(self.thumbnail.path) # open the image

            if img.height > 150 or img.width > 350:
                output_size = (300, 300) # Prevents server from running out of space too fast, saves storage and faster load times
                img.thumbnail(output_size) # Maintain aspect ratio
                img.save(self.thumbnail.path) # Saving the iamge into the path

    
class PlantHealth(models.Model):
    # use related_name to access user's plants, when actual plant is deleted, this health log will automatically be deleted
    plant_id = models.ForeignKey(UserPlant, on_delete=models.CASCADE, related_name='health_logs', verbose_name='Plant name') 
    height = models.FloatField()
    checked = models.BooleanField(default=False)
    observation = models.TextField(blank=True)
    image =  models.ImageField(upload_to='plant_pics', default='default.png', blank=True)
    log_date = models.DateTimeField(auto_now=True)

    disease_detected = models.CharField(max_length=255, blank=True)  # From API (name of top suggestion)
    disease_probability = models.FloatField(blank=True, null=True)

    disease_description = models.TextField(blank=True)
    disease_treatment_biological = models.TextField(blank=True)
    disease_treatment_chemical = models.TextField(blank=True)
    disease_treatment_prevention = models.TextField(blank=True)
    disease_cause = models.TextField(blank=True) 
    disease_url = models.URLField(blank=True, null=True) 

    def __str__(self):
        return f"Log for {self.plant_id} on {self.log_date.date()}" # Default output when referring to this class for better visibility
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs) # Saving information first

        if self.image:
            img = Image.open(self.image.path) # Loading image

            if img.height > 150 or img.width > 350: # Checks if image is larger than these requirements
                output_size = (300, 300) # Prevents server from running out of space too fast, saves storage and faster load times
                img.thumbnail(output_size) # Maintain aspect ratio
                img.save(self.image.path) # Saving the iamge into the path

