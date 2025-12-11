from django.shortcuts import render, redirect, get_object_or_404
from elasticsearch_dsl.query import MultiMatch
from .documents import BookDocument
from django.views.decorators.http import require_POST
from .models import Book

def index(request):
    q = request.GET.get("q")
    context = {}
    if q:
        query = MultiMatch(query=q, fields=["title"], fuzziness="AUTO")
        s = BookDocument.search().query(query)[0:25]
        print(s)
        context["books"] = s
    return render(request, "index.html", context)


@require_POST
def book_add(request):
    """Обрабатывает POST-запрос на добавление новой книги."""
    
    title = request.POST.get("new_title")
    
    if title:
        Book.objects.create(title=title)

    return redirect('index')


@require_POST
def book_delete(request):
    """Обрабатывает POST-запрос на удаление книги."""
    
    book_id = request.POST.get("book_id")
    
    # 1. Находим книгу в БД
    book_to_delete = get_object_or_404(Book, id=book_id)
    
    # 2. Удаляем из БД
    book_to_delete.delete() 
    
    return redirect('index')
