FROM cr.yandex/mirror/python:3.11-slim

WORKDIR /app

ENV REGISTRY="Yandex Mirror"

COPY app.py /app

USER 1001

EXPOSE 8080

CMD ["python", "-u", "app.py"]