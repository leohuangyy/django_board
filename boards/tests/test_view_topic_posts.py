from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import resolve,reverse

from ..models import Board,Post,Topic
from ..views import topic_posts


class TopicPostsTests(TestCase):
	def setUp(self):
		board = Board.objects.create(name='Django',description='Django board')
		user = User.objects.create(username='leo',email='leo.huangyy@qq.com',password='123')
		topic = Topic.objects.create(subject='Hello world',board=board,starter=user)
		Post.objects.create(message='decorator and ',topic=topic,created_by=user)
		url = reverse('topic_posts',kwargs={'pk':board.pk,'topic_pk':topic.pk})
		self.response = self.client.get(url)

	def test_status_code(self):
		self.assertEqual(self.response.status_code,200)

	def test_view_function(self):
		view = resolve('/boards/1/topics/100/')
		self.assertEqual(view.func,topic_posts)