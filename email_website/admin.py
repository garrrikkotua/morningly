from django.contrib import admin
from email_website.models import Subscription, Writer, Article, Post
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse


class PostInline(admin.StackedInline):
    model = Post


class ArticleAdmin(admin.ModelAdmin):

    exclude = ('path', )

    inlines = [
        PostInline,
    ]

    def response_change(self, request, obj):
        if "preview" in request.POST:
            template_path = obj.preview_article()
            obj.path = template_path
            obj.save()
            return TemplateResponse(request, template_path)
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
            html = '<h1>Успешно отправлено редактору на проверку</h1>'
            return HttpResponse(html)
        return super().response_change(request, obj)


admin.site.register(Subscription)
admin.site.register(Writer)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Post)
