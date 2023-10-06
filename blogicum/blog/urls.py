from django.urls import path

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    # ----------- Post paths -----------
    path(
        'posts/<int:id>/',
        views.post_detail,
        name='post_detail'
    ),
    path(
        'posts/create',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
    # ----------- Comment paths -----------
    path(
        'posts/<post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<post_id>/edit_comment/<comment_id>',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<post_id>/delete_comment/<comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    # ----------- User paths -----------
    path(
        'profile/<username>/',
        views.UserDetailView.as_view(),
        name='profile'
    )
]
