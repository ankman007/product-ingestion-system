import pandas as pd
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from .models import Product
from .serializers import ProductSerializer

REQUIRED_COLUMNS = ['sku', 'name', 'category', 'price', 'stock_qty', 'status']

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # Save file temporarily
        file_path = default_storage.save(file.name, file)
        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(default_storage.path(file_path))
            else:
                df = pd.read_excel(default_storage.path(file_path))
        except Exception as e:
            return Response({"error": f"Failed to read file: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Column validation
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            return Response({"error": f"Missing columns: {', '.join(missing_columns)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Insert/update products
        for row in df.to_dict(orient='records'):
            Product.objects.update_or_create(
                sku=row['sku'],
                defaults={
                    'name': row['name'],
                    'category': row['category'],
                    'price': row['price'],
                    'stock_qty': row['stock_qty'],
                    'status': row['status']
                }
            )

        return Response({"success": f"{len(df)} products processed successfully"})
