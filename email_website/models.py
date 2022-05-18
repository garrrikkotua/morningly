from django.db import models
from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.utils import timezone
from tinymce.models import HTMLField
from news_generator import ArticleRenderer, finance
import uuid
from django.urls import reverse
from django.utils.crypto import get_random_string
import requests
from .settings import DEFAULT_FROM_EMAIL, ANYMAIL
from django.core.mail import EmailMessage
from django.core.validators import MinValueValidator
from email.utils import format_datetime
from datetime import datetime
from unidecode import unidecode
from django.utils.text import slugify
from time import sleep


def default_random_string():
    """Random string for unique_id"""
    return get_random_string(length=15)


def batch(iterable, n=1):
    """Batch for sending emails"""
    length = len(iterable)
    for ndx in range(0, length, n):
        yield iterable[ndx:min(ndx + n, length)]


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

    @property
    def ready_for_sending(self):
        return self.subscribed_to_daily and self.email_confirmed

    @staticmethod
    def full_unsubscribe_url(unique_id):
        domain = Site.objects.get_current().domain
        return '{domain}{path}'.format(
            domain=domain,
            path=reverse('unsubscribe', kwargs={'uuid': unique_id})
        )


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
        (IN_PROGRESS, 'In progress'),
        (PUBLISHED, 'Published'),
        (NOT_APPROVED, 'Not approved for publishing'),
    ]
    pub_date = models.DateField(
        unique=True,
        help_text='Data of publication. Showing in the upper left corner of the email'
    )
    headline = models.CharField(
        max_length=200,
        help_text='Artilce name. Also the email subject',
    )
    intro_html = HTMLField(
        help_text='Intro texy'
    )
    show_market = models.BooleanField(
        default=True,
        help_text='To add market information or not'
    )

    market_data = HTMLField(
        blank=True,
        help_text='Market info'
    )

    market_html = HTMLField(
        blank=True,
        help_text='Text about market situation'
    )

    writers = models.ManyToManyField(
        Writer,
        help_text="Article's authors"
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_LIST,
        default=IN_PROGRESS,
        help_text="Article's status. Only admin can change it."
    )
    path = models.CharField(max_length=200)
    sending_time = models.DateTimeField(default=datetime(1970, 1, 1), validators=[MinValueValidator(datetime.now)])

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return '{} : {}'.format(self.pub_date, self.headline)

    def render_as_string(self, market_update=True):
        self.save()
        renderer = ArticleRenderer(article=self, market_update=market_update)
        string = renderer.render_as_string()
        self.path = renderer.create_path()
        return string

    def article_url(self):
        domain = Site.objects.get_current().domain
        return '{domain}{path}'.format(
            domain=domain,
            path=reverse('show-article', kwargs={
                'day': self.pub_date.day,
                'month': self.pub_date.month,
                'year': self.pub_date.year,
            })
        )

    @staticmethod
    def subscribe_url():
        return '{domain}'.format(domain=Site.objects.get_current().domain)

    def fetch_last_market_data(self):
        self.market_data = ArticleRenderer.render_market(self)
        self.save()

    def send_article(self, right_now=False):
        if self.status != Article.PUBLISHED:
            raise KeyError("article is not publihsed, you can't send it")

        self.add_template()  # добавили template в mailgun
        recipients = Subscription.objects.filter(
            models.Q(email_confirmed=True)
            &
            models.Q(subscribed_to_daily=True)
        ).values_list('email', 'unique_id')

        for x in batch(recipients, 50):
            message = EmailMessage(
                subject=self.headline,
                from_email=DEFAULT_FROM_EMAIL,
                to=[i[0] for i in x],
            )

            message.template_id = str(self.id)
            message.merge_data = {
                i[0]: {'unsubscribe_url': Subscription.full_unsubscribe_url(i[1])} for i in x
            }
            if not right_now:
                message.esp_extra = {
                    'o:deliverytime': format_datetime(self.sending_time),
                    'o:tag': ['Newsletter', str(self.pub_date)],
                }
            else:
                message.esp_extra = {
                    'o:tag': ['Newsletter', str(self.pub_date)],
                }
            message.send()

    def add_template(self):
        template = self.render_as_string()

        requests.delete(
            "{}/{}/templates/{}".format(
                ANYMAIL['MAILGUN_API_URL'], ANYMAIL["MAILGUN_SENDER_DOMAIN"], str(self.id),
            ),
            auth=("api", ANYMAIL["MAILGUN_API_KEY"]),
        )  # удаляем старый template, если есть

        return requests.post(
            "{}/{}/templates".format(
                ANYMAIL['MAILGUN_API_URL'], ANYMAIL["MAILGUN_SENDER_DOMAIN"]
            ),
            auth=("api", ANYMAIL["MAILGUN_API_KEY"]),
            data={'template': template,
                  'name': str(self.id),
                  'description': '{} : {}'.format(self.pub_date, self.headline[2:])}
        )


class Post(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    post_online = models.BooleanField(null=True, blank=True,
                                      help_text='To publish article online or not')
    position_in_article = models.IntegerField(
        help_text='Positional number of the article in the newsletter'
    )
    slug = models.SlugField(blank=True)
    header = models.CharField(
        max_length=100,
        help_text='Name of the srection'
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text='Name of the article'
    )
    image_link = models.URLField(
        blank=True,
        help_text='Link to the picture or gif'
    )
    image_alt = models.CharField(
        max_length=50,
        blank=True,
        help_text='This text will be showed if image failed to load'
    )
    caption = models.CharField(
        max_length=50,
        blank=True,
        help_text='Image caption'
    )
    html_text = HTMLField(
        help_text='Text of the article'
    )

    def create_slug(self):
        return slugify(unidecode(self.header + " " + self.title))

    def save(self, *args, **kwargs):
        if self.title != '' and self.title is not None:
            self.post_online = True
            self.slug = self.create_slug()
        else:
            self.post_online = False
        super(Post, self).save(*args, **kwargs)

    class Meta:
        ordering = ['position_in_article']

    def __str__(self):
        return str(self.article.pub_date) + ": " + self.header + ": " + self.title
