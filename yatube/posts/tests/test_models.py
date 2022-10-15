from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def test_title_label(self):
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст')

    def test_title_help_text(self):
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Введите текст поста')

    def test_model_have_correct_object_name(self):
        post = PostModelTest.post
        expected_object_name = post.text
        self.assertEqual(expected_object_name, str(post))

    def test_title_label(self):
        post = PostModelTest.post
        verbose = post._meta.get_field('group').verbose_name
        self.assertEqual(verbose, 'Группа')

    def test_title_help_text(self):
        post = PostModelTest.post
        help_text = post._meta.get_field('group').help_text
        self.assertEqual(help_text, 'Группа, к которой будет относиться пост')


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Текстовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_model_have_correct_object_name(self):
        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))
