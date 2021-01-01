from django.http import HttpResponse
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
import datetime
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.views.generic.list import ListView
from django.db.models import Q

from .forms import SubscriptionForm
from .models import Subscription, Article, Post
from .settings import DEFAULT_FROM_EMAIL


# показываем статью по дате
def show_article(request, day, month, year):
    date = datetime.date(year, month, day)
    article = get_object_or_404(Article, pub_date=date, status=Article.PUBLISHED)
    return render(request, 'skeleton.html', {'article_path': article.path, 'email_topic': article.headline[2:]})


# показываем самую последнюю статью
def show_latest(request):
    article = Article.objects.filter(pub_date__isnull=False, status=Article.PUBLISHED).latest('pub_date')
    return render(request, 'skeleton.html', {'article_path': article.path, 'email_topic': article.headline[2:]})


# подписываемся на основную рассылку
def subscribe(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SubscriptionForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if Subscription.objects.filter(email=form.cleaned_data['email']).exists():
                messages.warning(request, 'Вы уже подписались на рассылку')
                return render(request, 'subscribe.html', {'form': form})
            user = Subscription(email=form.cleaned_data['email'])
            user.save()
            # формируем приветсвенное письмо
            subject = '☀️ Подтвердите email'
            html_message = render_to_string('emails/confirm_email.html',
                                            {'uuid': user.unique_id, 'slug': user.conf_string,
                                             'request': request})
            plain_message = strip_tags(html_message)
            from_email = DEFAULT_FROM_EMAIL
            to = user.email
            # отправляем email
            mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)

            # отправили на страницу спасибо
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SubscriptionForm()

    return render(request, 'subscribe.html', {'form': form})


def unsubscribe(request, uuid):
    if request.method == "GET":
        user = get_object_or_404(Subscription, unique_id=uuid)
        return render(request, 'unsubscribe.html', {'email': user.email})
    if request.method == "POST":
        user = get_object_or_404(Subscription, unique_id=uuid)
        email = user.email
        user.delete()
        messages.success(request, 'Вы успешно отписались от рассылки Morningly')
        return render(request, 'unsubscribe.html', {'email': email})


def confirm_email(request, slug):
    user = get_object_or_404(Subscription, conf_string=slug)
    user.email_confirmed = True
    user.save()
    return render(request, 'email_confirmed.html')


def thanks_for_subscribing(request):
    return render(request, 'thanks_for_subscribing.html', {'subscribers_count': Subscription.objects.count()})


def privacy(request):
    return render(request, "privacy.html")


def responsibility(request):
    return render(request, "responsibility.html")


def contacts(request):
    return render(request, "contacts.html")


class ArchiveView(ListView):

    model = Article
    template_name = 'archive.html'
    ordering = ['-pub_date']

    def get_queryset(self):  # new
        query = self.request.GET.get('q')
        if query:
            return Article.objects.filter(
                (Q(headline__icontains=query.lower()) | Q(intro_html__icontains=query.lower())) & (Q(status=Article.PUBLISHED))
            )
        return Article.objects.order_by('-pub_date')[:10]
