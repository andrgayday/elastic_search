import csv
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from app.models import Book # Убедитесь, что Book импортируется корректно

# Установите размер пакета
BATCH_SIZE = 2000

class Command(BaseCommand):
    # Описание команды, которое будет отображаться в справке
    help = 'Импортирует данные о книгах из CSV-файла в модель Book, используя bulk_create.'
    
    # 1. Определяем аргументы, которые команда может принимать
    def add_arguments(self, parser):
        parser.add_argument(
            'csv_path',
            type=str,
            help='Полный путь к CSV-файлу для импорта (например, _dev/data_fixed.csv)'
        )
    
    # 2. Основная логика, запускаемая при выполнении команды
    def handle(self, *args, **options):
        csv_path = options['csv_path']
        books_to_create = []
        created_count = 0
        total_count = 0
        
        self.stdout.write(f"🚀 Начинаем чтение файла: {csv_path}")

        try:
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    title = row.get('NameFull')
                    total_count += 1
                    
                    if title:
                        # Создаем объект Book, но пока не сохраняем в БД
                        books_to_create.append(
                            Book(title=title)
                        )

                        # Проверяем, достигнут ли размер пакета
                        if len(books_to_create) >= BATCH_SIZE:
                            
                            # Используем transaction.atomic() для гарантии атомарности
                            with transaction.atomic():
                                Book.objects.bulk_create(books_to_create)
                                
                            created_count += len(books_to_create)
                            
                            self.stdout.write(
                                self.style.SUCCESS(f"✅ Создано записей: {created_count} / {total_count}. Текущий пакет: {BATCH_SIZE}")
                            )
                            
                            # Очищаем список для следующего пакета
                            books_to_create = []

                # Сохраняем оставшиеся записи (финальный пакет)
                if books_to_create:
                    with transaction.atomic():
                        Book.objects.bulk_create(books_to_create)
                        
                    created_count += len(books_to_create)
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Создано записей (финальный пакет): {created_count} / {total_count}")
                    )

        except FileNotFoundError:
            raise CommandError(f'Файл не найден по пути: "{csv_path}"')
        except Exception as e:
            # Откат транзакции при любой ошибке (если она произошла внутри atomic блока)
            raise CommandError(f'Произошла ошибка при обработке файла: {e}')


        self.stdout.write("---")
        self.stdout.write(
            self.style.SUCCESS(f"🎉 Завершено! Всего успешно создано объектов Book: {created_count}")
        )