# consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from django.utils import timezone
from .models import RoundInfo, Round, Team, User, Question, Choices
from datetime import timedelta

class AdminNotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'admin_group'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        await self.resolve_event(text_data)

    async def notify_admins(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'message': message}))

    async def resolve_event(self, event_text_data):
        data = json.loads(event_text_data)
        print(data)
        if data['type'] == 'roundStart' :
            await self.round_started({'message': 'RoundStarted'})
        elif data['type'] == 'roundEnd':
            stoptime = timezone.now()
            await sync_to_async(Round.objects.filter(state='Ongoing').update)(state='Completed', stop = stoptime)
            await self.round_end({'message': 'RoundEnded'})
        elif data['type'] == 'start_round':
            round = await sync_to_async(Round.objects.get)(pk=data['round_id'])
        

            if round:
                round.state = 'Ongoing'
                round.start = timezone.now()
                round.stop = timezone.now() + timedelta(minutes=round.duration)
                await sync_to_async(round.save)()
                event = {
                    'duration': round.duration,
                    'round_id': round.id
                }
                # await self.send(text_data=json.dumps({'type': 'round_time','duration': round.duration}))
                await self.round_started(event)
                print('Started', round)

        elif data['type'] == 'reset_rounds':
            await sync_to_async(Round.objects.all().update)(state='Inaccessible')
            await sync_to_async(RoundInfo.objects.all().delete)()
            await self.reset_rounds()
            print('Reset rounds')

    async def reset_rounds(self):
        await self.channel_layer.group_send(
            'non_admins',
            {
                'type': 'reset_round',
            }
        )

    async def round_end(self, event):
        
        # Broadcast the roundStarted event to all connected clients
        await self.channel_layer.group_send(
            'admin_group',
            {
                'type': 'round_end_event',
                'message': event
            }
        )

        await self.channel_layer.group_send(
            'non_admins',
            {
                'type': 'round_end_event',
                'message': event
            }
        )

    async def round_started(self, event):
        # start_time = timezone.now()

        # Broadcast the roundStarted event to all connected clients
        await self.channel_layer.group_send(
            'admin_group',
            {
                'type': 'round_started_event',
                'message': event
            }
        )

        await self.channel_layer.group_send(
            'non_admins',
            {
                'type': 'round_started_event',
                'message': event
            }
        )
        
    # Method to send roundStarted events to clients
    async def round_started_event(self, event):
        # Send the roundStarted event to the client
        await self.send(text_data=json.dumps(event))

    async def round_end_event(self, event):
        # Send the roundStarted event to the client
        await self.send(text_data=json.dumps(event))

    

    async def question_selected_event(self, event):
        # Send the roundStarted event to the client
        await self.send(text_data=json.dumps(event))

    async def choice_selected_event(self, event):
        await self.send(text_data=json.dumps(event))



class TeamNotificationsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        if not self.scope['user'].is_staff:
            await self.channel_layer.group_add('non_admins', self.channel_name)
        #     current_time = timezone.now()
        #     round_ = await sync_to_async(Round.objects.filter)(stop__gt=current_time)
        #     round1 = await sync_to_async(round_.first)()
        #     if round1:
        #        await self.send(text_data=json.dumps({'type': 'round', 'round_id': round1.id}))
        #     # else: 
        #     #     await self.send(text_data=json.dumps({'type':'no_running_round'}))

    async def disconnect(self, close_code):
        # Remove the user from the channel group when they disconnect
        await self.channel_layer.group_discard('non_admins', self.channel_name)

    async def receive(self, text_data):
        # Handle incoming messages, if needed
        print(text_data)
        await self.resolve_event(text_data)

    # Method to send messages to the non-admin channel group
    async def notify_non_admins(self, event):
        await self.send(text_data=json.dumps(event))

    # Method to send roundStarted events to clients
    async def round_started_event(self, event):
        # Send the roundStarted event to the client
        print(event)
        await self.send(text_data=json.dumps(event))
    
    async def reset_round(self, event):
        # Send round info data to the client
        await self.send(text_data=json.dumps(event))

    async def send_round_info(self, event):
        # Send round info data to the client
        await self.send(text_data=json.dumps(event))
        
    async def round_end_event(self, event):
        # Send the roundStarted event to the client
        await self.send(text_data=json.dumps(event))

    async def resolve_event(self, event_text_data):
        data = json.loads(event_text_data)
        print(data['type'])
        if data['type'] == 'QuestionSelected':
            # print(data['type'])
            await self.question_selected(data)
        elif data['type'] == 'QuestionAnswered':
            await self.question_answered(data)
        elif data['type'] == 'ChoiceSelected':
            await self.choice_selected(data)
        elif data['type'] == 'current_round':
            round = await sync_to_async(Round.objects.filter(state='Ongoing').first)()
            if not round:
                await self.send(text_data=json.dumps({'type':'no_running_round'}))
        elif data['type'] == 'AnswerFilled':
            await self.answer_filled(data)
        elif data['type'] == 'QuestionAnsweredSA':
            await self.question_answered_sa(data)


    async def question_selected_event(self, event):
        # Send the roundStarted event to the client
        await self.send(text_data=json.dumps(event))

    async def question_answered(self, event):
        if not event['round_id']:
            await self.send(text_data=json.dumps({'type':'no_running_round'}))
            return
        round_id = await sync_to_async(Round.objects.get)(pk=event['round_id'])
        if timezone.now() < round_id.stop:
            team_id = event['team_id']
            user = await sync_to_async(User.objects.get)(pk=team_id)
            team_id = await sync_to_async(Team.objects.get)(user=user)

            roundinfo = await sync_to_async(RoundInfo.objects.filter(round_id=round_id, team_id=team_id).order_by('-id').first)()

            # print(roundinfo)


            if roundinfo is not None:
                choice = await sync_to_async(Choices.objects.get)(pk=event['choice_id'])
                roundinfo.answer_selected_text = choice.text
                question_id = await sync_to_async(lambda: roundinfo.question_selected_id)()
                correct_answer = question_id.answer
                if correct_answer == roundinfo.answer_selected_text:
                    roundinfo.choice_is_correct_answer = True
                    roundinfo.marks_awarded = question_id.marks
                else:
                    roundinfo.choice_is_correct_answer = False
                    roundinfo.marks_awarded = 0

                await sync_to_async(roundinfo.save)()
                # question_id = await sync_to_async(roundinfo.choice_made_id.question_id)
                # correct_answer = await sync_to_async(Answers.objects.get)(
                #         question_id=question_id
                # )

                await self.send(text_data=json.dumps({'type':'answer', 'answer_text': correct_answer}))
            else:
                await self.send(text_data=json.dumps({'type':'no_running_round'}))

    async def question_answered_sa(self, event):
        if not event['round_id']:
            await self.send(text_data=json.dumps({'type':'no_running_round'}))
            return
        round_id = await sync_to_async(Round.objects.get)(pk=event['round_id'])
        if timezone.now() < round_id.stop:
            team_id = event['team_id']
            user = await sync_to_async(User.objects.get)(pk=team_id)
            team_id = await sync_to_async(Team.objects.get)(user=user)

            roundinfo = await sync_to_async(RoundInfo.objects.filter(round_id=round_id, team_id=team_id).order_by('-id').first)()

            # print(roundinfo)


            if roundinfo is not None:
                # choice = await sync_to_async(Choices.objects.get)(pk=event['choice_id'])
                roundinfo.answer_selected_text = event['answer_written']
                question_id = await sync_to_async(lambda: roundinfo.question_selected_id)()
                correct_answer = question_id.answer
                if correct_answer == roundinfo.answer_selected_text:
                    roundinfo.choice_is_correct_answer = True
                    roundinfo.marks_awarded = question_id.marks
                else:
                    roundinfo.choice_is_correct_answer = False
                    roundinfo.marks_awarded = 0

                await sync_to_async(roundinfo.save)()
                # question_id = await sync_to_async(roundinfo.choice_made_id.question_id)
                # correct_answer = await sync_to_async(Answers.objects.get)(
                #         question_id=question_id
                # )

                await self.send(text_data=json.dumps({'type':'answer_sa', 'answer_text': correct_answer}))
            else:
                await self.send(text_data=json.dumps({'type':'no_running_round'}))

    async def question_selected(self, event):
        if not event['round_id']:
            await self.send(text_data=json.dumps({'type':'no_running_round'}))
            return
        round_id = await sync_to_async(Round.objects.get)(pk=event['round_id'])
        if timezone.now() < round_id.stop:
            question_selected_id = await sync_to_async(Question.objects.get)(pk=event['question_selected_id'])
            team_id = event['team_id']
            user = await sync_to_async(User.objects.get)(pk=team_id)
            team_id = await sync_to_async(Team.objects.get)(user=user)
            if not team_id:
                team_id = await sync_to_async(Team.objects.create)(user=user)
            # Create a new RoundInfo object with the extracted details
            roundinfo = await sync_to_async(RoundInfo.objects.create)(
                round_id=round_id,
                team_id=team_id,
                question_selected_id=question_selected_id,
                answer_selected_text=None,  # Set choice_made_id to None initially
                choice_is_correct_answer=None,  # Set choice_is_correct_answer to None initially
                marks_awarded=None  # Set marks_awarded to None for now
            )
            print(user)
            print(roundinfo)
            print(event)
            event['question_selected_text'] = question_selected_id.text
            # event['question_duration'] = round_id.question_time
            # Broadcast the question selected event to all connected clients
            await self.send(json.dumps({'type': 'question_selected_event_success', 'message': {'question_id':event['question_selected_id'], 'question_time': round_id.question_time}}))
            await self.channel_layer.group_send(
                'admin_group',
                {
                    'type': 'question_selected_event',
                    'message': event
                }
            )

            await self.channel_layer.group_send(
                'non_admins',
                {
                    'type': 'question_selected_event',
                    'message': event
                }
            )

        else:
            await self.send(text_data=json.dumps({'type':'no_running_round'}))

    async def choice_selected(self, event):
        if not event['round_id']:
            await self.send(text_data=json.dumps({'type':'no_running_round'}))
            return
        round_id = await sync_to_async(Round.objects.get)(pk=event['round_id'])
        if timezone.now() < round_id.stop:
            choice_selected_id = await sync_to_async(Choices.objects.get)(pk=event['choice_id'])
            # team_id = event['team_id']
            # Create a new RoundInfo object with the extracted details
            
            event['choice_selected_text'] = choice_selected_id.text
            # Broadcast the question selected event to all connected clients
            await self.channel_layer.group_send(
                'admin_group',
                {
                    'type': 'choice_selected_event',
                    'message': event
                }
            )
        else:
            await self.send(text_data=json.dumps({'type':'no_running_round'}))

    async def answer_filled(self, event):
        if not event['round_id']:
            await self.send(text_data=json.dumps({'type':'no_running_round'}))
            return
        round_id = await sync_to_async(Round.objects.get)(pk=event['round_id'])
        if timezone.now() < round_id.stop:
            # choice_selected_id = await sync_to_async(Choices.objects.get)(pk=event['choice_id'])
            # team_id = event['team_id']
            # Create a new RoundInfo object with the extracted details
            
            event['choice_selected_text'] = event['answer_written']

            # Broadcast the question selected event to all connected clients
            await self.channel_layer.group_send(
                'admin_group',
                {
                    'type': 'choice_selected_event',
                    'message': event
                }
            )
        else:
            await self.send(text_data=json.dumps({'type':'no_running_round'}))
        