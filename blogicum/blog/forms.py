from django import forms
from .models import Comment, Post
from django.contrib.auth import get_user_model


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'title', 'text', 'pub_date',
            'location', 'category', 'image',
        ]
        widgets = {
            'pub_date': forms.DateInput(attrs={'type': 'date'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
