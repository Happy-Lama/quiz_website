from django.test import TestCase
from .models import Question, Team, Choices, Answers, Round, RoundInfo
from django.utils import timezone
from django.contrib.auth.models import User

class QuestionModelTestCase(TestCase):
    def setUp(self):
        self.question = Question.objects.create(text="Sample question", type="MCQ")

    def test_question_text(self):
        self.assertEqual(self.question.text, "Sample question")

    def test_question_type(self):
        self.assertEqual(self.question.type, "MCQ")

class TeamModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="team_a", password="password123")
        self.team = Team.objects.create(user=self.user)

    def test_team_user(self):
        self.assertEqual(self.team.user, self.user)

class ChoicesModelTestCase(TestCase):
    def setUp(self):
        self.question = Question.objects.create(text="Sample question", type="MCQ")
        self.choice = Choices.objects.create(question_id=self.question, text="Choice 1")

    def test_choice_question(self):
        self.assertEqual(self.choice.question_id, self.question)

    def test_choice_text(self):
        self.assertEqual(self.choice.text, "Choice 1")

class AnswersModelTestCase(TestCase):
    def setUp(self):
        self.question = Question.objects.create(text="Sample question", type="MCQ")
        self.choice = Choices.objects.create(question_id=self.question, text="Choice 1")
        self.answer = Answers.objects.create(question_id=self.question, choice_id=self.choice, marks_awarded=1)

    def test_answer_question(self):
        self.assertEqual(self.answer.question_id, self.question)

    def test_answer_choice(self):
        self.assertEqual(self.answer.choice_id, self.choice)

    def test_answer_marks_awarded(self):
        self.assertEqual(self.answer.marks_awarded, 1)

class RoundModelTestCase(TestCase):
    def setUp(self):
        self.round = Round.objects.create(start=timezone.now(), stop=timezone.now())

    def test_round_start(self):
        self.assertIsNotNone(self.round.start)

    def test_round_stop(self):
        self.assertIsNotNone(self.round.stop)

# class RoundInfoModelTestCase(TestCase):
#     def setUp(self):
#         self.round = Round.objects.create(start=timezone.now(), stop=timezone.now())
#         self.team = Team.objects.create(username="Team A", password="password123")
#         self.question = Question.objects.create(text="Sample question", type="MCQ")
#         self.choice = Choices.objects.create(question_id=self.question, text="Choice 1")
#         self.round_info = RoundInfo.objects.create(round_id=self.round, team_id=self.team, question_selected_id=self.question, choice_made_id=self.choice, choice_is_correct_answer=True, marks_awarded=1)

#     def test_round_info_round(self):
#         self.assertEqual(self.round_info.round_id, self.round)

#     def test_round_info_team(self):
#         self.assertEqual(self.round_info.team_id, self.team)

#     def test_round_info_question_selected(self):
#         self.assertEqual(self.round_info.question_selected_id, self.question)

#     def test_round_info_choice_made(self):
#         self.assertEqual(self.round_info.choice_made_id, self.choice)

#     def test_round_info_choice_is_correct_answer(self):
#         self.assertTrue(self.round_info.choice_is_correct_answer)

#     def test_round_info_marks_awarded(self):
#         self.assertEqual(self.round_info.marks_awarded, 1)
        
class RoundInfoModelTestCase(TestCase):
    def setUp(self):
        self.round = Round.objects.create(start=timezone.now(), stop=timezone.now())
        self.user = User.objects.create_user(username="team_a", password="password123")
        self.team = Team.objects.create(user=self.user)
        self.question = Question.objects.create(text="Sample question", type="MCQ")
        self.choice = Choices.objects.create(question_id=self.question, text="Choice 1")
        self.round_info = RoundInfo.objects.create(round_id=self.round, team_id=self.team, question_selected_id=self.question, choice_made_id=self.choice, choice_is_correct_answer=True, marks_awarded=1)

    def test_round_info_round(self):
        self.assertEqual(self.round_info.round_id, self.round)

    def test_round_info_team(self):
        self.assertEqual(self.round_info.team_id, self.team)

    def test_round_info_question_selected(self):
        self.assertEqual(self.round_info.question_selected_id, self.question)

    def test_round_info_choice_made(self):
        self.assertEqual(self.round_info.choice_made_id, self.choice)

    def test_round_info_choice_is_correct_answer(self):
        self.assertTrue(self.round_info.choice_is_correct_answer)

    def test_round_info_marks_awarded(self):
        self.assertEqual(self.round_info.marks_awarded, 1)      


from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Question

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.admin = User.objects.create_superuser(username='adminuser', password='admin12345')
        self.question = Question.objects.create(text='Sample question', type='MCQ')

    def test_custom_login_view(self):
        response = self.client.post(reverse('login'), {'username': 'testuser', 'password': '12345'})
        self.assertEqual(response.status_code, 302)  # Redirects to home page upon successful login

    def test_index_view(self):
        # Test for non-admin user
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)  # Check if the home page is rendered for non-admin user

        # Test for admin user
        self.client.force_login(self.admin)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)  # Redirects to admin panel for admin user

    def test_leaderboard_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('leaderboard'))
        self.assertEqual(response.status_code, 200)  # Check if the leaderboard page is rendered

    def test_question_view(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('question_view', kwargs={'question_id': self.question.id}))
        self.assertEqual(response.status_code, 200)  # Check if the question page is rendered

    def test_index_admin_view(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('index_admin'))
        self.assertEqual(response.status_code, 200)  # Check if the admin page is rendered

    def test_questions_admin_view(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('questions_admin', kwargs={'question_id': self.question.id}))
        self.assertEqual(response.status_code, 200)  # Check if the question admin page is rendered
