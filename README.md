# Project Description

A product ingestion system built with DRF that allows you to manage products and bulk import them from CSV/Excel files. The project is containerized with Docker for easy setup and includes an admin panel for managing product data.  

The feature set for this project are as follows:
- **Multiple File Support**: Upload and process multiple files in a single API call.  
- **Product Management API**: Create, update, delete, and fetch products.  
- **Bulk File Upload**: Import product data directly from CSV or Excel files.  
- **Error Handling**: Reports invalid rows while continuing to process valid ones.  
- **Django Admin Panel**: Manage products with search, filters, and list views.  
- **Dockerized Setup**: Simple and consistent environment with Docker & Docker Compose.  

---

## Technology used

- Python 3.8+
- Django 4.x
- Django REST Framework
- Pandas + OpenPyXL
- SQLite (default)

---

## API Endpoints

### Products  
- `GET /api/products/` → List all products  
- `POST /api/products/` → Create a new product  
- `GET /api/products/{id}/` → Retrieve a single product  
- `PUT/PATCH /api/products/{id}/` → Update a product  
- `DELETE /api/products/{id}/` → Delete a product  

### File Upload  
- `POST /api/products/upload/` → Upload CSV/Excel file(s)  

📌 **Testing file upload in Postman**  
- Body → form-data → `key: file` → upload `.csv` or `.xlsx`  

**Sample CSV:**  
```csv
sku,name,category,price,stock_qty,status
SKU0001,Product 1,Clothing,232.54,189,inactive
SKU0002,Product 2,Electronics,337.42,60,active
SKU0003,Product 3,Home,416.91,104,inactive
```

📑 **Multiple File Uploads**
- You can upload multiple files in a single API call.
- Each file will be processed separately, and the response will show the status for each file.

**Sample Response (multiple files):**
```
{
    "files": [
        {
            "file": "products_1.xlsx",
            "processed": 8,
            "errors": []
        },
        {
            "file": "products_2.csv",
            "processed": 1000,
            "errors": []
        },
        {
            "file": "products_3.xlsx",
            "processed": 1000,
            "errors": []
        }
    ]
}
```

---

## Django Admin
- Create superuser with command `docker-compose exec web python manage.py createsuperuser`
- Then, login with same credentials at route: http://127.0.0.1:8000/admin/
- You can manage products with search, filters, list view on admin page.

---

## To set up this project

1. Clone this repo and navigate into the project directory.
2. Create a new .env file by copying the env.example file and update it with your credentials as needed
3. Build docker image `docker-compose build`
4. Start container `docker-compose up`
5. Apply migrations `docker-compose exec web python manage.py migrate`
6. Project should be live at localhost port 8000.
