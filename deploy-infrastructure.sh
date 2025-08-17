#!/bin/bash

# 🏗️ Развертывание инфраструктуры (Redis + RabbitMQ)

echo "🏗️ Развертываем инфраструктуру..."

# Проверяем подключение к кластеру
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Не удается подключиться к кластеру"
    exit 1
fi

echo "✅ Подключение к кластеру установлено"

# Устанавливаем Redis
echo "📦 Устанавливаем Redis..."
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set master.persistence.enabled=false \
  --set replica.persistence.enabled=false \
  --set cluster.enabled=false

# Устанавливаем RabbitMQ
echo "📦 Устанавливаем RabbitMQ..."
helm install my-release bitnami/rabbitmq \
  --set auth.enabled=false \
  --set persistence.enabled=false

# Ждем запуска
echo "⏳ Ждем запуска сервисов..."
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=redis --timeout=120s
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=rabbitmq --timeout=120s

echo "✅ Инфраструктура развернута!"
echo ""
echo "📊 Статус:"
kubectl get pods -l app.kubernetes.io/name=redis
kubectl get pods -l app.kubernetes.io/name=rabbitmq
