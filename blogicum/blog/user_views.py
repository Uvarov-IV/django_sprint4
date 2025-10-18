from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CommentForm, PostForm, UserForm
from .models import Comment, Post

User = get_user_model()


def get_posts_manager(
    manager=Post.objects,
    apply_filters=True,
    annotate_comments=True
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
    request,
    queryset,
    posts_per_page=settings.POSTS_PER_PAGE
):
    paginator = Paginator(queryset, posts_per_page)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    if request.user == profile_user:
        posts_query = get_posts_manager(
            manager=profile_user.posts,  # type: ignore
            apply_filters=False,
            annotate_comments=True
        )
    else:
        posts_query = get_posts_manager(
            manager=profile_user.posts,  # type: ignore
            apply_filters=True,
            annotate_comments=True
        )
    
    page_obj = get_paginated_page(request, posts_query)
    
    return render(
        request,
        "blog/profile.html",
        {"profile": profile_user, "page_obj": page_obj}
    )


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = PostForm()
    
    return render(request, "blog/create.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    
    if request.method == "POST":
        form = PostForm(
            request.POST or None,
            request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = PostForm(instance=post)
    
    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == "POST":
        form = CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    
    return redirect("blog:post_detail", post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id
    )
    
    if comment.author != request.user:
        raise Http404("Comment not found")
    
    if request.method == "POST":
        form = CommentForm(request.POST or None, instance=comment)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = CommentForm(instance=comment)
    
    return render(
        request,
        "blog/comment.html",
        {"comment": comment, "form": form}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post_id=post_id
    )
    
    if comment.author != request.user:
        raise Http404("Comment not found")
    
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)
    
    return render(request, "blog/delete_comment.html", {"comment": comment})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)
    
    form = PostForm(instance=post)
    return render(request, "blog/detail.html", {"post": post, "form": form})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserForm(request.POST or None, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = UserForm(instance=request.user)
    
    return render(request, "blog/edit_profile.html", {"form": form})
