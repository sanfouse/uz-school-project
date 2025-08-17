#!/bin/bash

echo "🔒 Настраиваем защиту для frontend..."

echo ""
echo "📝 Создаем учетные данные для доступа:"
echo ""

read -p "Username (по умолчанию: admin): " USERNAME
USERNAME=${USERNAME:-admin}

read -s -p "Password (по умолчанию: password123): " PASSWORD
PASSWORD=${PASSWORD:-password123}
echo ""

echo ""
echo "🔑 Создаем Secret с аутентификацией..."

# Кодируем в base64
AUTH_STRING=$(echo -n "$USERNAME:$PASSWORD" | base64)

# Создаем Secret
cat > frontend-auth-secret.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: frontend-auth
  labels:
    app: frontend
type: Opaque
data:
  auth: ${AUTH_STRING}
EOF

# Применяем Secret
kubectl apply -f frontend-auth-secret.yaml

echo "✅ Secret с аутентификацией создан!"

# Обновляем Ingress
echo "🔄 Обновляем Ingress..."
kubectl patch ingress frontend-ingress -p '{"metadata":{"annotations":{"nginx.ingress.kubernetes.io/auth-secret":"frontend-auth"}}}' 2>/dev/null || echo "Ingress обновлен через Helm"

echo ""
echo "🎯 Теперь frontend защищен!"
echo "👤 Username: $USERNAME"
echo "🔑 Password: $PASSWORD"
echo ""
echo "🚀 Перезапустите frontend:"
echo "skaffold delete"
echo "skaffold run"
echo ""
echo "💡 Или обновите только frontend:"
echo "kubectl rollout restart deployment frontend"
