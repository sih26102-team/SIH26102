FROM python:3.11-slim
WORKDIR /app
COPY backend-case-management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend-case-management/ .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]