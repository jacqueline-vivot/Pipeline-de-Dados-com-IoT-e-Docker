FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY sql ./sql
ENV PYTHONUNBUFFERED=1
CMD ["streamlit", "run", "src/dashboard.py", "--server.address=0.0.0.0"]
