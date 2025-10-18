from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .forms import CommentForm
from .models import Category, Post

User = get_user_model()


def get_posts_queryset(user=None):
    queryset = Post.objects.select_related(
        "category", "location", "author"
    ).annotate(comment_count=Count("comments"))

    if user is None or not user.is_authenticated:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )
    else:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )

    return queryset.order_by("-pub_date")


def index(request):
    post_list = get_posts_queryset(request.user)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("category", "location", "author"),
        id=post_id
    )

    is_visible = (
        post.is_published
        and post.pub_date <= timezone.now()
        and post.category
        and post.category.is_published
    )

    if not is_visible and request.user != post.author:
        post = get_object_or_404(get_posts_queryset(), id=post_id)

    form = CommentForm()
    comments = post.comments.select_related("author")  # type: ignore

    return render(
        request,
        "blog/detail.html",
        {"post": post, "form": form, "comments": comments}
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = get_posts_queryset(request.user).filter(category=category)
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj}
    )
