FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY mcp-docker/mcp_http_server.py /app/mcp_http_server.py

VOLUME ["/app/managed_dir"]

EXPOSE 9000

CMD ["python", "/app/mcp_http_server.py"]
