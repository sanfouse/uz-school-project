# 🚀 Быстрое развертывание на облачном кластере

## 📋 Что развертываем

- **Frontend** - Streamlit приложение с Ingress
- **Scrapers API** - API для управления скраперами  
- **Profi Scraper** - основной скрапер
- **Notification Bot** - бот для уведомлений
- **Redis** - кэш и очереди
- **RabbitMQ** - брокер сообщений

## ⚡ Быстрый старт (5 минут)

### 1. Подготовка кластера

```bash
# Создаем кластер (выберите один вариант)
# GKE (Google)
gcloud container clusters create scraper-cluster \
  --zone=europe-west1-b \
  --num-nodes=3 \
  --machine-type=e2-standard-2

# EKS (AWS) 
eksctl create cluster \
  --name scraper-cluster \
  --region eu-west-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 3

# AKS (Azure)
az aks create \
  --resource-group scraper-rg \
  --name scraper-cluster \
  --node-count 3 \
  --node-vm-size Standard_B2s
```

### 2. Установка инструментов

```bash
# Установка kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# Установка Helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Установка Skaffold
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
sudo install skaffold /usr/local/bin/
```

### 3. Подключение к кластеру

```bash
# GKE
gcloud container clusters get-credentials scraper-cluster --zone=europe-west1-b

# EKS
aws eks update-kubeconfig --region eu-west-1 --name scraper-cluster

# AKS
az aks get-credentials --resource-group scraper-rg --name scraper-cluster
```

### 4. Установка Nginx Ingress Controller

```bash
# Быстрая установка
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

# Ждем запуска
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### 5. Развертывание приложения

```bash
# Клонируем проект
git clone <your-repo>
cd uz-school-project

# Запускаем Skaffold
skaffold run
```

## 🔧 Настройка для продакшена

### 1. Создаем production values

```bash
# Frontend
cat > frontend/.helm/prod-values.yaml << EOF
ingress:
  enabled: true
  host: your-domain.com  # Замените на ваш домен

resources:
  requests:
    cpu: 0.5
    memory: 512Mi
  limits:
    cpu: 1.0
    memory: 1Gi
EOF

# Scrapers API
cat > scrapers-api/.helm/prod-values.yaml << EOF
resources:
  requests:
    cpu: 0.5
    memory: 512Mi
  limits:
    cpu: 1.0
    memory: 1Gi
EOF
```

### 2. Развертывание с production настройками

```bash
skaffold run -f skaffold-prod.yaml
```

## 🌐 Настройка домена

### 1. Получаем внешний IP

```bash
# Получаем IP Ingress Controller
kubectl get service -n ingress-nginx ingress-nginx-controller

# Или для LoadBalancer
kubectl get service -n ingress-nginx ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### 2. Настраиваем DNS

```bash
# Добавляем A-запись
# your-domain.com -> <EXTERNAL-IP>

# Проверяем
nslookup your-domain.com
```

### 3. Обновляем values.yaml

```yaml
# frontend/.helm/values.yaml
ingress:
  enabled: true
  host: your-domain.com  # Ваш домен
```

## 📊 Мониторинг и логи

### 1. Проверка статуса

```bash
# Все ресурсы
kubectl get all

# Логи приложений
kubectl logs -l app=frontend -f
kubectl logs -l app=scrapers-api -f

# Статус Ingress
kubectl get ingress
kubectl describe ingress frontend-ingress
```

### 2. Доступ к приложению

```bash
# Проверяем Ingress
kubectl get ingress -o wide

# Тестируем доступ
curl -H "Host: your-domain.com" http://<EXTERNAL-IP>
```

## 🚨 Troubleshooting

### Проблема: Ingress не работает

```bash
# Проверяем Ingress Controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx -l app.kubernetes.io/component=controller

# Проверяем Ingress
kubectl describe ingress frontend-ingress
```

### Проблема: Приложение не запускается

```bash
# Проверяем поды
kubectl get pods
kubectl describe pod <pod-name>

# Проверяем логи
kubectl logs <pod-name>
```

### Проблема: Нет места на диске

```bash
# Очищаем неиспользуемые ресурсы
kubectl delete pods --field-selector=status.phase=Failed --all-namespaces
kubectl delete jobs --field-selector=status.successful=1 --all-namespaces
```

## 📝 Быстрые команды

```bash
# Развертывание
skaffold run                    # Продакшен
skaffold dev                    # Разработка

# Проверка
kubectl get all                 # Все ресурсы
kubectl get ingress            # Ingress
kubectl get pods               # Поды

# Логи
kubectl logs -l app=frontend -f
kubectl logs -l app=scrapers-api -f

# Удаление
skaffold delete                 # Удалить все
```

## 🎯 Результат

После выполнения у вас будет:

✅ **Работающий кластер** с приложением  
✅ **Ingress** для доступа извне  
✅ **Автоматическое масштабирование**  
✅ **Мониторинг** и логи  
✅ **Готовность к продакшену**  

## 💰 Стоимость

- **GKE**: ~$50-100/месяц (3 ноды)
- **EKS**: ~$70-120/месяц (3 ноды)  
- **AKS**: ~$60-110/месяц (3 ноды)

*Цены примерные, зависят от региона и настроек*
