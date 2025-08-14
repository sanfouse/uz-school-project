#!/bin/bash

# 🏭 Создание production конфигурации
set -e

echo "🏭 Создаем production конфигурацию..."

# Запрашиваем домен
read -p "🌐 Введите ваш домен (например: app.example.com): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo "❌ Домен не может быть пустым"
    exit 1
fi

echo "✅ Домен: $DOMAIN"

# Создаем production values для frontend
echo "📝 Создаем frontend/.helm/prod-values.yaml..."
cat > frontend/.helm/prod-values.yaml << EOF
replicaCount: 2

image:
  repository: frontend
  tag: latest
  pullPolicy: Always

service:
  type: ClusterIP
  port: 8501

ingress:
  enabled: true
  host: $DOMAIN

resources:
  requests:
    cpu: 0.5
    memory: 512Mi
  limits:
    cpu: 1.0
    memory: 1Gi

secrets:
  SCRAPERS_API_BASE: "http://scrapers-api-service"
EOF

# Создаем production values для scrapers-api
echo "📝 Создаем scrapers-api/.helm/prod-values.yaml..."
cat > scrapers-api/.helm/prod-values.yaml << EOF
replicaCount: 2

image:
  repository: scrapers-api
  tag: latest
  pullPolicy: Always

service:
  type: ClusterIP
  port: 8000

resources:
  requests:
    cpu: 0.5
    memory: 512Mi
  limits:
    cpu: 1.0
    memory: 1Gi

secrets:
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  REDIS_DB: "0"
  REDIS_PASSWORD: ""
  RABBITMQ_HOST: "rabbitmq-service"
  RABBITMQ_PORT: "5672"
  RABBITMQ_USER: "guest"
  RABBITMQ_PASSWORD: "guest"
  RABBITMQ_QUEUE: "scraper-jobs"
EOF

# Создаем production values для notification-bot
echo "📝 Создаем notification-bot/.helm/prod-values.yaml..."
cat > notification-bot/.helm/prod-values.yaml << EOF
replicaCount: 1

image:
  repository: notification-bot
  tag: latest
  pullPolicy: Always

resources:
  requests:
    cpu: 0.2
    memory: 256Mi
  limits:
    cpu: 0.5
    memory: 512Mi

secrets:
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  REDIS_DB: "0"
  REDIS_PASSWORD: ""
  RABBITMQ_HOST: "rabbitmq-service"
  RABBITMQ_PORT: "5672"
  RABBITMQ_USER: "guest"
  RABBITMQ_PASSWORD: "guest"
  RABBITMQ_QUEUE: "notifications"
EOF

# Создаем production values для profi-scraper
echo "📝 Создаем profi-scraper/.helm/prod-values.yaml..."
cat > profi-scraper/.helm/prod-values.yaml << EOF
replicaCount: 1

image:
  repository: profi-scraper
  tag: latest
  pullPolicy: Always

resources:
  requests:
    cpu: 0.5
    memory: 512Mi
  limits:
    cpu: 1.0
    memory: 1Gi

secrets:
  REDIS_HOST: "redis-service"
  REDIS_PORT: "6379"
  REDIS_DB: "0"
  REDIS_PASSWORD: ""
  RABBITMQ_HOST: "rabbitmq-service"
  RABBITMQ_PORT: "5672"
  RABBITMQ_USER: "guest"
  RABBITMQ_PASSWORD: "guest"
  RABBITMQ_QUEUE: "scraper-jobs"
EOF

echo ""
echo "✅ Production конфигурация создана!"
echo ""
echo "📁 Созданные файлы:"
echo "   - frontend/.helm/prod-values.yaml"
echo "   - scrapers-api/.helm/prod-values.yaml"
echo "   - notification-bot/.helm/prod-values.yaml"
echo "   - profi-scraper/.helm/prod-values.yaml"
echo ""
echo "🚀 Для развертывания используйте:"
echo "   skaffold run -f skaffold-prod.yaml"
echo ""
echo "🌐 Домен настроен: $DOMAIN"
echo "💡 Не забудьте добавить A-запись в DNS: $DOMAIN -> <EXTERNAL-IP>"
