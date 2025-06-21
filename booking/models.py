from django.db import models
from authentication.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from .views import send_flight_email, send_visa_email

# Create your models here.


class Flight(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='flights')
    from_city = models.CharField(max_length=100)
    to_city = models.CharField(max_length=100)
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField(blank=True, null=True)
    airline = models.CharField(max_length=100, blank=True, null=True)
    boarding_class = models.CharField(max_length=20, choices=[
        ('economy', 'Economy'), ('business', 'Business'), ('first-class', 'First Class')], default='economy')
    trip_type = models.CharField(max_length=20, choices=[
        ('oneway', 'One Way'), ('return', 'Round Trip'), ('multi', 'Multi City')], default='oneway')
    passenger = models.IntegerField(default=1)
    flight_number = models.CharField(max_length=20, blank=True, null=True)
    

    def __str__(self):
        return f"{self.airline} from {self.from_city} to {self.to_city}"


class Visa(models.Model):
    TYPE_CHOICE= (("tourist", 'Tourist'), ('student','Student'), ('work', 'Work'))
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='visas')
    visa_type = models.CharField(max_length=50, choices=TYPE_CHOICE)
    nationality= models.CharField(max_length=50)
    country = models.CharField(max_length=100)
    duration = models.CharField(max_length=50)
    reason = models.TextField()
    travel_date = models.DateTimeField()
    
    def __str__(self):
        return f"{self.visa_type} for {self.country}"

@receiver(post_save, sender=Flight)
def onFlightSave(sender, instance, created, **kwargs):
    if not created:
        return
    send_flight_email(instance)
    
@receiver(post_save, sender=Visa)
def onVisaSave(sender, instance, created, **kwargs):
    if not created:
        return
    send_visa_email(instance)