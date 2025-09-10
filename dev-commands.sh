#!/bin/bash

# Script de comandos úteis para desenvolvimento
# Use: ./dev-commands.sh <comando>

case "$1" in
    "setup")
        echo "🚀 Configurando ambiente..."
        ./setup-docker.sh
        ;;
    "start")
        echo "▶️ Iniciando serviços..."
        docker-compose up -d
        ;;
    "stop")
        echo "⏹️ Parando serviços..."
        docker-compose down
        ;;
    "restart")
        echo "🔄 Reiniciando serviços..."
        docker-compose restart
        ;;
    "logs")
        echo "📋 Visualizando logs..."
        docker-compose logs -f
        ;;
    "shell")
        echo "🐚 Abrindo shell Django..."
        docker-compose exec backend python manage.py shell
        ;;
    "bash")
        echo "💻 Abrindo bash do container..."
        docker-compose exec backend bash
        ;;
    "migrate")
        echo "🗄️ Executando migrações..."
        docker-compose exec backend python manage.py migrate
        ;;
    "superuser")
        echo "👤 Criando superusuário..."
        docker-compose exec backend python manage.py createsuperuser
        ;;
    "collectstatic")
        echo "📁 Coletando arquivos estáticos..."
        docker-compose exec backend python manage.py collectstatic --noinput
        ;;
    "rebuild")
        echo "🔨 Rebuild completo..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        ;;
    "clean")
        echo "🧹 Limpando containers e volumes..."
        docker-compose down -v
        docker system prune -f
        ;;
    "status")
        echo "📊 Status dos containers..."
        docker-compose ps
        ;;
    "test")
        echo "🧪 Executando testes..."
        docker-compose exec backend python manage.py test
        ;;
    *)
        echo "🛠️ Comandos disponíveis:"
        echo "  setup      - Configurar ambiente inicial"
        echo "  start      - Iniciar serviços"
        echo "  stop       - Parar serviços"
        echo "  restart    - Reiniciar serviços"
        echo "  logs       - Ver logs em tempo real"
        echo "  shell      - Shell Django"
        echo "  bash       - Bash do container"
        echo "  migrate    - Executar migrações"
        echo "  superuser  - Criar superusuário"
        echo "  collectstatic - Coletar arquivos estáticos"
        echo "  rebuild    - Rebuild completo"
        echo "  clean      - Limpar containers e volumes"
        echo "  status     - Status dos containers"
        echo "  test       - Executar testes"
        echo ""
        echo "Uso: ./dev-commands.sh <comando>"
        ;;
esac
