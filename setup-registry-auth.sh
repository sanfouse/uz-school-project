#!/bin/bash

echo "🔐 Настраиваем аутентификацию для Docker Registry..."

echo ""
echo "📝 Введите учетные данные для registry:"
echo "Registry: aadbccd8-cute-cygnus.registry.twcstorage.ru"
echo ""

read -p "Username: " REGISTRY_USERNAME
read -s -p "Password: " REGISTRY_PASSWORD
echo ""

if [ -z "$REGISTRY_USERNAME" ] || [ -z "$REGISTRY_PASSWORD" ]; then
    echo "❌ Ошибка: Username и Password не могут быть пустыми"
    exit 1
fi

echo ""
echo "🔑 Создаем Secret для registry..."

# Создаем Secret с учетными данными registry
kubectl create secret docker-registry registry-secret \
    --docker-server=aadbccd8-cute-cygnus.registry.twcstorage.ru \
    --docker-username="$REGISTRY_USERNAME" \
    --docker-password="$REGISTRY_PASSWORD" \
    --docker-email="" \
    --dry-run=client -o yaml > registry-secret.yaml

# Применяем Secret
kubectl apply -f registry-secret.yaml

echo "✅ Secret для registry создан!"

# Обновляем все deployments чтобы использовать Secret
echo "🔄 Обновляем deployments для использования registry Secret..."

# Обновляем scrapers-api deployment
kubectl patch deployment scrapers-api -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"registry-secret"}]}}}}'

# Обновляем notification-bot deployment (если есть)
kubectl patch deployment notification-bot -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"registry-secret"}]}}}}' 2>/dev/null || echo "notification-bot deployment не найден"

# Обновляем frontend deployment (если есть)
kubectl patch deployment frontend -p '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"registry-secret"}]}}}}' 2>/dev/null || echo "frontend deployment не найден"

echo "✅ ImagePullSecrets добавлены во все deployments!"

echo ""
echo "🚀 Теперь перезапустите поды:"
echo "kubectl rollout restart deployment scrapers-api"
echo "kubectl rollout restart deployment notification-bot"
echo "kubectl rollout restart deployment frontend"
echo ""
echo "💡 Или перезапустите все через Skaffold:"
echo "skaffold delete"
echo "skaffold run"
