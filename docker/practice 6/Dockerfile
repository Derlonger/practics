# ✅ Антипаттерн 1: Использование latest тега
# ✅ Антипаттерн 2: Запуск от root пользователя (нет USER)
# ✅ Антипаттерн 3: Не используется WORKDIR
# ✅ Антипаттерн 4: Копирование всего контекста (включая .git, кэши, т.д.)
# ✅ Антипаттерн 5: Установка зависимостей без очистки кэша
# ✅ Антипаттерн 6: Много отдельных RUN команд (каждая = новый слой)
# ✅ Антипаттерн 7: Не используется .dockerignore
# ✅ Антипаттерн 8: Нет порядка копирования (сначала код, потом зависимости)
# ✅ Антипаттерн 9: Устанавливаются dev-зависимости в продакшн образе
# ✅ Антипаттерн 10: Секреты в ENV
# ✅ Антипаттерн 11: Нет healthcheck
# ✅ Антипаттерн 12: Используется shell форма CMD (не exec)
# ✅ Антипаттерн 13: Нет metadata (LABEL)
# ✅ Антипаттерн 14: Не указан EXPOSE
# ✅ Антипаттерн 15: Нет оптимизации слоев
# ✅ Антипаттерн 16: Большой базовый образ (не alpine/slim)

FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-alpine3.15 AS runtime

LABEL name="python-app-best-practices-Docker"
LABEL version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN addgroup -S appuser && adduser -S -G appuser appuser \
 && chown -R appuser:appuser /app

COPY --from=builder --chown=app:app /install /usr/local

COPY --chown=app:app app.py .

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080', timeout=3)" || exit 1

USER appuser

EXPOSE 8080

CMD ["python", "/app/app.py"]
