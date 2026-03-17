from django.db import models
from django.contrib.auth.models import User


class PetReport(models.Model):

    REPORT_TYPE_CHOICES = (
        ('Lost', 'Lost'),
        ('Found', 'Found'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Closed', 'Closed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    pet_name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=50)
    breed = models.CharField(max_length=100)
    color = models.CharField(max_length=100)

    location = models.CharField(max_length=200)
    description = models.TextField()

    phone_number = models.CharField(max_length=15, null=True, blank=True)

    report_type = models.CharField(
        max_length=10,
        choices=REPORT_TYPE_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    pet_image = models.ImageField(upload_to='pet_reports/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.pet_name} - {self.status}"


class Notification(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username}"