from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=150)
    grade = models.CharField(max_length=10)
    medium = models.CharField(max_length=20)  # English / Tamil / Hindi etc.
    school_name = models.CharField(max_length=200)


    learning_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced')
        ],
        default='beginner'
    )

    def __str__(self):
        return self.full_name
