FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY sysadmin_app /app/sysadmin_app

EXPOSE 8000

CMD ["adk", "web", "--host", "0.0.0.0"]
