#!/bin/bash

echo "🚀 Configurando ambiente de desenvolvimento Sintonar..."

# Criar arquivo .env se não existir
if [ ! -f .env ]; then
    echo "📄 Criando arquivo .env baseado no .env.docker..."
    cp .env.docker .env
    echo "✅ Arquivo .env criado! Ajuste as configurações conforme necessário."
fi

# Build e start dos containers
echo "🔨 Fazendo build dos containers..."
docker-compose build

echo "🚀 Iniciando serviços..."
docker-compose up -d postgres redis

echo "⏳ Aguardando PostgreSQL e Redis ficarem prontos..."
sleep 10

echo "🗄️ Executando migrações..."
docker-compose run --rm backend python manage.py migrate

echo "👤 Criando superusuário (opcional)..."
echo "Deseja criar um superusuário? (y/n)"
read -r create_superuser
if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    docker-compose run --rm backend python manage.py createsuperuser
fi

echo "🚀 Iniciando todos os serviços..."
docker-compose up -d

echo ""
echo "✅ Ambiente configurado com sucesso!"
echo ""
echo "🌐 Serviços disponíveis:"
echo "   - API Django: http://localhost:8000"
echo "   - Admin Django: http://localhost:8000/admin"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
echo ""
echo "📋 Comandos úteis:"
echo "   - Ver logs: docker-compose logs -f"
echo "   - Parar serviços: docker-compose down"
echo "   - Restart: docker-compose restart"
echo "   - Shell Django: docker-compose exec backend python manage.py shell"
echo "   - Bash container: docker-compose exec backend bash"
echo ""
echo "🎉 Bom desenvolvimento!"
