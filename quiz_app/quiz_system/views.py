from django.shortcuts import redirect, render, HttpResponse, get_object_or_404
from .models import Question, Team, RoundInfo, Round
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .utils import admin_required, get_live_feed_data
from django.db.models import Sum, Case, When, Exists, OuterRef
from django.utils import timezone
from django.db import models

# login view
class CustomLoginView(LoginView):
    success_url = reverse_lazy('home')  # Redirect to 'home' URL after successful login


@login_required
def index(request):
    if request.user.is_staff:
        # Render the admin page for staff users (admins)
        return redirect('/panel/admin/')
    else:
        # Render the normal home page for non-admin users
        questions_queryset = Question.objects.all()

        # Annotate each question with whether it has been attempted and passed by the user's team
        questions = []
        try:
            team_id = Team.objects.get(user=request.user)
        except Team.DoesNotExist:
            # If Team doesn't exist for the user, create a new one
            team_id = Team.objects.create(user=request.user)

        # Check if there is an ongoing round
        current_time = timezone.now()
        ongoing_round = Round.objects.filter(start__lte=current_time, stop__gt=current_time).first()

        roundinfo_qs = RoundInfo.objects.filter(team_id=team_id).values('question_selected_id', 'choice_is_correct_answer')

        for question in questions_queryset:
            attempted = False
            passed = False
            for roundinfo in roundinfo_qs:
                if roundinfo['question_selected_id'] == question.id:
                    attempted = True
                    passed = bool(roundinfo['choice_is_correct_answer'])
                    break
            
            # Check if the question has already been chosen in the ongoing round
            if ongoing_round and RoundInfo.objects.filter(round_id=ongoing_round.id, question_selected_id=question.id).exists():
                print("Ongoing Round")
                chosen_in_ongoing_round = True
            else:
                chosen_in_ongoing_round = False

            questions.append({
                'id': question.id,
                'author': question.author,
                'attempted': attempted,
                'passed': passed,
                'chosen_in_ongoing_round': chosen_in_ongoing_round
            })

        return render(request, 'quiz_system/home.html', {'questions': questions})




@login_required
def leaderboard(request):
    # Query RoundInfo table to get the total points for each team/user
    scoreboard = (
        RoundInfo.objects
        .values('team_id__user__username')
        .annotate(total_points=Sum('marks_awarded'))
        .order_by('-total_points')
    )

    # Convert the query result into a list of dictionaries
    leaderboard = [
        {'team_name': item['team_id__user__username'], 'total_points': item['total_points'], 'team_position': i + 1}
        for i, item in enumerate(scoreboard)
    ]

    return render(request, 'quiz_system/leaderboard.html', {'leaderboard': leaderboard})



@login_required
def question_view(request, question_id):
    # Fetch the question object matching the given ID or return 404 if not found
    question = get_object_or_404(Question, id=question_id)

    # Fetch all choices related to the question
    choices = question.choices_set.all()
    print(choices)
    # Construct a dictionary containing all fields of the question object
    question_data = {
        'id': question.id,
        'text': question.text,
        'type': question.type,
        'choices': [{'id': choice.id, 'text': choice.text} for choice in choices]
        # Add more fields here if needed
    }

    return render(request, 'quiz_system/question_page.html', {'question': question_data})

@admin_required
def index_admin(request):
    # Your view logic goes here
    live_feed_data = get_live_feed_data()
    print(live_feed_data)
    return render(request, 'quiz_system/competition_control_admin.html', {'live_feed_data': live_feed_data})


@admin_required
def questions_admin(request, question_id):
    question = {
        'text': 'How old is Makerere University?',
        'options': [
            12, 15, 34, 100
        ]
    }
    return render(request, 'quiz_system/question_page_admin.html', {'question': question})



from django.contrib.auth.signals import user_logged_in
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# channel specific things
def user_logged_in_handler(sender, request, user, **kwargs):
    channel_layer = get_channel_layer()
    message = f"User {user.username} logged in"
    async_to_sync(channel_layer.group_send)('admin_group', {'type': 'notify_admins', 'message': message})

user_logged_in.connect(user_logged_in_handler)


