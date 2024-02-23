from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.


class Round(models.Model):
    states_a = 'Ongoing'
    states_b = 'Completed'
    states_default = 'Inaccessible'

    STATES = [
        (states_a, 'Round is ongoing'),
        (states_b, 'Round has ended'),
        (states_default, 'Round is inaccessble to all participants')
    ]

    start = models.DateTimeField(null=True, default=None)
    stop = models.DateTimeField(null=True, default=None)
    round_name = models.CharField(max_length=255, default="")
    duration = models.PositiveIntegerField(default=15)
    state = models.CharField(max_length=12, choices=STATES, default="Inaccessible")
    question_time = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"Round {self.id} <{self.round_name}>"
    
class Question(models.Model):
    type_mcq = "MCQ"
    type_short_answer = "SA"

    QUESTION_TYPES = [
        (type_mcq, "MCQ Type Questions"),
        (type_short_answer, "Short Answer Type Questions")
    ]
    text = models.CharField(max_length=5000)
    type = models.CharField(max_length=3, default="MCQ", choices=QUESTION_TYPES)
    round_id = models.ForeignKey(Round, on_delete=models.SET_NULL, null=True, default=None)
    answer = models.CharField(max_length=255, default="", null=True)
    marks = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='images/', null=True, default=None, blank=True)

    def __str__(self):
        return f"Question <{self.type}>"

class Team(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    logged_in = models.BooleanField(default=False)

class Choices(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=2048)


class RoundInfo(models.Model):
    round_id = models.ForeignKey(Round, on_delete=models.CASCADE)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    question_selected_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer_selected_text = models.CharField(max_length=255, null=True, default=None)
    choice_is_correct_answer = models.BooleanField(default=False, null=True) 
    marks_awarded = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"RoundInfo <Team {self.team_id}, Round {self.round_id}>"