#!/bin/bash

echo "🔐 Исправляем права доступа для scrapers-api..."

# Применяем RBAC для scrapers-api
echo "📋 Применяем RBAC для scrapers-api..."
kubectl apply -f scrapers-api-rbac.yaml

echo "✅ RBAC для scrapers-api создан!"

# Проверяем что ServiceAccount создался
echo "🔍 Проверяем ServiceAccount..."
kubectl get serviceaccount scrapers-api-sa -n default

echo ""
echo "🔄 Теперь нужно перезапустить scrapers-api:"
echo "skaffold delete"
echo "skaffold run"
echo ""
echo "💡 Или перезапустить только scrapers-api:"
echo "kubectl rollout restart deployment scrapers-api"
echo ""
echo "🎯 После этого scrapers-api сможет:"
echo "✅ Создавать поды (Jobs)"
echo "✅ Создавать ConfigMaps"
echo "✅ Получать информацию о подах"
echo "✅ Управлять Jobs"
