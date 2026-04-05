FROM python:3.11-slim

WORKDIR /app

ENV APP_NAME="Frontend"
ENV BACKEND_URL="http://backend:5000"

COPY app.py .

RUN chown -R 1001:1001 /app
USER 1001

EXPOSE 8080

CMD ["python", "-u", "app.py"]
