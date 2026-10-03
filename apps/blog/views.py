from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import F, Q
from apps.blog.models import BlogPost, BlogCategory

def blog_list_view(request):
    """Career advice, resume guides, and interview tips blog."""
    posts = BlogPost.objects.filter(is_published=True).select_related('category', 'author')

    q = request.GET.get('q', '').strip()
    if q:
        posts = posts.filter(Q(title__icontains=q) | Q(content__icontains=q) | Q(excerpt__icontains=q))

    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    paginator = Paginator(posts, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    categories = BlogCategory.objects.all()

    return render(request, 'blog/blog_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': q,
        'selected_category': category_slug,
    })


def blog_detail_view(request, slug):
    """Detailed blog article view."""
    post = get_object_or_404(BlogPost.objects.select_related('category', 'author'), slug=slug, is_published=True)
    BlogPost.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)

    recent_posts = BlogPost.objects.filter(is_published=True).exclude(pk=post.pk)[:4]

    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'recent_posts': recent_posts,
    })
