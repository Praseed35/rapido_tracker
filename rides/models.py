from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class DailyRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    petrol_expense = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    @property
    def total_earnings(self):
        return sum(ride.earning for ride in self.rides.all()) or 0
    
    @property
    def total_commission(self):
        return sum(ride.commission for ride in self.rides.all()) or 0
    
    @property
    def total_savings(self):
        return self.total_earnings - self.total_commission
    
    @property
    def final_savings(self):
        return self.total_savings - self.petrol_expense

class Ride(models.Model):
    daily_record = models.ForeignKey(DailyRecord, on_delete=models.CASCADE, related_name='rides')
    earning = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Ride on {self.daily_record.date}"
    
    @property
    def savings(self):
        return self.earning - self.commission
    


class Ride(models.Model):
    daily_record = models.ForeignKey(DailyRecord, on_delete=models.CASCADE, related_name='rides')
    earning = models.DecimalField(max_digits=10, decimal_places=2)
    commission = models.DecimalField(max_digits=10, decimal_places=2)
    device_time = models.DateTimeField(null=True, blank=True)  # New field for device time
    timestamp = models.DateTimeField(auto_now_add=True)  # Keep server time for reference
    
    class Meta:
        ordering = ['timestamp']  # Or 'id' if you prefer
        
    def __str__(self):
        return f"Ride on {self.timestamp}"
    @property
    def savings(self):
        return self.earning - self.commission