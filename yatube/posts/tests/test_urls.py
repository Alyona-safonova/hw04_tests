from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Post, Group, User



class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user1 = User.objects.create_user(username ='leo')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user1,
            text='Тестовый пост'
        )
        cls.templates = [
            "/",
            f"/group/{cls.group.slug}/",
            f"/profile/{cls.user}/",
            f"/posts/{cls.post.id}/",
        ]
        cls.templates_url_names = {
            "/": "posts/index.html",
            f"/group/{cls.group.slug}/": "posts/group_list.html",
            f"/profile/{cls.user.username}/": "posts/profile.html",
            f"/posts/{cls.post.id}/": "posts/post_detail.html",
            f"/posts/{cls.post.id}/edit/": "posts/create_post.html",
            "/create/": "posts/create_post.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author = Client()
        self.author.force_login(self.user1)
    
    def test_exists_at_desired_location(self):
        """Тестируем страницы доступные всем."""
        for address in self.templates:
            with self.subTest(address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, 200)
    
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.author.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_unexisting_page(self):
        """Страница /unexisting_page/ должна выдать ошибку."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_create_url_redirect_anonymous_on_auth_login(self):
        """Страница /create/ не доступна неавторизованному пользователю."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_post_edit_url_redirect_anonymous_on_auth_login(self):
        """Страница /edit/ не доступна неавторизованному пользователю."""
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_post_create_authorized_client(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_post_edit_for_author(self):
        """Страница /edit/ доступна только автору."""
        response = self.author.get(f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_edit_for_authorized_client(self):
        """проверяем, что не автор поста (даже если это залогиненный пользователь) не может редактировать пост (происходит редирект)."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/', follow=True)
        self.assertRedirects(response, f'/posts/{self.post.id}/')