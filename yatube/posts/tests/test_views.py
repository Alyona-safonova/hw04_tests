from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
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
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_posts", kwargs={"slug": self.group.slug}
            ): "posts/group_list.html",
            reverse(
                "posts:profile", kwargs={"username": self.post.author}
            ): "posts/profile.html",
            reverse(
                "posts:post_detail", kwargs={"post_id": self.post.id}
            ): "posts/post_detail.html",
            reverse(
                "posts:post_edit", kwargs={"post_id": self.post.id}
            ): "posts/create_post.html",
            reverse("posts:post_create"): "posts/create_post.html",
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_view_context_page(self):
        post = Post.objects.all()
        pages_list = (
            reverse("posts:index"),
            reverse("posts:group_posts", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.post.author})
        )
        for reverse_name in pages_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    response.context['page_obj'][0].text,
                    post.get(id=response.context['page_obj'][0].id).text
                )

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_detail", kwargs={"post_id": self.post.id})
        )
        self.assertEqual(response.context.get("post").text, self.post.text)
        self.assertEqual(response.context.get("post").author, self.post.author)
        self.assertEqual(response.context.get("post").group, self.post.group)

    def test_create_edit_show_correct_context(self):
        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={"post_id": self.post.id})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_show_correct_context(self):
        response = self.authorized_client.get(reverse("posts:post_create"))
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_in_pages(self):
        group_id = PostPagesTests.group.id
        pages = (
            reverse("posts:index"),
            reverse("posts:group_posts", kwargs={'slug': 'test-slug'}),
            reverse("posts:profile", kwargs={'username': 'auth'})
        )
        for page in pages:
            response = self.authorized_client.get(page)
            post = response.context['page_obj'][0]
            post_text = post.text
            post_author = post.author
            post_group = post.group
            self.assertEqual(post_text, 'Тестовый пост')
            self.assertEqual(post_author.username, 'auth')
            self.assertEqual(post_group.id, group_id)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        for i in range(1, 15):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост {i}',
                group=cls.group
            )

    def setUp(self):
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        response = self.author.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.author.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 4)
