from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import UserForm
from .models import Comment, Post

User = get_user_model()


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts_query = Post.objects.filter(author=profile_user)
    if request.user != profile_user:
        posts_query = posts_query.filter(
            is_published=True, pub_date__lte=timezone.now()
        )
    paginator = Paginator(
        posts_query.select_related("category", "location")
        .annotate(comment_count=Count("comments"))
        .order_by("-pub_date"),
        10,
    )
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "blog/profile.html",
        {"profile": profile_user, "page_obj": page_obj}
    )


@login_required
def post_create(request):
    from .forms import PostForm

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
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
    from .forms import PostForm
    from .models import Post

    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect("blog:post_detail", post_id=post_id)
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("blog:post_detail", post_id=post_id)
    else:
        form = PostForm(instance=post)
    return render(request, "blog/create.html", {"form": form})


@login_required
def add_comment(request, post_id):
    from .models import Post

    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Comment.objects.create(
                text=text, post=post, author=request.user
            )
    return redirect("blog:post_detail", post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        from django.http import Http404

        raise Http404("Comment not found")
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            comment.text = text
            comment.save()
        return redirect("blog:post_detail", post_id=post_id)
    from .forms import CommentForm

    form = CommentForm(instance=comment)
    return render(
        request, "blog/comment.html", {"comment": comment, "form": form}
    )


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.author != request.user:
        from django.http import Http404

        raise Http404("Comment not found")
    if request.method == "POST":
        comment.delete()
        return redirect("blog:post_detail", post_id=post_id)
    return render(request, "blog/delete_comment.html", {"comment": comment})


@login_required
def post_delete(request, post_id):
    from .models import Post

    post = get_object_or_404(Post, id=post_id, author=request.user)
    if request.method == "POST":
        post.delete()
        return redirect("blog:profile", username=request.user.username)
    return render(request, "blog/detail.html", {"post": post})


@login_required
def edit_profile(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("blog:profile", username=request.user.username)
    else:
        form = UserForm(instance=request.user)
    return render(request, "blog/edit_profile.html", {"form": form})
