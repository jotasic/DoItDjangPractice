from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post, Category, Tag
from django.contrib.auth.models import User
# Create your tests here.


class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.user_trump = User.objects.create(
            username="trump", password="something")
        self.user_ohbama = User.objects.create(
            username="ohbama", password="something")

        self.user_trump.set_password("something")
        self.user_trump.save()


        self.user_ohbama.set_password("something")
        self.user_ohbama.is_staff = True
        self.user_ohbama.save()

        self.category_programming = Category.objects.create(
            name='programming', slug='programming')
        self.category_music = Category.objects.create(
            name='music', slug='music')


        self.tag_python_kor = Tag.objects.create(name="파이썬 공부", slug="파이썬 공부")
        self.tag_python = Tag.objects.create(name="python", slug="python")
        self.tag_hello = Tag.objects.create(name="hello", slug="hello")
        

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트 입니다.', content='Hello Django', author=self.user_trump, category=self.category_programming)

        self.post_001.tags.add(self.tag_hello)

        self.post_002 = Post.objects.create(
            title='두 번째 포스트 입니다.', content='Good Bye Django', author=self.user_ohbama, category=self.category_music)

        self.post_003 = Post.objects.create(
            title='세 번째 포스트 입니다.', content='Good morning Django', author=self.user_ohbama)

        self.post_003.tags.add(self.tag_python_kor)
        self.post_003.tags.add(self.tag_python)

    def test_update_post(self) :
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 로그인 하지 않은 경우
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인은 했지만 작성자가 아닌 경우
        self.assertNotEqual(self.post_003.author, self.user_trump)
        self.client.login(
            username = self.user_trump.username,
            password = 'something'
        )

        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 작성자가 접근하는 경우
        self.client.login(
            username = self.post_003.author.username,
            password = 'something'
        )

        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트를 수정했습니다.',
                'content': '안녕 세계? 우리는 하나!',
                'category': self.category_music.pk
            },
            follow=True
        )

        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트를 수정했습니다.', main_area.text)
        self.assertIn('안녕 세계? 우리는 하나!', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)
        


    def test_create_post(self):
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 User가 로그인을 한다.
        self.client.login(username="trump", password="something")
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 User가 로그인을 한다.
        self.client.login(username="ohbama", password="something")
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        self.client.post(
            '/blog/create_post/',
            {
                'title' : 'Post Form 만들기',
                'content' : 'Post Form 페이지를 만듭시다.',
                'tags_str' : 'new tag; 한글 태그, python'
            }
        )

        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()

        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, "ohbama")


        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertEqual(Tag.objects.count(), 5)
        



    def test_tage_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)
        
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.h1.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)





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
        self.assertIn(self.tag_hello.name, post_001_card.text)
        self.assertNotIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_hello.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_python_kor.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn('미분류', post_003_card.text)
        self.assertNotIn(self.tag_hello.name, post_003_card.text)
        self.assertIn(self.tag_python.name, post_003_card.text)
        self.assertIn(self.tag_python_kor.name, post_003_card.text)

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

        self.assertIn(self.tag_hello.name, post_area.text)
        self.assertNotIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_python_kor.name, post_area.text)
        


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