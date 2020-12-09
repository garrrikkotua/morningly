from django.db import models
from django.utils import timezone
from tinymce.models import HTMLField
from news_generator import ArticleRenderer
import uuid
from django.urls import reverse
from django.utils.crypto import get_random_string


def default_random_string():
    return get_random_string(length=15)


class Subscription(models.Model):
    email = models.EmailField(primary_key=True)
    date_joined = models.DateTimeField(default=timezone.now)
    subscribed_to_daily = models.BooleanField(default=True)
    people_referred_count = models.IntegerField(default=0)
    email_confirmed = models.BooleanField(default=False)
    conf_string = models.CharField(max_length=15, default=default_random_string, editable=False, unique=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)

    def unsubscribe_url(self):
        return reverse('unsubscribe', kwargs={'unique_id': self.unique_id})

    def confirm_email_url(self):
        return reverse('confirm-email', kwargs={'slug': self.conf_string})


class Writer(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField()
    link = models.URLField()

    class Meta:
        ordering = ['email']

    @property
    def name(self):
        return self.first_name + ' ' + self.last_name

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name)


class Article(models.Model):
    IN_PROGRESS = 'PG'
    PUBLISHED = 'PB'
    NOT_APPROVED = 'NA'
    STATUS_LIST = [
        (IN_PROGRESS, 'В прогрессе'),
        (PUBLISHED, 'Опубликовано'),
        (NOT_APPROVED, 'Не одобрено к публикации'),
    ]
    pub_date = models.DateField(unique=True)
    headline = models.CharField(max_length=200)
    intro_html = HTMLField()
    market_html = HTMLField()
    writers = models.ManyToManyField(Writer)
    status = models.CharField(
        max_length=2,
        choices=STATUS_LIST,
        default=IN_PROGRESS,
    )
    path = models.CharField(max_length=200)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return '{} : {}'.format(self.pub_date, self.headline)

    def preview_article(self):
        renderer = ArticleRenderer(
            pub_date=self.pub_date,
            intro_html=self.intro_html,
            market_html=self.market_html,
            writers=list(self.writers.all()))
        renderer.add_all_posts(self.post_set.all())
        path = renderer.render_article()
        return path


class Post(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    position_in_article = models.IntegerField()
    header = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    image_link = models.URLField(blank=True)
    image_alt = models.CharField(max_length=50, blank=True)
    caption = models.CharField(max_length=50, blank=True)
    html_text = HTMLField()

    class Meta:
        ordering = ['position_in_article']

    def __str__(self):
        return '{} : {}'.format(self.header, self.title)
