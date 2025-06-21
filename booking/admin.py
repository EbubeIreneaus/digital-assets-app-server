from django.contrib import admin
from .models import Flight, Visa
    
# Register your models here.
class FlightAdmin(admin.ModelAdmin):
    list_display = ['user', 'flight_number', 'from_city', 'to_city', 'departure_date', 'arrival_date', 'airline']
    search_fields = ['user','flight_number']
   

class VisaAdmin(admin.ModelAdmin):
    list_display = ['user', 'visa_type', 'country', 'duration']
    search_fields = ['user', 'visa_type']
    list_filter = ['country', 'visa_type']

admin.site.register(Flight, FlightAdmin)
admin.site.register(Visa, VisaAdmin)
