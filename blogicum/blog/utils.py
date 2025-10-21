from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone

from .models import Post


def get_posts_queryset(
    manager=Post.objects, apply_filters=True, annotate_comments=True
):
    queryset = manager.select_related("category", "location", "author")

    if apply_filters:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now(),
        )

    if annotate_comments:
        queryset = queryset.annotate(comment_count=Count("comments"))

    return queryset.order_by("-pub_date")


def get_paginated_page(
    request, queryset, posts_per_page=settings.POSTS_PER_PAGE
):
    paginator = Paginator(queryset, posts_per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
