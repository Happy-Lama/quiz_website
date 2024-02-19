from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.
"""
-	Question:
o	Fields: id, text, type
-	Team:
o	Fields: user
-	Choices:
o	Fields: question_id, text, choice_id
-	Answers:
o	Fields: question_id, choice_id, marks_awarded
-	Round:
o	Fields: id, start, stop
-	RoundInfo:
o	Fields: round_id, team_id, question_selected_id, choice_made_id, choice_is_correct_answer, marks_awarded

"""

class Question(models.Model):
    text = models.CharField(max_length=5000)
    type = models.CharField(max_length=255, default="MCQ")
    author = models.CharField(max_length=255)

class Team(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Choices(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=2048)

class Answers(models.Model):
    question_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.CharField(max_length=2048, null=True)
    marks_awarded = models.PositiveIntegerField()

class Round(models.Model):
    start = models.DateTimeField(default=timezone.now)
    stop = models.DateTimeField()

class RoundInfo(models.Model):
    round_id = models.ForeignKey(Round, on_delete=models.CASCADE)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    question_selected_id = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_made_id = models.ForeignKey(Choices, on_delete=models.CASCADE, null=True)
    choice_is_correct_answer = models.BooleanField(default=False, null=True) 
    marks_awarded = models.PositiveIntegerField(null=True)