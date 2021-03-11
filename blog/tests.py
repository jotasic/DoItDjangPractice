from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category
from django.contrib.auth.models import User
# Create your tests here.


class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create(
            username="trump", password="something")
        self.user_ohbama = User.objects.create(
            username="ohbama", password="something")

        self.category_programming = Category.objects.create(
            name='programming', slug='programming')
        self.category_music = Category.objects.create(
            name='music', slug='music')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트 입니다.', content='Hello Django', author=self.user_trump, category=self.category_programming)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트 입니다.', content='Good Bye Django', author=self.user_ohbama, category=self.category_music)

        self.post_003 = Post.objects.create(
            title='세 번째 포스트 입니다.', content='Good morning Django', author=self.user_ohbama)



    def test_post_list(self):

        self.assertEqual(Post.objects.count(), 3)

        reponse = self.client.get('/blog/')
        self.assertEqual(reponse.status_code, 200)
        soup = BeautifulSoup(reponse.content, 'html.parser')
        
        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_ohbama.username.upper(), main_area.text)

        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        reponse = self.client.get('/blog/')
        soup = BeautifulSoup(reponse.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):
        # 1.1 포스트가 하나 있다. => setup 포스트에서 생성하도록 변경
        # post_001 = Post.objects.create(
        #     title='첫번째 포스트', content='첫번째 포스트 입니다', author=self.user_trump)
        # 1.2 그 포스트의 url은 /blog/1/ 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')
        # 2.1 첫번째 포스트의 url로 접근하면 정상적으로 작동한다(status code : 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 2.2 포스트 목록 페이지와 똑같은 네비게이션 바가 있다.
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 타이틀에 있다.
        self.assertIn(self.post_001.title, soup.title.text)

        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)

        # 2.5 첫 번째 포스트의 작성자가 포스트 영역에 있다
        # 아직 작성 불가

        # 2.6 첫 번째 포스트 내용이 포스트 영역 안에 있다.
        self.assertIn(self.post_001.content, post_area.text)

        self.assertIn(self.user_trump.username.upper(), post_area.text)


    def test_Category_page(self) :
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, "html.parser")
        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.h1.text)
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)


        

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        log_btn = navbar.find('a', text='My Home Page')
        self.assertIn(log_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertIn(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertIn(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertIn(about_me_btn.attrs['href'], '/about_me/')



    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(
            f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(
            f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)