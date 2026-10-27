from rest_framework import serializers
from  .models  import Book,Borrow

class BookSerializers(serializers.ModelSerializer):
    class Meta:
            model=Book
            fields="__all__"

class BorrowSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = Borrow
        fields = ['id', 'book', 'book_title', 'student_name', 'student_id',
                  'borrowed_at', 'due_date', 'returned_at']
        read_only_fields = ['borrowed_at', 'due_date', 'returned_at']


