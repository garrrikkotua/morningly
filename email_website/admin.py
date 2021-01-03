from django.contrib import admin
from email_website.models import Subscription, Writer, Article, Post
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse, path
from django.utils.html import format_html
from email_website.forms import PrepareForSendingForm
from datetime import datetime
from django.utils import timezone
from django.shortcuts import render


class PostInline(admin.StackedInline):
    model = Post


class ArticleAdmin(admin.ModelAdmin):

    exclude = ('path', 'sending_time',)

    list_display = (
        'pub_date',
        'headline',
        'status',
        'prepare_for_sending',
    )

    inlines = [
        PostInline,
    ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('send/<int:article_id>', self.admin_site.admin_view(self.send_view),
                 name='prepare-for-sending')
        ]
        return custom_urls + urls

    def prepare_for_sending(self, obj):
        return format_html(
            '<a class="button" href="{}">Отправка</a>',
            reverse('admin:prepare-for-sending', kwargs={'article_id': obj.id})
        )
    prepare_for_sending.short_description = 'Подготовка к отправке'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser

        if not is_superuser:
            form.base_fields['status'].disabled = True

        return form

    def send_view(self, request, article_id, *args, **kwargs):
        article = self.get_object(request, article_id)

        if article.status != Article.PUBLISHED:
            self.message_user(request, 'Статья не опубликована. Её нельзя отправить')
            url = reverse(
                'admin:email_website_article_change',
                args=[article.id],
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(url)

        if request.method == "GET":
            form = PrepareForSendingForm()
        else:
            form = PrepareForSendingForm(request.POST)
            if form.is_valid():
                sending_time = form.cleaned_data['sending_time']
                sending_date = form.cleaned_data['sending_date']
                dt = datetime.combine(sending_date, sending_time)
                article.sending_time = timezone.make_aware(dt)
                article.save()
                article.send_article(right_now=form.cleaned_data['right_now'])  # отправляем request на mailgun
                self.message_user(request, 'Отправка успешно запланирована')
                url = reverse(
                    'admin:email_website_article_change',
                    args=[article.id],
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)

        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['article'] = article
        context['title'] = 'Запланировать отправку'

        return render(
            request,
            'admin/email_website/article/article_action.html',
            context,
        )

    def response_change(self, request, obj):
        if "preview" in request.POST:
            template_path = obj.preview_article()
            obj.path = template_path
            obj.save()
            return render(request, template_path)
        elif "publish" in request.POST:
            obj.status = Article.PUBLISHED
            template_path = obj.preview_article()
            obj.path = template_path
            obj.save()
            date = obj.pub_date
            return HttpResponseRedirect(reverse('show-article', kwargs={'day': date.day, 'month': date.month, 'year': date.year}))
        elif 'send_to_approve' in request.POST:
            obj.status = Article.NOT_APPROVED
            template_path = obj.preview_article()
            obj.path = template_path
            obj.save()
            html = '<h1>Успешно отправлено главному редактору на проверку</h1>'
            return HttpResponse(html)
        return super().response_change(request, obj)


admin.site.register(Subscription)
admin.site.register(Writer)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Post)
