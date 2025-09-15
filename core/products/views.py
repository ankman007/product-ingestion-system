import pandas as pd
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from loguru import logger

from .models import Product
from .serializers import ProductSerializer

REQUIRED_COLUMNS = ['sku', 'name', 'category', 'price', 'stock_qty', 'status']


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        raise Http404("Product not found")

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return JsonResponse(serializer.data)

    elif request.method in ['PUT', 'PATCH']:
        data = JSONParser().parse(request)
        serializer = ProductSerializer(product, data=data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        product.delete()
        return JsonResponse({'message': 'Product deleted successfully'}, status=204)

@api_view(['POST'])
@parser_classes([MultiPartParser])
def product_upload(request):
    files = request.FILES.getlist('file')  # Support multiple files
    if not files:
        return Response({"error": "No files uploaded"}, status=400)

    response_summary = []

    for file in files:
        file_result = {"file": file.name, "processed": 0, "errors": []}

        if not file.name.endswith(('.csv', '.xls', '.xlsx')):
            msg = "Invalid file type. Only CSV or Excel files allowed."
            logger.warning(f"{file.name}: {msg}")
            file_result['errors'].append(msg)
            response_summary.append(file_result)
            continue

        file_path = default_storage.save(file.name, file)

        try:
            if file.name.endswith('.csv'):
                df = pd.read_csv(default_storage.path(file_path))
            else:
                df = pd.read_excel(default_storage.path(file_path))
        except Exception as e:
            msg = f"Failed to read file: {str(e)}"
            logger.error(f"{file.name}: {msg}")
            file_result['errors'].append(msg)
            response_summary.append(file_result)
            continue

        if df.empty:
            msg = "File is empty"
            logger.warning(f"{file.name}: {msg}")
            file_result['errors'].append(msg)
            response_summary.append(file_result)
            continue

        # Check required columns
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            msg = f"Missing columns: {', '.join(missing_columns)}"
            logger.warning(f"{file.name}: {msg}")
            file_result['errors'].append(msg)
            response_summary.append(file_result)
            continue

        for col in ['sku', 'name', 'category', 'status']:
            df[col] = df[col].astype(str).str.strip()

        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['stock_qty'] = pd.to_numeric(df['stock_qty'], errors='coerce')

        empty_skus = df['sku'].isnull() | (df['sku'] == '')
        if empty_skus.any():
            rows = df[empty_skus].index.tolist()
            msg = f"Empty SKUs found at rows: {rows}"
            logger.warning(f"{file.name}: {msg}")
            df = df[~empty_skus]  # Remove invalid rows
            file_result['errors'].append(msg)

        # Drop duplicate SKUs in the same file (keep last)
        dup_in_file = df[df.duplicated(subset='sku', keep=False)]
        if not dup_in_file.empty:
            logger.info(f"{file.name}: Duplicate SKUs in file removed: {dup_in_file['sku'].tolist()}")
            df = df.drop_duplicates(subset='sku', keep='last')
            file_result['errors'].append(f"Duplicate SKUs removed in file: {dup_in_file['sku'].tolist()}")

        # Save to DB
        processed_count = 0
        with transaction.atomic():
            for row in df.to_dict(orient='records'):
                try:
                    obj, created = Product.objects.update_or_create(
                        sku=row['sku'],
                        defaults={
                            'name': row['name'],
                            'category': row['category'],
                            'price': row['price'],
                            'stock_qty': row['stock_qty'],
                            'status': row['status']
                        }
                    )
                    processed_count += 1
                    if created:
                        logger.info(f"{file.name}: Created new product: {obj.sku}")
                    else:
                        logger.info(f"{file.name}: Updated existing product: {obj.sku}")
                except Exception as e:
                    msg = f"Failed to save SKU {row['sku']}: {str(e)}"
                    logger.error(f"{file.name}: {msg}")
                    file_result['errors'].append(msg)

        file_result['processed'] = processed_count
        response_summary.append(file_result)

    return Response({"files": response_summary}, status=200)