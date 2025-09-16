import pandas as pd
from django.http import JsonResponse, Http404
from rest_framework.parsers import JSONParser, MultiPartParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from django.db import transaction
from loguru import logger

from .utils import read_file, validate_dataframe
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
    files = request.FILES.getlist('file')
    if not files:
        return Response({"error": "No files uploaded"}, status=400)

    response_summary = []

    for file in files:
        file_result = {"file": file.name, "processed": 0, "errors": []}

        try:
            df = read_file(file)
        except Exception as e:
            msg = f"Failed to read file: {str(e)}"
            logger.error(f"{file.name}: {msg}")
            file_result['errors'].append(msg)
            response_summary.append(file_result)
            continue

        df, validation_errors = validate_dataframe(df, file.name)
        file_result['errors'].extend(validation_errors)

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


@api_view(['GET'])
def api_root(request):
    api_info = {
        "Products": {
            "GET /api/products/": "Retrieve a list of all products",
            "POST /api/products/": "Create a new product",
            "GET /api/products/{id}/": "Retrieve a single product by ID",
            "PUT /api/products/{id}/": "Update all fields of a product by ID",
            "PATCH /api/products/{id}/": "Partially update a product by ID",
            "DELETE /api/products/{id}/": "Delete a product by ID"
        },
        "File Upload": {
            "POST /api/products/upload/": "Upload CSV/Excel file(s) to bulk create/update products"
        }
    }
    return Response(api_info)