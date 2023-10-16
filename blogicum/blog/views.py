import datetime as dt
from django import http

from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from typing import Any
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm
)
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.views.generic.edit import (
    CreateView, UpdateView, DeleteView
)
from django.views.generic.detail import DetailView
from . import constant
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
    template = 'blog/user.html'
    instance = get_object_or_404(User, username=request.user)
    form = ProfileForm(request.POST or None, instance=instance)
    if request.user == instance:
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user)
        else:
            print(form.errors.as_data())
    else:
        return redirect('pages:403csrf')
    context = {'form': form}

    return render(request, template, context)


# ------- Post Views -------
def post_detail(request, id):
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
            ),
            pk=id
        )
    else:
        post = get_object_or_404(
            Post.objects.filter(
                pub_date__lt=timezone.now(),
                is_published=True,
                category__is_published=True
            ),
            pk=id
        )
    comments = Comment.objects.filter(
        post=post,
        created_at__lt=timezone.now()
    )
    form = CommentForm(data=request.POST or None)
    context = {
        'form': form,
        'post': post,
        'comments': comments,
    }
    return render(request, template, context)


@login_required
def add_post(request):
    template = 'blog/create.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = request.user
        instance.save()
        return redirect('blog:profile', username=request.user)
    context = {'form': form}
    return render(request, template, context)


def edit_post(request, post_id):
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
    template = 'blog/create.html'
    instance = get_object_or_404(
        Post, id=post_id, author=request.user
    )
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:index')
    # context = {'form': form}
    return render(request, template)


# ------- Comment Views -------
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'

    def form_valid(self, form, **kwargs):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'id': post_id})


# @login_required
# def add_comment(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#     template = 'includes/comments.html'
#     form = CommentForm(data=request.POST or None)
#     if form.is_valid():
#         form.instance.author = request.user
#         form.instance.post = post
#         form.save()
#         return redirect('blog:post_detail', id=post_id)
#     context = {'form': form}
#     return render(request, template, context)


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'id': post_id})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'
    success_url = reverse_lazy('blog:index')

    def dispatch(self, request, *args: Any, **kwargs: Any) -> HttpResponse:
        instance = get_object_or_404(Comment, pk=kwargs['pk'])
        if instance.author != request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        post_id = self.kwargs['post_id']
        return reverse_lazy('blog:post_detail', kwargs={'id': post_id})

# @login_required
# def delete_comment(request, post_id, comment_id):
#     template = 'blog/comment.html'
#     post = Post.objects.get(pk=post_id)
#     instance = get_object_or_404(
#         Comment, post=post, pk=comment_id, author=request.user
#     )
#     if request.method == 'POST':
#         instance.delete()
#         return redirect('blog:post_detail', id=post_id)
#     return render(request, template)

# class PostCreateView(CreateView):
#     model = Post
#     fields = [
#         'title', 'text', 'pub_date', 'author', 'location', 'category', 'image'
#     ]
#     template_name = 'blog/create.html'
#     success_url = reverse_lazy('blog:index')


# class PostUpdateView(UpdateView):
#     model = Post
#     fields = '__all__'
#     template_name = 'blog/create.html'
#     pk_url_kwarg = 'post_id'

#     def get_success_url(self):
#         post_id = self.kwargs['post_id']
#         return reverse_lazy('blog:post_detail', kwargs={'id': post_id})


# class PostDeleteView(DeleteView):
#     model = Post
#     pk_url_kwarg = 'post_id'
#     template_name = 'blog/create.html'
#     success_url = reverse_lazy('blog:index')


# class UserDetailView(DetailView):
#     model = User
#     slug_url_kwarg = 'username'
#     slug_field = 'username'
#     template_name = 'blog/profile.html'

#     def get_context_data(self, **kwargs):
#         context = super(UserDetailView, self).get_context_data(**kwargs)
#         context['page_obj'] = Post.objects.select_related(
#             'category', 'location', 'author',
#         ).filter(
#             pub_date__lt=dt.datetime.now(),
#             is_published=True,
#             category__is_published=True,
#         ).order_by('id')
#         context['profile'] = self.object
#         return context


# class CommentCreateView(CreateView):
#     model = Comment
#     fields = ['text']
#     template_name = 'blog/comment.html'
#     success_url = reverse_lazy('blog:index')

#     def form_valid(self, form, **kwargs):
#         self.object = form.save(commit=False)
#         self.object.author = self.request.user
#         post_id = self.kwargs.get('post_id')
#         self.object.post = Post.objects.get(pk=post_id)

#         return super(CommentCreateView, self).form_valid(form)


# class CommentUpdateView(UpdateView):
#     model = Comment
#     fields = ['text']
#     pk_url_kwarg = 'comment_id'
#     template_name = 'blog/comment.html'

#     def get_object(self, queryset=None):
#         comment_id = self.kwargs.get('comment_id')
#         post_id = self.kwargs.get('post_id')
#         return self.model.objects.get(pk=comment_id, post_id=post_id)

#     def get_success_url(self):
#         post_id = self.kwargs['post_id']
#         return reverse_lazy('blog:post_detail', kwargs={'id': post_id})


# class CommentDeleteView(DeleteView):
#     model = Comment
#     template_name = 'blog/comment.html'

#     def get_object(self, queryset=None):
#         comment_id = self.kwargs.get('comment_id')
#         post_id = self.kwargs.get('post_id')
#         return self.model.objects.get(pk=comment_id, post_id=post_id)

#     def get_success_url(self):
#         post_id = self.kwargs['post_id']
#         return reverse_lazy('blog:post_detail', kwargs={'id': post_id})
