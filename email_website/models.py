from django.db import models
from django.contrib.sites.models import Site
from django.utils import timezone
from tinymce.models import HTMLField
from news_generator import ArticleRenderer
import uuid
from django.urls import reverse
from django.utils.crypto import get_random_string
import requests
from .settings import DEFAULT_FROM_EMAIL, ANYMAIL
from django.core.mail import EmailMessage
from django.core.validators import MinValueValidator
from email.utils import format_datetime
from datetime import datetime


def default_random_string():
    """Рандомная строка заданной длины для unique_id"""
    return get_random_string(length=15)


def batch(iterable, n=1):
    """Батч для отправки писем"""
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
        (IN_PROGRESS, 'В прогрессе'),
        (PUBLISHED, 'Опубликовано'),
        (NOT_APPROVED, 'Не одобрено к публикации'),
    ]
    pub_date = models.DateField(
        unique=True,
        help_text='Дата выхода выпуска. Она отображается в верхнем левом углу письма'
    )
    headline = models.CharField(
        max_length=200,
        help_text='Название выпуска. Оно же тема письма',
    )
    intro_html = HTMLField(
        help_text='Текст вступления'
    )
    show_market = models.BooleanField(
        default=True,
        help_text='Если галочка выключена, то рыночная информация не добавляется в статью, и market_html игнорируется.'
    )
    market_html = HTMLField(
        blank=True,
        help_text='Текст про ситуацию на рынке'
    )
    writers = models.ManyToManyField(
        Writer,
        help_text='Авторы выпуска'
    )
    status = models.CharField(
        max_length=2,
        choices=STATUS_LIST,
        default=IN_PROGRESS,
        help_text='Статус выпуска. Управляется только админом.'
    )
    path = models.CharField(max_length=200)
    sending_time = models.DateTimeField(default=datetime(1970, 1, 1), validators=[MinValueValidator(datetime.now)])

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return '{} : {}'.format(self.pub_date, self.headline)

    def preview_article(self):
        self.save()
        renderer = ArticleRenderer(article=self)
        path = renderer.render_article()
        return path

    def render_as_string(self):
        self.save()
        renderer = ArticleRenderer(article=self)
        string = renderer.render_as_string()
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

    def send_article(self, right_now=False):
        if self.status != Article.PUBLISHED:
            raise KeyError('статья не опубликована, её нельзя отправить')

        self.add_template()  # добавили template в mailgun
        recipients = Subscription.objects.filter(
            models.Q(email_confirmed=True)
            &
            models.Q(subscribed_to_daily=True)
        ).values_list('email', 'unique_id')

        for x in batch(recipients, 500):
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
                    'o:tag': ['Newsletter'],
                }
            else:
                message.esp_extra = {
                    'o:tag': ['Newsletter'],
                }
            message.send()

    def add_template(self):
        with open(self.path, 'r', encoding='utf-8') as f:
            template = f.read()

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
    position_in_article = models.IntegerField(
        help_text='Порядковыый номер статьи в выпуске'
    )
    header = models.CharField(
        max_length=100,
        help_text='Название раздела'
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text='Название статьи'
    )
    image_link = models.URLField(
        blank=True,
        help_text='Ссылка на картинку или gif'
    )
    image_alt = models.CharField(
        max_length=50,
        blank=True,
        help_text='Если картинка не загрузится, будет написан этот текст'
    )
    caption = models.CharField(
        max_length=50,
        blank=True,
        help_text='Подпись под картинкой'
    )
    html_text = HTMLField(
        help_text='Текст статьи'
    )

    class Meta:
        ordering = ['position_in_article']

    def __str__(self):
        return self.title
