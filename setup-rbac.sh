#!/bin/bash

echo "🔐 Настраиваем права доступа для кластера..."

# Применяем RBAC
kubectl apply -f k8s-rbac.yaml

echo "✅ RBAC ресурсы созданы!"

# Ждем создания ServiceAccount
echo "⏳ Ждем создания ServiceAccount..."
sleep 5

# Создаем токен для ServiceAccount (автоматически)
echo "🔑 Создаем токен для ServiceAccount..."
kubectl create token app-deployer -n default --duration=8760h > app-deployer-token.txt

# Читаем токен
TOKEN=$(cat app-deployer-token.txt)

echo ""
echo "🎯 ТОКЕН ДОСТУПА:"
echo "=================================="
echo "$TOKEN"
echo "=================================="
echo ""

# Создаем kubeconfig для нового пользователя
echo "📝 Создаем kubeconfig для app-deployer..."

# Получаем текущий контекст
CURRENT_CONTEXT=$(kubectl config current-context)
CLUSTER_NAME=$(kubectl config view --minify -o jsonpath='{.clusters[0].name}')
CLUSTER_SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')

# Создаем новый kubeconfig
cat > app-deployer-kubeconfig.yaml << EOF
apiVersion: v1
kind: Config
clusters:
- name: ${CLUSTER_NAME}
  cluster:
    server: ${CLUSTER_SERVER}
    certificate-authority-data: $(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')

users:
- name: app-deployer
  user:
    token: ${TOKEN}

contexts:
- name: app-deployer-context
  context:
    cluster: ${CLUSTER_NAME}
    user: app-deployer
    namespace: default

current-context: app-deployer-context
EOF

echo "✅ Kubeconfig создан: app-deployer-kubeconfig.yaml"
echo "✅ Токен сохранен в: app-deployer-token.txt"
echo ""
echo "🚀 Теперь можете использовать:"
echo "export KUBECONFIG=./app-deployer-kubeconfig.yaml"
echo "kubectl get pods"
echo ""
echo "Или для Skaffold:"
echo "skaffold run --kubeconfig=./app-deployer-kubeconfig.yaml"
echo ""
echo "💡 Токен действителен 1 год (8760 часов)"
