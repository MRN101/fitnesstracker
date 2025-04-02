from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    height = models.DecimalField(max_digits=5, decimal_places=2)
    gender = models.CharField(max_length=10)
    dob = models.DateField()

    def __str__(self):
        return self.user.username

    def calculate_bmi(self):
        height_in_meters = self.height / 100
        bmi = self.weight / (height_in_meters ** 2)
        return round(bmi, 2)

class Workout(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    calories = models.IntegerField()
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.name} - {self.calories} calories ({self.date})"

class Step(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    steps_taken = models.IntegerField()

    def __str__(self):
        return f"{self.date}: {self.steps_taken} steps"

    def calories_burned(self):
        return round(self.steps_taken * 0.04, 2)

class Nutrition(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_name = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now) 
    calories = models.IntegerField()

    def __str__(self):
        return f"{self.date}: {self.food_name} - {self.calories} cal"