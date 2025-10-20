from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils import timezone

from .forms import CommentForm, PostForm, UserForm
from .models import Category, Comment, Post
from .utils import get_paginated_page, get_posts_queryset


def index(request):
    post_list = get_posts_queryset(request.user)
    page_obj = get_paginated_page(request, post_list)
    return render(request, "blog/index.html", {"page_obj": page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("category", "location", "author"),
        id=post_id
    )

    if (
        not post.is_published
        or post.pub_date > timezone.now()
        or not post.category.is_published  # type: ignore
    ):
        if request.user != post.author:
            raise Http404("Post not found")

    form = CommentForm()
    comments = post.comments.select_related("author")  # type: ignore

    return render(
        request,
        "blog/detail.html",
        {"post": post, "form": form, "comments": comments},
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True
    )
    post_list = get_posts_queryset(
        request.user, manager=category.posts  # type: ignore
    )
    page_obj = get_paginated_page(request, post_list)
    return render(
        request,
        "blog/category.html",
        {"category": category, "page_obj": page_obj},
    )


def profile(request, username):
    from django.contrib.auth import get_user_model

    User = get_user_model()

    profile_user = get_object_or_404(User, username=username)

    posts_query = get_posts_queryset(
        manager=profile_user.posts,  # type: ignore
        apply_filters=(request.user != profile_user),
        annotate_comments=True,
    )

    page_obj = get_paginated_page(request, posts_query)

    return render(
        request,
        "blog/profile.html",
        {"profile": profile_user, "page_obj": page_obj},
    )


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect("blog:profile", username=request.user.username)

    return render(request, "blog/create.html", {"form": form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)

    form = PostForm(
        request.POST or None, request.FILES or None, instance=post
    )
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)

    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

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
        Comment, id=comment_id, post_id=post_id
    )

    if comment.author != request.user:
        raise Http404("Comment not found")

    form = CommentForm(request.POST or None, instance=comment)
    if form.is_valid():
        form.save()
        return redirect("blog:post_detail", post_id=post_id)

    return render(
        request, "blog/comment.html", {"comment": comment, "form": form}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(
        Comment, id=comment_id, post_id=post_id
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
    form = UserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect("blog:profile", username=request.user.username)

    return render(request, "blog/edit_profile.html", {"form": form})
