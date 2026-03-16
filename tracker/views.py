# Importing libraries to be used
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DeleteView
from .forms import PlantHealthForm, UserPlantForm
from .models import UserPlant, PlantHealth
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse
from kindwise import PlantApi 
from decouple import config
from json import dumps


# Create your views here.
def index(request):
    return render(request, 'tracker/index.html') # Simply rendering the web page

def add_health_log(request, plant_id=None):
    if request.method == 'POST': # If client is sending a messaeg
        form = PlantHealthForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            image_purpose = request.POST.get('image_purpose')
            plant_health = form.save(commit=False)

            # API logic
            if image_purpose == 'identify':
                try:
                    plant_health.save()
                    image = plant_health.image.path

                    api = PlantApi(config("PLANT_ID_API_KEY")) # Built in functionality from API's SDK

                    health_assessment = api.health_assessment(
                        image,
                        details=['cause', 'description', 'treatment', 'url']
                    ) # Choosing what to get from API

                    plant_health.checked = True
                    # Extract results
                    top_suggestion = None
                    if health_assessment.result.disease.suggestions:
                        top_suggestion = health_assessment.result.disease.suggestions[0]
                    
                    if top_suggestion:
                        plant_health.disease_detected = top_suggestion.name
                        plant_health.disease_probability = top_suggestion.probability
                        
                        # Access details directly from the suggestion object
                        details = top_suggestion.details 
                        plant_health.disease_description = details.get('description', '')
                        plant_health.disease_url = details.get('url', '')
                        plant_health.disease_cause = details.get('cause') or "We don't know"
                        
                        # Get treatment from details
                        treatment_info = details.get('treatment', {})
                        plant_health.disease_treatment_biological = '\n'.join(treatment_info.get('biological', []))
                        plant_health.disease_treatment_chemical = '\n'.join(treatment_info.get('chemical', []))
                        plant_health.disease_treatment_prevention = '\n'.join(treatment_info.get('prevention', []))
                        plant_health.save()
                    
                        messages.success(request, "Health assessment completed successfully!")
                        return redirect('plant-detail', plant_id=plant_health.plant_id.id)

                    else:
                        # No message from API
                        messages.warning(request, "Health assessment completed, but no specific issues were identified.")
                        plant_health.save()
                        return redirect('plant-detail', plant_id=plant_health.plant_id.id)
                
                except Exception as e:
                    # Error from API
                    messages.error(request, f"Health assessment failed: {str(e)}")
                    return redirect('plant-detail', plant_id=plant_health.plant_id.id)
                
            form.save()
            return redirect('plants')  # Redirect to the form page after save
    
            
    else:
        initial_data = {}   
        if plant_id:
            try:
                plant = UserPlant.objects.get(id=plant_id, user=request.user)
                initial_data['plant_id'] = plant.id
            except:
                # Error message shown when the plant not found
                messages.error(request, "Plant not found or you don't have permission to access it.")
                return redirect('plants')

    form = PlantHealthForm(initial=initial_data,  user=request.user)
    return render(request, 'tracker/tracker.html', {'form': form})


class PlantListView(LoginRequiredMixin, ListView):
    model = UserPlant
    template_name = 'tracker/plants.html'
    context_object_name = 'plants'
    form_class = UserPlantForm

    def get_queryset(self):
        # Return a list of plants only by the logged in user
        return UserPlant.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()  # Add empty form to context
        return context
    
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            image_purpose = request.POST.get('image_purpose', 'identify')
            # Doesn't save, but gets so can access the object
            plant = form.save(commit=False)
            plant.user = request.user

            plant.save()
            if image_purpose == 'identify' and plant.thumbnail:
                try:
                    
                    api = PlantApi(config("PLANT_ID_API_KEY")) # SDK functionality

                    identification = api.identify(plant.thumbnail.path, 
                        details=[
                            'common_names', 
                            'url', 
                            'description', 
                            'taxonomy', 
                            'best_watering', 
                            'best_light_condition', 
                            'best_soil_type',
                            'toxicity',
                            'scientific_name',
                            'common_uses'
                        ]) # Choosing what to get from API

                    # extract details from API call
                    if (identification.result.classification.suggestions):

                        suggestions = identification.result.classification.suggestions

                        if len(suggestions) > 0:
                            best_match = suggestions[0] # get the first suggestion, best prediction

                            plant.common_name = best_match.name
                            plant.api_plant_id = best_match.id
                            details = best_match.details
                            
                            # Returns a JSON file, so extract details from it
                            # Setting database object to information retreived
                            if 'best_watering' in details:
                                plant.care_watering = details['best_watering']
                            if 'best_light_condition' in details:
                                plant.care_light = details['best_light_condition']
                            if 'best_soil_type' in details:
                                plant.care_soil = details['best_soil_type']
                            if 'description' in details:
                                plant.plant_description = details['description']['value']
                            if 'toxicity' in details:
                                plant.toxicity_info = details['toxicity']
                            if 'scientific_name' in details:
                                plant.scientific_name = details['scientific_name']

                            # Saving the obejct, and sendinga  sucess messaeg
                            plant.save()
                            messages.success(request, f"Plant identified as: {plant.common_name} (Confidence: {best_match.probability *100 }%)")
                                            
                        else:
                            # When the API doesn't know what plant is sent back
                            plant.common_name = "We don't know"
                            messages.warning(request, "No plant identification found")
                    
                    else:
                        # When the API doesn't know what plant is sent back
                        plant.common_name = "We don't know"
                        messages.warning(request, "No plant identification found")                         
                
                except Exception as e:
                    # Returning error messages if there are any
                    messages.warning(request, f"Plant identification failed: {str(e)}")

            
            return redirect('plant-detail', plant_id=plant.id )
                
        return self.render_to_response(self.get_context_data(form=form))
        
    
@login_required
def water_plant(request, plant_id):
    plant = get_object_or_404(UserPlant, id=plant_id, user=request.user)
    plant.last_watered = timezone.now() # Changing last watered to now
    plant.save(update_fields=['last_watered']) # Saving the time zone

    messages.success(request, f'{plant.nickname or plant.common_name} was watered successfully!') # Sending success message
    return redirect('plants')


@login_required
def plant_detail(request, plant_id):
    # Gatherin object given by plant_id passed through argument
    plant = get_object_or_404(UserPlant, id=plant_id, user=request.user)
    # Getting health logs assosciated with the health_log
    health_logs = plant.health_logs.all().order_by('-log_date')
    health_log_not_reversed = plant.health_logs.all().order_by('log_date')

    # graph data
    chart_dates = []
    chart_heights = []
    n = 0

    #Add dates to arrays
    for log in health_log_not_reversed:
        n = n + 1
        chart_dates.append(f"Log {n} ({log.log_date.strftime('%Y-%m-%d')})")
        chart_heights.append(float(log.height))

    #Make python data usable in javascript
    heightJSON = dumps(chart_heights)
    datesJSON = dumps(chart_dates)

    # Creating context object to pass into web page
    context = {
        'plant': plant,
        'health_logs': health_logs,
        'chart_dates': datesJSON,
        'chart_heights': heightJSON,
    }

    return render(request, 'tracker/plant_detail.html', context)

class DeletePlantListView(LoginRequiredMixin, UserPassesTestMixin, DeleteView): # Loginrequired and UserPasses for security
    model = UserPlant
    success_url = '/plants/'

    def test_func(self): # Checks if the plant is owned by the user
        plant = self.get_object()
        if self.request.user == plant.user:
            return True
        return False

class DeleteTrackListView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = PlantHealth
    def get_success_url(self):
        # Get the plant health record that was just deleted
        health_log = self.object  # self.object contains the deleted instance
        # Redirect to the plant detail page
        return reverse('plant-detail', kwargs={'plant_id': health_log.plant_id.id})

    def test_func(self): #Check whether owner of plant is the user who is logged in
        health_log = self.get_object()
        if self.request.user == health_log.plant_id.user:
            return True
        return False

@login_required
def edit_plant(request, plant_id):
    plant = get_object_or_404(UserPlant, id=plant_id, user=request.user) # Receives the plant object, and making sure its user is the one signed in
    
    if request.method == 'POST':
        form = UserPlantForm(request.POST, request.FILES, instance=plant) # Getting data from the form
        if form.is_valid():
            form.save()
            messages.success(request, f"{plant.nickname or plant.common_name} has been updated!")
            return redirect('plant-detail', plant_id=plant.id)
        else:
            messages.error(request, "Please correct the errors below.") # Returns a error message
    else:
        form = UserPlantForm(instance=plant) # If GET operation, only show form
    
    # Creation of context object to pass through to template
    context = {
        'form': form,
        'plant': plant
    }
    return render(request, 'tracker/edit_plant.html', context)


@login_required
def health_assesment(request, pk):
    # Get health assesment object from primary key provided
    assesment = get_object_or_404(PlantHealth, pk=pk)

    return render(request, 'tracker/health_asesment.html', {'assesment': assesment}) # Rendering web page with assemsment object
