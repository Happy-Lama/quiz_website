from django.shortcuts import redirect, render, get_object_or_404
from .models import Question, Team, RoundInfo, Round
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .utils import admin_required, get_live_feed_data, get_registered_rounds
from django.db.models import Sum
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
        # Get the current ongoing round
        current_round = Round.objects.filter(state='Ongoing', stop__gt=timezone.now()).order_by('-stop').first()
        if current_round:
            # Fetch the questions for the current round
            questions = Question.objects.filter(round_id=current_round)

            team_id = Team.objects.get(user=request.user)

            round_info = RoundInfo.objects.filter(round_id=current_round, team_id=team_id)

            # Create a dictionary to store question information
            questions_info = []

            # Iterate over the questions
            for idx, question in enumerate(questions):
                # Initialize status flags
                attempted_by_user = False
                passed_by_user = False
                attempted_by_others = False

                # Check if the user has attempted this question
                if round_info.filter(question_selected_id=question).exists():
                    attempted_by_user = True
                    passed_by_user = round_info.get(question_selected_id=question).choice_is_correct_answer

                # Check if others have attempted this question
                if RoundInfo.objects.filter(round_id=current_round, question_selected_id=question).exclude(team_id=team_id).exists():
                    attempted_by_others = True

                # Add question information to the dictionary
                questions_info.append({
                    'question_no': idx + 1,
                    'id': question.id,
                    'attempted': attempted_by_user,
                    'passed': passed_by_user,
                    'attempted_by_others': attempted_by_others
                })
            print(questions_info)
            return render(request, 'quiz_system/home.html', {'questions': questions_info})
        return render(request, 'quiz_system/home.html', {'questions': []})





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

@admin_required
def leaderboard_admin(request):
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

    return render(request, 'quiz_system/leaderboard_admin.html', {'leaderboard': leaderboard})

@login_required
def question_view(request, question_id):
    # Fetch the question object matching the given ID or return 404 if not found
    question = get_object_or_404(Question, id=question_id)
    # Check  the roundinfo to see if user has done the question
    try:
        team = Team(user=request.user)
        roundinfo = RoundInfo.objects.get(team_id=team, question_selected_id=question)
        print(roundinfo)
        print(RoundInfo.objects.all())
        if roundinfo:
            redirect('/')
    except:
        redirect('/')
    # Fetch all choices related to the question
    choices = question.choices_set.all()
    print(choices)
    # Construct a dictionary containing all fields of the question object
    question_data = {
        'id': question.id,
        'text': question.text,
        'type': question.type,
        'choices': [{'id': choice.id, 'text': choice.text} for choice in choices] if question.type == 'MCQ' else [],
        'image': question.image, 
        # Add more fields here if needed
    }

    return render(request, 'quiz_system/question_page.html', {'question': question_data})

@admin_required
def index_admin(request):
    # Your view logic goes here
    live_feed_data = get_live_feed_data()
    rounds, ongoing_round = get_registered_rounds()
    # print(live_feed_data)
    return render(request, 'quiz_system/competition_control_admin.html', {'live_feed_data': live_feed_data, 'rounds': rounds, 'ongoing_round': ongoing_round})





from django.contrib.auth.signals import user_logged_in
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# channel specific things
def user_logged_in_handler(sender, request, user, **kwargs):
    channel_layer = get_channel_layer()
    message = f"User {user.username} logged in"
    async_to_sync(channel_layer.group_send)('admin_group', {'type': 'notify_admins', 'message': message})

user_logged_in.connect(user_logged_in_handler)


