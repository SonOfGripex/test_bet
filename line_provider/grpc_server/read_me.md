#Для генерации
python -m grpc_tools.protoc -I. --grpc_python_out=. --python_out=. grpc_server/service.proto