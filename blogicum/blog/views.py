from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .forms import CommentForm
from .models import Category, Comment, Post

User = get_user_model()
POSTS_PER_PAGE = 10


def get_posts_queryset():
    return (
        Post.objects.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
        .select_related("category", "location", "author")
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )


def index(request):
    post_list = get_posts_queryset()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_published = (
        post.is_published
        and post.pub_date <= timezone.now()
        and post.category
        and post.category.is_published
    )
    if not is_published:
        if request.user != post.author:
            from django.http import Http404

            raise Http404("Post not found")
    form = CommentForm()
    comments = Comment.objects.filter(post=post).select_related("author")
    return render(
        request,
        "blog/detail.html",
        {"post": post, "form": form, "comments": comments}
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    post_list = get_posts_queryset().filter(category=category)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj}
    )
