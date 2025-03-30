FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PATH="/usr/local/bin:${PATH}"

CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "app:app"] 