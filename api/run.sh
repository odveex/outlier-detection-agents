docker stop fastapi-container || true
docker rm fastapi-container || true
docker build -t fastapi-test .
docker run --name fastapi-container -p 8000:8000 fastapi-test