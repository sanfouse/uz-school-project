#!/bin/bash

# 🚀 Автоматическое развертывание на облачном кластере
set -e

echo "🚀 Начинаем развертывание на облачном кластере..."

# Проверяем наличие kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl не установлен. Установите kubectl"
    exit 1
fi

# Проверяем подключение к кластеру
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Не удается подключиться к кластеру Kubernetes"
    echo "💡 Убедитесь, что вы подключены к кластеру:"
    echo "   - GKE: gcloud container clusters get-credentials <cluster-name> --zone=<zone>"
    echo "   - EKS: aws eks update-kubeconfig --region <region> --name <cluster-name>"
    echo "   - AKS: az aks get-credentials --resource-group <rg> --name <cluster-name>"
    exit 1
fi

echo "✅ Подключение к кластеру установлено"

# Проверяем наличие Skaffold
if ! command -v skaffold &> /dev/null; then
    echo "❌ Skaffold не установлен. Установите Skaffold"
    exit 1
fi

echo "✅ Skaffold найден"

# Проверяем наличие Nginx Ingress Controller
echo "🔍 Проверяем Nginx Ingress Controller..."
if ! kubectl get namespace ingress-nginx &> /dev/null; then
    echo "📦 Устанавливаем Nginx Ingress Controller..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml
    
    echo "⏳ Ждем запуска Ingress Controller..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=180s
    
    echo "✅ Ingress Controller установлен и запущен"
else
    echo "✅ Ingress Controller уже установлен"
fi

# Проверяем статус Ingress Controller
echo "📊 Статус Ingress Controller:"
kubectl get pods -n ingress-nginx

# Получаем внешний IP (если есть)
echo "🌐 Получаем внешний IP..."
EXTERNAL_IP=$(kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "PENDING")

if [ "$EXTERNAL_IP" != "PENDING" ] && [ "$EXTERNAL_IP" != "" ]; then
    echo "✅ Внешний IP: $EXTERNAL_IP"
    echo "💡 Добавьте A-запись в DNS: your-domain.com -> $EXTERNAL_IP"
else
    echo "⏳ Внешний IP еще не назначен (это нормально для новых кластеров)"
fi

# Развертываем приложение
echo "🚀 Развертываем приложение..."
skaffold run

# Ждем запуска всех подов
echo "⏳ Ждем запуска всех подов..."
kubectl wait --for=condition=ready pod -l app=frontend --timeout=120s
kubectl wait --for=condition=ready pod -l app=scrapers-api --timeout=120s

# Показываем статус
echo ""
echo "📊 Статус развертывания:"
echo "=========================="
kubectl get pods
echo ""
echo "🌐 Ingress:"
kubectl get ingress
echo ""
echo "🔌 Сервисы:"
kubectl get svc

# Проверяем доступность
echo ""
echo "🌐 Проверка доступности:"
if [ "$EXTERNAL_IP" != "PENDING" ] && [ "$EXTERNAL_IP" != "" ]; then
    echo "✅ Внешний IP: $EXTERNAL_IP"
    echo "💡 Для тестирования:"
    echo "   curl -H 'Host: your-domain.com' http://$EXTERNAL_IP"
else
    echo "⏳ Внешний IP еще не назначен"
    echo "💡 Проверьте позже: kubectl get service -n ingress-nginx ingress-nginx-controller"
fi

echo ""
echo "🎉 Развертывание завершено!"
echo ""
echo "📝 Полезные команды:"
echo "   kubectl get all                    # Все ресурсы"
echo "   kubectl logs -l app=frontend -f    # Логи фронтенда"
echo "   kubectl logs -l app=scrapers-api -f # Логи API"
echo "   kubectl get ingress                # Статус Ingress"
echo "   skaffold delete                    # Удалить все"
echo ""
echo "🔧 Для настройки домена:"
echo "   1. Получите внешний IP: kubectl get service -n ingress-nginx ingress-nginx-controller"
echo "   2. Добавьте A-запись в DNS: your-domain.com -> <EXTERNAL-IP>"
echo "   3. Обновите frontend/.helm/values.yaml: ingress.host: your-domain.com"
echo "   4. Перезапустите: skaffold run"
