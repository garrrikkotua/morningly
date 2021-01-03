from jinja2 import Environment, select_autoescape, FileSystemLoader
from pathlib import Path
import os
import humanize
from .finance import get_data


_t = humanize.i18n.activate("ru_RU")

BASE_DIR = Path(__file__).resolve().parent.parent

env = Environment(
    loader=FileSystemLoader(os.path.join(BASE_DIR, 'templates/jinja')),
    autoescape=select_autoescape(['html', 'xml'])
)


class ArticleRenderer:
    def __init__(self, **params):

        if 'article' in params:  # instantiating with models.Article
            article = params['article']
            self.date = article.pub_date
            self.intro_html = article.intro_html
            self.market_data = self.get_market_data()
            self.market_html = article.market_html
            self.show_market = article.show_market
            self.writers = list(article.writers.all())
            self.posts = article.post_set.all()
            self.article_url = article.article_url()
            self.subscribe_url = article.subscribe_url()

        else:
            self.date = params['pub_date']
            self.intro_html = params['intro_html']
            self.market_data = self.get_market_data()
            self.market_html = params['market_html']
            self.show_market = params['show_market']
            self.writers = params['writers']
            self.posts = []

    @staticmethod
    def get_market_data():
        return get_data().items()

    months = {'1': 'Января',
         '2': 'Февраля',
         '3': 'Марта',
         '4': 'Апреля',
         '5': 'Мая',
         '6': 'Июня',
         '7': 'Июля',
         '8': 'Августа',
         '9': 'Сентября',
         '10': 'Октября',
         '11': 'Ноября',
         '12': 'Декабря',
        }

    def human_date(self):
        date = self.date
        return str(date.day) + ' ' + self.months[str(date.month)] + ', ' + str(date.year)

    def create_path(self):
        date_str = '{}-{}-{}'.format(self.date.day, self.date.month, self.date.year)
        return os.path.join(BASE_DIR, 'templates/ready_articles/' + date_str)

    def add_post(self, post):
        self.posts.append(post)

    def add_all_posts(self, posts_array):
        self.posts = posts_array

    def pack_parameters(self):
        return dict(
            date=self.human_date(),
            intro_html=self.intro_html,
            market_data=self.market_data,
            market_html=self.market_html,
            show_market=self.show_market,
            authors=self.writers,
            posts=self.posts,
            article_url=self.article_url,
            subscribe_url=self.subscribe_url,
            unsubscribe_url='',
        )

    def render_article(self):
        path = self.create_path()
        template = env.get_template('news_template.html')
        params = self.pack_parameters()
        rendered_template = template.render(**params)
        Path(path).mkdir(parents=True, exist_ok=True)
        with open(path + '/news.html', 'w', encoding='utf-8') as f:
            f.write(rendered_template)
        return path + '/news.html'

    def render_as_string(self):
        path = self.create_path()
        template = env.get_template('news_template.html')
        params = self.pack_parameters()
        rendered_template = template.render(**params)
        Path(path).mkdir(parents=True, exist_ok=True)
        with open(path + '/news.html', 'w', encoding='utf-8') as f:
            f.write(rendered_template)
        return rendered_template

    def render_for_user(self, user):
        template = env.get_template('news_template.html')
        params = self.pack_parameters()
        params['unsubscribe_url'] = user.unsubscribe_url()
        return template.render(**params)

