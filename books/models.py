from django.db import models
from datetime import timedelta
from django.utils import timezone

class Book(models.Model):
    title=models.CharField(max_length=200)
    author=models.CharField(max_length=200)
    isbn=models.CharField(max_length=100,unique=True)
    category=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=8, decimal_places=2)
    quantity=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


def __str__(self):
    return self.title



def default_due_date():
    return timezone.now().date() + timedelta(days=14)


class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows')
    student_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=30)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(default=default_due_date)
    returned_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_name} - {self.book.title}"






