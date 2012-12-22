# Create your views here.

from django.shortcuts import render_to_response
from models import *
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required


def Blog(request):
    """Main listing."""
    posts = Post.objects.filter(publish=1).all().order_by("-created")
    paginator = Paginator(posts, 2)
    recent_posts = Post.objects.filter(publish=1).all().order_by("-created")[:4]
    links = LinksToRead.objects.all()

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)

    return render_to_response("blog.html", {"posts": posts, "links": links, "recentposts": recent_posts})


@staff_member_required
def BlogPreview(request):
    posts = Post.objects.filter(publish=0).all().order_by("-created")
    recent_posts = Post.objects.filter(publish=0).all().order_by("-created")[:4]
    links = LinksToRead.objects.all()

    return render_to_response("blog.html", {"posts": posts, "links": links, "recentposts": recent_posts})


def Article(request, post_num):
    """Page for Post"""
    try:
        post = Post.objects.filter(publish=1).get(pk=post_num)
    except:
        post = None
        recent_posts = Post.objects.filter(publish=1).all().order_by("-created")[:4]
        links = LinksToRead.objects.all()
        render_to_response("blog_post.html", {"links": links, "recentposts": recent_posts}, context_instance=RequestContext(request))
    posts = Post.objects.filter(publish=1).all().order_by("-created")
    paginator = Paginator(posts, 2)
    recent_posts = Post.objects.filter(publish=1).all().order_by("-created")[:4]
    links = LinksToRead.objects.all()

    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        posts = paginator.page(page)
    except (InvalidPage, EmptyPage):
        posts = paginator.page(paginator.num_pages)
    return render_to_response("blog_post.html", {"post": post, "links": links, "recentposts": recent_posts}, context_instance=RequestContext(request))
