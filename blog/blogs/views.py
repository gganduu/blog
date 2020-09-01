from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from blogs import models
from django.urls import reverse
from django.http.response import HttpResponseBadRequest
from utils.response_code import RETCODE
import logging
logger = logging.getLogger('blog')
# Create your views here.

class IndexView(View):
    def get(self, request):
        categories = models.Category.objects.all()
        cat_id = request.GET.get('cat_id', 1)
        category = models.Category.objects.get(id=cat_id)
        articles = models.Article.objects.filter(category=category)
        # split page related code
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 2)
        from django.core.paginator import Paginator
        paginator = Paginator(articles, per_page=page_size)
        try:
            page_articles = paginator.page(page_num)
        except Exception as e:
            logger.error(e)
            return HttpResponse('Empty Page')
        total_pages = paginator.num_pages

        context = {
            'categories': categories,
            'category': category,
            'page_articles': page_articles,
            'page_num': page_num,
            'page_size': page_size,
            'total_pages': total_pages,
        }
        return render(request, 'blogs/index.html', context)

class WriteBlog(LoginRequiredMixin, View):
    def get(self, request):
        categories = models.Category.objects.all()
        context = {'categories': categories}
        return render(request, 'blogs/write_blog.html', context)

    def post(self, request):
        image = request.FILES.get('avatar')
        title = request.POST.get('title')
        id = request.POST.get('category')
        tag = request.POST.get('tags')
        summary = request.POST.get('sumary')
        content = request.POST.get('content')
        if not all([title, id, tag, summary, content]):
            return HttpResponseBadRequest('code:'+str(RETCODE.NECESSARYPARAMERR))
        category = models.Category.objects.filter(id=id).first()
        if category is None:
            return HttpResponse('Wrong Category')
        try:
            article = models.Article.objects.create(
                title=title,
                category=category,
                tag=tag,
                summary=summary,
                content=content,
                image=image,
                author=request.user
            )
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('code:'+str(RETCODE.DATABASEERR))
        path = reverse('blogs:detail')+'?article_id={}'.format(article.id)
        return redirect(path)

class DetailView(View):
    def get(self, request):
        article_id = request.GET.get('article_id')
        try:
            article = models.Article.objects.get(id=article_id)
        except Exception as e:
            logger.error(e)
            return render(request, 'blogs/404.html')
        category = article.category
        try:
            categories = models.Category.objects.all()
            hot_articles = models.Article.objects.order_by('-num_viewed')[:3]
            # comments = models.Comment.objects.filter(article=article).order_by('-created_time')
            comments = article.comment_set.all().order_by('-created_time')
            num_comments = comments.count()
            # from django.db.models import Count
            # num_comments = models.Comment.objects.aggregate(Count('id')).get('id__count')
        except Exception as e:
            logger.error(e)
            return HttpResponse('Database operation failed')

        from django.core.paginator import Paginator
        page_num = request.GET.get('page_num', 1)
        page_size = request.GET.get('page_size', 2)
        paginator = Paginator(comments, per_page=page_size)
        try:
            page_comments = paginator.page(page_num)
        except Exception as e:
            logger.error(e)
            return HttpResponse('Empty Page')
        total_pages = paginator.num_pages
        # update num_viewed
        article.num_viewed += 1
        article.save()
        context = {
            'category': category,
            'categories': categories,
            'article': article,
            'page_num': page_num,
            'page_size': page_size,
            'total_pages': total_pages,
            'page_comments': page_comments,
            'num_comments': num_comments,
            'user': request.user,
            'hot_articles': hot_articles
        }
        return render(request, 'blogs/detail.html', context)

    def post(self, request):
        user = request.user
        if user and user.is_authenticated:
            content = request.POST.get('content')
            article_id = request.POST.get('article_id')
            try:
                article = models.Article.objects.get(id=article_id)
                models.Comment.objects.create(content=content, author=user, article=article)
            except Exception as e:
                logger.error(e)
                return HttpResponse('Database operation failed')
            article.num_comments += 1
            article.save()
            path = reverse('blogs:detail')+'?article_id={}'.format(article_id)
            return redirect(path)
        else:
            return redirect(reverse('user:login'))

# http://127.0.0.1:8000/detail/?article_id=62
# http://127.0.0.1:8000/?article_id=2&page_size=2&page_num=2
# http://127.0.0.1:8000/detail/?article_id=62&page_size=2&page_num=2