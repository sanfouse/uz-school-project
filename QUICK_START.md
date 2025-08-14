# ⚡ Быстрый старт на облачном кластере

## 🚀 Развертывание за 3 команды

### 1. Создайте кластер (выберите один)

```bash
# Google Cloud (GKE)
gcloud container clusters create scraper-cluster --zone=europe-west1-b --num-nodes=3 --machine-type=e2-standard-2
gcloud container clusters get-credentials scraper-cluster --zone=europe-west1-b

# AWS (EKS)
eksctl create cluster --name scraper-cluster --region eu-west-1 --nodegroup-name workers --node-type t3.medium --nodes 3
aws eks update-kubeconfig --region eu-west-1 --name scraper-cluster

# Azure (AKS)
az aks create --resource-group scraper-rg --name scraper-cluster --node-count 3 --node-vm-size Standard_B2s
az aks get-credentials --resource-group scraper-rg --name scraper-cluster
```

### 2. Запустите автоматическое развертывание

```bash
./deploy-cloud.sh
```

### 3. Настройте домен (опционально)

```bash
./create-prod-config.sh
skaffold run -f skaffold-prod.yaml
```

## 🎯 Что получите

✅ **Работающее приложение** за 5 минут  
✅ **Ingress** для доступа извне  
✅ **Автоматическое масштабирование**  
✅ **Готовность к продакшену**  

## 📱 Доступ к приложению

После развертывания:

1. **Получите внешний IP:**
   ```bash
   kubectl get service -n ingress-nginx ingress-nginx-controller
   ```

2. **Откройте в браузере:**
   ```
   http://<EXTERNAL-IP>
   ```

## 🔧 Полезные команды

```bash
# Статус
kubectl get all
kubectl get ingress

# Логи
kubectl logs -l app=frontend -f
kubectl logs -l app=scrapers-api -f

# Удаление
skaffold delete
```

## 💰 Стоимость

- **GKE**: ~$50-100/месяц
- **EKS**: ~$70-120/месяц  
- **AKS**: ~$60-110/месяц

## 📚 Подробная документация

См. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) для детального описания.
