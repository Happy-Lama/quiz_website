# admin.py
from django.contrib import admin
from .models import Question, Choices, Round, Team

# admin.site.register(Question)
admin.site.register(Choices)
admin.site.register(Round)
admin.site.register(Team)

class ChoiceInline(admin.StackedInline):
    model = Choices
    extra = 1

class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]

admin.site.register(Question, QuestionAdmin)


