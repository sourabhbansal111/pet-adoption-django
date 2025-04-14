from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom User model (optional if using default auth)

class Usert(AbstractUser):
    profile_picture = models.ImageField(upload_to='home/static/images/uploads/users/', null=True, blank=True)
    role = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=15,blank=True)
    dob=models.DateField(null=True ,blank=True)
    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    )
    gender=models.CharField(max_length=20,choices=GENDER_CHOICES,blank=True)
    is_verified=models.BooleanField(default=False)
    address=models.CharField(null=True,blank=True,max_length=400 ,default="-")

    def __str__(self):
        return self.username

class Contact(models.Model):
    nameuser = models.CharField(max_length=100)
    number = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    location = models.CharField(max_length=200)
    message = models.TextField(max_length=5000)
    type_CHOICES = (
        ('pet', 'Pet Adorption'),
        ('service', 'Pet Service'),
    )
    type=models.CharField(max_length=20,choices=type_CHOICES)
    pname = models.CharField(max_length=100)
    pid = models.CharField(max_length=100)
    status = models.CharField(max_length=10, default="NV")  # NV = Not Verified?

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

class Letter(models.Model):
    firstname = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    number = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    message = models.TextField(max_length=5000)
    status = models.CharField(max_length=10, default="NR")  # NR = Not Read?

    def __str__(self):
        return self.firstname

class Blog(models.Model):
    id = models.IntegerField(primary_key=True)  # Custom ID, manually set
    photo = models.URLField(max_length=200)
    pet_name = models.CharField(max_length=100)
    heading_explanation = models.TextField()
    subheadings = models.TextField(default="", blank=True)  # **-separated values
    explanations = models.TextField(default="", blank=True)  # **-separated values

    def get_subheading_list(self):
        return self.subheadings.split("**") if self.subheadings else []

    def get_explanation_list(self):
        return self.explanations.split("**") if self.explanations else []

    def __str__(self):
        return self.pet_name
