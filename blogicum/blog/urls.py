from django.urls import path

from . import views
from .user_views import (add_comment, delete_comment, edit_comment,
                         edit_profile, post_create, post_delete, post_edit,
                         profile)

app_name = "blog"

urlpatterns = [
    path("", views.index, name="index"),
    path("posts/<int:post_id>/", views.post_detail, name="post_detail"),
    path("category/<slug:category_slug>/", views.category_posts,
         name="category_posts"),
    path("profile/edit/", edit_profile, name="edit_profile"),
    path("profile/<str:username>/", profile, name="profile"),
    path("create/", post_create, name="create_post"),
    path("posts/create/", post_create, name="post_create"),
    path("posts/<int:post_id>/edit/", post_edit, name="post_edit"),
    path("posts/<int:post_id>/edit/", post_edit, name="edit_post"),
    path("posts/<int:post_id>/delete/", post_delete, name="post_delete"),
    path("posts/<int:post_id>/delete/", post_delete, name="delete_post"),
    path("posts/<int:post_id>/comment/", add_comment, name="add_comment"),
    path(
        "posts/<int:post_id>/comment/<int:comment_id>/edit/",
        edit_comment,
        name="edit_comment",
    ),
    path(
        "posts/<int:post_id>/comment/<int:comment_id>/delete/",
        delete_comment,
        name="delete_comment",
    ),
]
