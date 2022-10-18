from tokenize import group
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Post, Group, User


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group1 = Group.objects.create(
            title='Изменяем текст',
            slug='test-slug1',
            description='Тестовое описание1'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )
        self.assertRedirects(
            response, reverse("posts:profile", kwargs={"username": self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.first())

    def test_post_edit(self):
        """Валидная форма изменяет запись в Post."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Изменяем текст",
            "group": self.group1.id,
            "author": self.user
        }
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs=({"post_id": self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.first())

    def test_post_edit_not_create_guest_client(self):
        """Валидная форма не изменит запись в Post если неавторизован."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Изменяем текст",
            "group": self.group1.id,
            "author": self.user
        }
        response = self.guest_client.post(
            reverse("posts:post_edit", kwargs=({"post_id": self.post.id})),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, f"/auth/login/?next=/posts/{self.post.id}/edit/"
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.first())

    def test_post_create_not_create_guest_client(self):
        """Валидная форма не создаст запись в Post если неавторизован."""
        posts_count = Post.objects.count()
        form_data = {
            "text": "Тестовая группа",
            "group": self.group.id,
            "author": self.user
        }
        response = self.guest_client.post(
            reverse("posts:post_create"),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, "/auth/login/?next=/create/"
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.first())
