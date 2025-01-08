FROM python:3.10

WORKDIR /bet_maker

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -m grpc_tools.protoc -I. --grpc_python_out=. --python_out=. grpc_server/service.proto

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]