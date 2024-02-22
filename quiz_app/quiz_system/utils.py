# utils.py
from django.utils import timezone
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from quiz_system.models import Team, Round, RoundInfo

def admin_required(view_func):
    """
    Decorator for views that checks if the user is an admin.
    """
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            # Redirect to a different page or return a 403 Forbidden response
            # You can customize this behavior based on your requirements
            return HttpResponseForbidden('You are not authorized to access this page.')
        return view_func(request, *args, **kwargs)
    return _wrapped_view




def get_live_feed_data():
    # Get all logged in users who are not staff members
    logged_in_users = User.objects.filter(is_staff=False, is_active=True)
    print("Logged in Users",logged_in_users)
    live_feed_data = []

    # Iterate over each logged in user
    for user in logged_in_users:
        try:
            # Get the team associated with the user
            team = Team.objects.get(user=user)

            # Get the last round
            last_round = Round.objects.filter(stop__lt=timezone.now()).last()

            # Check if the last round is finished
            if last_round and last_round.stop > timezone.now():
                # Get the round info associated with the last round for the team
                round_info = RoundInfo.objects.filter(round_id=last_round, team_id=team).last()

                if round_info:
                    # Construct the dictionary of live feed data
                    live_feed_entry = {
                        'team_id': team.user.id,
                        'name': team.user.username,
                        'question_selected_text': round_info.question_selected_id.text,
                        'answer_selected': round_info.choice_made_id.text
                    }
            else:
                live_feed_entry = {
                    'team_id': team.user.id,
                    'name': team.user.username,
                    'question_selected_text': '',
                    'answer_selected': ''
                }               
        
        except Team.DoesNotExist:
            team = Team.objects.create(user=user)
            live_feed_entry = {
                'team_id': team.user.id,
                'name': team.user.username,
                'question_selected_text': '',
                'answer_selected': ''
            }
        finally:
            live_feed_data.append(live_feed_entry)

    return live_feed_data



def get_registered_rounds():
    rounds = Round.objects.all()
    rounds_ = []
    ongoing_round_available = False
    for round in rounds:
        if round.state == 'Ongoing':
            ongoing_round_available = True
        rounds_.append(
            {
                'id': round.id,
                'name': round.round_name,
                'completed': round.state == 'Completed',
                'ongoing': round.state == 'Ongoing',
                # 'disabled': ongoing_round_available
            }
        )
    return rounds_, ongoing_round_available