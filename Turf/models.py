from django.db import models

# Create your models here.
class TurfDb(models.Model):
    turf_name=models.CharField(max_length=50)
    location=models.CharField(max_length=50)
    turf_type=models.CharField(max_length=50)
    price_per_hour=models.DecimalField(max_digits=8,decimal_places=2)
    description=models.TextField()
    is_available=models.BooleanField(default=True)

    def __str__(self):
        return self.name

class bookingDb(models.Model):
    user_name=models.CharField(max_length=25)
    booking_date=models.DateField()
    start_time=models.TimeField()
    end_time=models.TimeField()
    total_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    status=models.CharField(max_length=20,default="confirmed")

    def __str__(self):
        return self.user_name
    
