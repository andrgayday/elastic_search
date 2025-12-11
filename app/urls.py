from django.urls import path
from .views import index, book_add, book_delete

urlpatterns = [
    path("", index, name="index"),
    path('add/', book_add, name='book_add'),
    path('delete/', book_delete, name='book_delete'),
]