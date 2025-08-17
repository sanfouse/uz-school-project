#!/bin/bash

echo "📊 Мониторинг ресурсов Kubernetes Job"
echo ""

# Проверяем аргументы
if [ $# -eq 0 ]; then
    echo "Использование: $0 <имя_джобы>"
    echo "Пример: $0 profi-scraper-job-test-123"
    exit 1
fi

JOB_NAME=$1

echo "🔍 Ищем поды для Job: $JOB_NAME"
echo "=================================="

# Получаем поды Job
PODS=$(kubectl get pods -l job-name=$JOB_NAME -o jsonpath='{.items[*].metadata.name}')

if [ -z "$PODS" ]; then
    echo "❌ Поды для Job '$JOB_NAME' не найдены"
    echo ""
    echo "💡 Возможные причины:"
    echo "   - Job еще не создан"
    echo "   - Job завершился и поды удалены"
    echo "   - Неправильное имя Job"
    echo ""
    echo "🔍 Доступные Jobs:"
    kubectl get jobs
    exit 1
fi

echo "✅ Найдены поды: $PODS"
echo ""

# Мониторинг ресурсов для каждого пода
for POD in $PODS; do
    echo "📊 Ресурсы пода: $POD"
    echo "----------------------------------"
    
    # Статус пода
    echo "📋 Статус:"
    kubectl get pod $POD -o wide
    
    echo ""
    
    # Использование ресурсов
    echo "💾 Использование ресурсов:"
    kubectl top pod $POD 2>/dev/null || echo "   Не удалось получить метрики (возможно под еще запускается)"
    
    echo ""
    
    # Детальная информация
    echo "🔍 Детальная информация:"
    kubectl describe pod $POD | grep -E "(Status:|Events:|Containers:|Resources:)" | head -20
    
    echo ""
    echo "=================================="
    echo ""
done

echo "🚀 Команды для дальнейшего мониторинга:"
echo "   kubectl logs $PODS                    # Логи пода"
echo "   kubectl exec -it $PODS -- /bin/bash   # Войти в под"
echo "   watch -n 5 'kubectl top pod $PODS'    # Постоянный мониторинг"
echo "   kubectl get events --sort-by='.lastTimestamp'  # События кластера"
