# Project Description

The Product Ingestion System is a backend service built with Django REST Framework (DRF) that provides a robust API for managing products and bulk uploading them from CSV/Excel files. The project is fully containerized using Docker & Docker Compose, making it easy to set up and run in any environment.

🔗 [Postman Docs](https://documenter.getpostman.com/view/32993281/2sB3HqHyLC)

---

## Key Features
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

- `GET /api/products/` → List all products  
- `POST /api/products/` → Create a new product  
- `GET /api/products/{id}/` → Retrieve a single product  
- `PUT/PATCH /api/products/{id}/` → Update a product  
- `DELETE /api/products/{id}/` → Delete a product  
- `POST /api/products/upload/` → Upload CSV/Excel file(s)  

Note: For complete API details and usage examples, refer to the published Postman documentation [here](https://documenter.getpostman.com/view/32993281/2sB3HqHyLC).

---

## To set up this project

1. Clone this repo and navigate into the project directory.
2. Create a new .env file by copying the env.example file and update it with your credentials as needed
3. Build docker image `docker-compose build`
4. Start container `docker-compose up`
5. Apply migrations `docker-compose exec web python manage.py migrate`
6. Create superuser with command `docker-compose exec web python manage.py createsuperuser`
7. Project should be live at localhost port 8000.
