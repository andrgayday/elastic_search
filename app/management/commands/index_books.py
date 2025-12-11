# app/management/commands/index_books.py

from django.core.management.base import BaseCommand, CommandError
from app.models import Book
from app.documents import BookDocument 


class Command(BaseCommand):
    # Мета-информация, которая будет отображаться при вызове 'python manage.py help index_books'
    help = 'Индексирует все объекты Book из базы данных в Elasticsearch'

    def add_arguments(self, parser):
        # Добавляем возможность принимать аргументы (необязательно)
        parser.add_argument(
            '--limit', 
            type=int, 
            default=0,
            help='Ограничить количество индексируемых книг'
        )

    def handle(self, *args, **options):
        # Логика, которая выполняется при вызове команды
        
        limit = options['limit']
        
        self.stdout.write(self.style.NOTICE('Начало индексации книг...'))
        
        try:
            # Получение данных из БД
            queryset = Book.objects.all()
            if limit > 0:
                queryset = queryset[:limit]

            total_count = queryset.count()
            self.stdout.write(f'Найдено {total_count} книг для индексации.')

            # Итерация и сохранение в Elasticsearch (с использованием batch/bulk, если возможно)
            
            es_actions = []
            
            for book in queryset:
                # -----------------------------------------------------------------
                # ИСПРАВЛЕНИЕ: Создаем BookDocument, явно передавая поля и метаданные
                # -----------------------------------------------------------------
                book_doc = BookDocument(
                    title=book.title,
                    meta={'id': book.id} 
                )
                
                # Добавляем действие на создание/обновление в список
                action = {
                    '_op_type': 'index',  # Тип операции (index/create/update/delete)
                    '_index': "books",
                    '_id': book.id,
                    '_source': book_doc.to_dict()
                }
                es_actions.append(action)
            
            # 3. Выполняем массовую индексацию (Bulk Indexing)
            from elasticsearch.helpers import bulk
            from elasticsearch_dsl.connections import connections

            es_client = connections.get_connection()
            self.stdout.write(self.style.NOTICE('Выполняю массовую индексацию...'))

            # Вызов bulk API
            success, errors = bulk(es_client, es_actions)
            
            if errors:
                # Обработка ошибок
                self.stdout.write(self.style.ERROR(f'❌ Обнаружены ошибки при пакетной индексации: {len(errors)}'))
                # print(errors[:5]) # Раскомментируйте для просмотра первых 5 ошибок
            
            
            self.stdout.write(self.style.SUCCESS(f'✅ Успешно проиндексировано {success} документов.'))
            
        except Exception as e:
            raise CommandError(f'Ошибка при индексации: {e}')