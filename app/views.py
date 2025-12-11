from django.shortcuts import render, redirect, get_object_or_404
from elasticsearch_dsl.query import MultiMatch
from .documents import BookDocument
from django.views.decorators.http import require_POST
from .models import Book


def index(request):
    q = request.GET.get("q")
    context = {}
    print(q)
    if q:
        query = MultiMatch(query=q, fields=["title"], fuzziness="AUTO")
        s = BookDocument.search().query(query).sort({'_score': {'order': 'desc'}})[0:25]
        es_results_map = {hit.meta.id: hit.meta.score for hit in s.execute()}
        es_ids = list(es_results_map.keys())
        books_db = Book.objects.filter(id__in=es_ids)
        books_for_template = []
        for book_obj in books_db:
            book_obj.score = es_results_map.get(str(book_obj.id))
            books_for_template.append(book_obj)
            books_for_template.sort(key=lambda book: book.score, reverse=True)

        context["books"] = books_for_template
        context["query"] = q
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
