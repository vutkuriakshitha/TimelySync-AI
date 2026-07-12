FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Train models at image build time so the container is ready to serve
# predictions immediately on start. Re-run manually to retrain later.
RUN python -m app.training.train_all

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
