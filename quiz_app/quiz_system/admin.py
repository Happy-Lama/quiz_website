# admin.py
from django.contrib import admin
from .models import Question, Choices, Answers

# admin.site.register(Question)
admin.site.register(Choices)
admin.site.register(Answers)

class ChoiceInline(admin.StackedInline):
    model = Choices
    extra = 4

class AnswerInline(admin.StackedInline):
    model = Answers
    extra = 1  # You can adjust this as needed

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline, AnswerInline]

admin.site.register(Question, QuestionAdmin)
