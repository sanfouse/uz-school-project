#!/bin/bash

# 🌐 Получение IP адреса и настройка доступа без домена

echo "🌐 Настраиваем доступ к frontend без домена..."

# Проверяем, что Ingress Controller запущен
echo "🔍 Проверяем Ingress Controller..."
if ! kubectl get pods -n ingress-nginx | grep -q "ingress-nginx-controller.*Running"; then
    echo "❌ Ingress Controller не запущен. Запустите сначала:"
    echo "   kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml"
    exit 1
fi

echo "✅ Ingress Controller запущен"

# Получаем внешний IP
echo "📡 Получаем внешний IP..."
EXTERNAL_IP=""

# Пробуем разные способы получения IP
if kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null | grep -q .; then
    EXTERNAL_IP=$(kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
elif kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null | grep -q .; then
    EXTERNAL_IP=$(kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
else
    echo "⏳ Внешний IP еще не назначен (это нормально для новых кластеров)"
    echo "💡 Попробуйте позже или используйте port-forward"
fi

if [ -n "$EXTERNAL_IP" ]; then
    echo "✅ Внешний IP: $EXTERNAL_IP"
    echo ""
    echo "🌐 Теперь вы можете:"
    echo "   1. Открыть в браузере: http://$EXTERNAL_IP"
    echo "   2. Или использовать curl: curl http://$EXTERNAL_IP"
else
    echo ""
    echo "🔧 Альтернативные способы доступа:"
    echo ""
    echo "1️⃣ Port-forward для Ingress Controller:"
    echo "   kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 80:80"
    echo "   Затем откройте: http://localhost"
    echo ""
    echo "2️⃣ Port-forward для frontend сервиса:"
    echo "   kubectl port-forward service/frontend 8501:8501"
    echo "   Затем откройте: http://localhost:8501"
    echo ""
    echo "3️⃣ Через Skaffold (если запущен):"
    echo "   skaffold dev"
    echo "   Затем откройте: http://localhost:8501"
fi

echo ""
echo "📊 Текущий статус:"
echo "=================="
kubectl get pods -l app=frontend
echo ""
kubectl get ingress
echo ""
kubectl get svc -n ingress-nginx
