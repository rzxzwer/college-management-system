from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Администратор'),
        ('staff', 'Персонал'),
        ('student', 'Студент'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    department = models.CharField(max_length=100, blank=True)
    group = models.CharField(max_length=50, blank=True)

class Department(models.Model):
    name = models.CharField(max_length=100)
    data = models.JSONField(default=dict)

class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    course = models.IntegerField()
    group = models.CharField(max_length=50)
    data = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.group}"

class Staff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    data = models.JSONField(default=dict)

class Statistics(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    data = models.JSONField(default=dict)
