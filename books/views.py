from django.db.models import Sum, F
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Book,Borrow
from .serializers import BookSerializers,BorrowSerializer

LOW_STOCK_LIMIT = 5

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializers
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'author', 'isbn']
    ordering_fields = ['title', 'price', 'quantity', 'created_at']


    def get_queryset(self):
            queryset = super().get_queryset()
            category = self.request.query_params.get('category')
            if category:
                queryset = queryset.filter(category__iexact=category)
            return queryset    


    @action(detail=False, methods=['get'])
    def stats(self, request):
        books = Book.objects.all()
        data = {
            'total_books': books.count(),
            'total_stock': books.aggregate(total=Sum('quantity'))['total'] or 0,
            'total_value': books.aggregate(
                total=Sum(F('price') * F('quantity'))
            )['total'] or 0,
            'low_stock_count': books.filter(quantity__lt=LOW_STOCK_LIMIT).count(),
            'categories': list(
                books.values_list('category', flat=True).distinct().order_by('category')
            ),
        }
        return Response(data)

    @action(detail=False, methods=['post'])
    def bulk(self, request):
        rows = request.data
        if not isinstance(rows, list) or len(rows) == 0:
            return Response({'detail': 'Send a non-empty list of books.'}, status=400)
        if len(rows) > 200:
            return Response({'detail': 'Maximum 200 books at a time.'}, status=400)

        results = []
        saved = 0
        for index, row in enumerate(rows):
            serializer = self.get_serializer(data=row)
            if serializer.is_valid():
                serializer.save()
                saved += 1
                results.append({'index': index, 'ok': True})
            else:
                results.append({'index': index, 'ok': False, 'errors': serializer.errors})

        return Response({'saved': saved, 'failed': len(rows) - saved, 'results': results})


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrow.objects.select_related('book').order_by('-borrowed_at')
    serializer_class = BorrowSerializer
    http_method_names = ['get', 'post', 'head', 'options']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        book = serializer.validated_data['book']

        with transaction.atomic():
            if book.quantity < 1:
                return Response({'book': ['This book is out of stock.']}, status=400)
            book.quantity -= 1
            book.save()
            serializer.save()
        return Response(serializer.data, status=201)

    @action(detail=True, methods=['post'], url_path='return')
    def return_book(self, request, pk=None):
        borrow = self.get_object()
        if borrow.returned_at:
            return Response({'detail': 'Already returned.'}, status=400)
        with transaction.atomic():
            borrow.returned_at = timezone.now()
            borrow.save()
            borrow.book.quantity += 1
            borrow.book.save()
        return Response(self.get_serializer(borrow).data)    
    