from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import RoundInfo


@receiver(post_save, sender=RoundInfo)
def round_info_updated(sender, instance, **kwargs):
    # Prepare round info data
    round_info_data = {
        'round_id': instance.round_id,
        'team_id': instance.team_id,
        'question_selected_id': instance.question_selected_id,
        'choice_made_id': instance.choice_made_id,
        'choice_is_correct_answer': instance.choice_is_correct_answer,
        'marks_awarded': instance.marks_awarded
    }
    # Send round info data to all connected consumers
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)('non_admins', {
        'type': 'send_round_info',
        'message': round_info_data
    })
    async_to_sync(channel_layer.group_send)('admins', {
        'type': 'send_round_info',
        'message': round_info_data
    })