"""
    Файл настройки всех view приложения blog

    Проблемы: смесь FBV и CBV, по регламенту такого быть не должно,
        У меня не получилось, изначально все было сделано на FBV,
        но тесты не проходили сколько бы я не пытался.
"""
import datetime as dt
from typing import Any

from . import constant
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.utils import timezone
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView
)
from blog.models import (
    Post, Category, Comment
)
from .forms import PostForm, CommentForm, ProfileForm

User = get_user_model()


def index(request):
    """Главная страница проекта со всеми постами."""

    post_list = Post.objects.select_related(
        'category', 'location', 'author',
    ).filter(
        pub_date__lt=timezone.now(),
        is_published=True,
        category__is_published=True,
    ).order_by('-pub_date')

    paginator = Paginator(post_list, constant.CARDS_LIMIT_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    template = 'blog/index.html'
    context = {'page_obj': page_obj}
    return render(request, template, context)


def category_posts(request, category_slug):
    """Страница постов по категориям."""
    template = 'blog/category.html'

    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    posts = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        pub_date__lt=timezone.now(),
        category=category,
        is_published=True,
    ).order_by('-pub_date')

    paginator = Paginator(posts, constant.CARDS_LIMIT_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'category': category
    }
    return render(request, template, context)


# ------- User View -------
def user_profile(request, username):
    """Страница пользователя."""
    template = 'blog/profile.html'
    profile = get_object_or_404(User, username=username)

    if request.user == profile:
        posts = Post.objects.select_related(
            'category', 'location', 'author',
        ).filter(
            author=profile
        ).order_by('-pub_date')
    else:
        posts = Post.objects.select_related(
            'category', 'location', 'author',
        ).filter(
            pub_date__lt=dt.datetime.now(),
            is_published=True,
            category__is_published=True,
            author=profile
        ).order_by('-pub_date')
    paginator = Paginator(posts, constant.CARDS_LIMIT_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'profile': profile,
    }
    return render(request, template, context)


@login_required
def edit_profile(request):
    """Страница изменения профиля."""
    template = 'blog/user.html'
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('blog:profile', username=request.user)
    context = {'form': form}

    return render(request, template, context)


# ------- Post Views -------
def post_detail(request, id):
    """Страница поста."""
    template = 'blog/detail.html'

    if request.user.is_authenticated:
        post = get_object_or_404(
            Post.objects.filter(
                Q(author=request.user)
                | Q(
                    pub_date__lt=timezone.now(),
                    is_published=True,
                    category__is_published=True,
                )
            ).prefetch_related('comment_set'),
            pk=id
        )
    else:
        post = get_object_or_404(
            Post.objects.filter(
                pub_date__lt=timezone.now(),
                is_published=True,
                category__is_published=True
            ).prefetch_related('comment_set'),
            pk=id
        )

    comments = post.comment_set.all()

    form = CommentForm(data=request.POST or None)
    context = {
        'form': form,
        'post': post,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def add_post(request):
    """Страница добавления поста."""
    template = 'blog/create.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.pub_date = timezone.now()
        instance.save()
        return redirect('blog:profile', username=request.user)
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    """Страница редактирования поста."""
    template = 'blog/create.html'
    instance = get_object_or_404(
        Post, id=post_id
    )
    form = PostForm(request.POST or None, instance=instance)
    if request.user == instance.author:
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', id=post_id)
    else:
        return redirect('blog:post_detail', id=post_id)

    context = {'form': form}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    """Страница удаления поста"""
    template = 'blog/create.html'
    instance = get_object_or_404(
        Post, id=post_id, author=request.user
    )
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    return render(request, template)


# ------- Comment Views -------
class BaseCommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'id': post_id})


class ChangeCommentMixin(BaseCommentMixin):
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        instance = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class CommentCreateView(LoginRequiredMixin, BaseCommentMixin, CreateView):
    """Страница создания комментария."""
    def form_valid(self, form, **kwargs):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)


class CommentUpdateView(LoginRequiredMixin, ChangeCommentMixin, UpdateView):
    """Страница редактирования комментария"""
    pass


class CommentDeleteView(LoginRequiredMixin, ChangeCommentMixin, DeleteView):
    """Страница удаления комментария"""
    pass
