import datetime as dt
from typing import Any
from django.db import models

from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404
from django.utils import timezone

from . import constant
from blog.models import (
    Post, Category, Comment
)

User = get_user_model()


def index(request):
    template = 'blog/index.html'
    post_list = Post.objects.select_related(
        'category', 'location', 'author',
    ).filter(
        pub_date__lt=dt.datetime.now(),
        is_published=True,
        category__is_published=True,
    ).order_by('-pub_date')

    paginator = Paginator(post_list, constant.CARDS_LIMIT_FOR_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'

    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )

    post_list = Post.objects.select_related(
        'category', 'location', 'author'
    ).filter(
        pub_date__lt=dt.datetime.now(),
        category=category,
        is_published=True,
    )

    context = {
        'post_list': post_list,
        'category': category
    }
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'

    post = get_object_or_404(
        Post.objects.filter(
            pub_date__lt=dt.datetime.now(),
            is_published=True,
            category__is_published=True
        ),
        pk=id
    )
    comments = Comment.objects.filter(
        post=post,
        created_at__lt=dt.datetime.now()
    )

    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, template, context)


# ------- Post Views -------
class PostListView(ListView):
    model = Post
    queryset = Post.objects.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )
    paginate_by = 10
    ordering = 'pub_date'
    template_name = 'blog/index.html'


class PostCreateView(CreateView):
    model = Post
    fields = [
        'title', 'text', 'pub_date', 'author', 'location', 'category', 'image'
    ]
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class PostUpdateView(UpdateView):
    model = Post
    fields = '__all__'
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'id': post_id})


# class PostDetailView(DetailView):
#     model = Post
#     template_name = 'blog/detail.html'
#     pk_url_kwarg = 'id'
#     context_object_name = 'post'

#     def get_context_data(self, **kwargs):
#         context = super(PostDetailView, self).get_context_data(**kwargs)
#         context['comments'] = Comment.objects.filter(
#             post_id=self.kwargs.get('post_id')
#         )
#         return context

#     def get_object(self, queryset=None):
#         object = super().get_object()
#         if self.request.user != object.author and (
#             not object.is_published
#             or not object.category.is_published
#             or not object.pub_date <= timezone.now()
#         ):
#             raise Http404('Page not found')
#         return object


class PostDeleteView(DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class UserDetailView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        context['page_obj'] = Post.objects.select_related(
            'category', 'location', 'author',
        ).filter(
            pub_date__lt=dt.datetime.now(),
            is_published=True,
            category__is_published=True,
        ).order_by('id')
        context['profile'] = self.object
        return context


class CommentCreateView(CreateView):
    model = Comment
    fields = ['text']
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')

    def form_valid(self, form, **kwargs):
        self.object = form.save(commit=False)
        self.object.author = self.request.user
        post_id = self.kwargs.get('post_id')
        self.object.post = Post.objects.get(pk=post_id)

        return super(CommentCreateView, self).form_valid(form)


class CommentUpdateView(UpdateView):
    model = Comment
    fields = ['text']
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        post_id = self.kwargs.get('post_id')
        return self.model.objects.get(pk=comment_id, post_id=post_id)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'id': post_id})


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_object(self, queryset=None):
        comment_id = self.kwargs.get('comment_id')
        post_id = self.kwargs.get('post_id')
        return self.model.objects.get(pk=comment_id, post_id=post_id)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'id': post_id})
