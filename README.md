# 🐳 Docker Development Setup

Este guia te ajudará a configurar rapidamente o ambiente de desenvolvimento usando Docker.

## 🚀 Setup Rápido

```bash
# 1. Clone o repositório (se ainda não fez)
git clone <repo-url>
cd sintonar-mvp-api

# 2. Execute o script de setup
./setup-docker.sh
```

## 📋 Serviços Incluídos

- **PostgreSQL 15**: Banco de dados principal
- **Redis 7**: Cache e broker para Celery  
- **Django Backend**: API principal na porta 8000
- **Celery Worker**: Processamento de tarefas em background
- **Celery Beat**: Agendador de tarefas

## 🔧 Comandos Úteis

### Gerenciamento dos containers
```bash
# Iniciar todos os serviços
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f backend

# Parar todos os serviços
docker-compose down

# Rebuild e restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Django Management
```bash
# Acessar shell do Django
docker-compose exec backend python manage.py shell

# Executar migrações
docker-compose exec backend python manage.py migrate

# Criar superusuário
docker-compose exec backend python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose exec backend python manage.py collectstatic

# Acessar bash do container
docker-compose exec backend bash
```

### Desenvolvimento
```bash
# Ver status dos containers
docker-compose ps

# Restart apenas um serviço
docker-compose restart backend

# Ver logs de erro
docker-compose logs backend | grep -i error
```

## 🌐 URLs de Desenvolvimento

- **API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/sintonar  
- **API Documentation**: http://localhost:8000/v1/schema/swagger-ui/

## ⚙️ Configuração

As configurações estão no arquivo `.env.docker` que é copiado para `.env` automaticamente. 

### Principais variáveis:
- `DEBUG=1`: Modo debug ativado
- `DATABASE_HOST=postgres`: Nome do serviço PostgreSQL
- `REDIS_HOST=redis`: Nome do serviço Redis
- `ALLOWED_HOSTS`: Hosts permitidos para desenvolvimento

## 🔍 Troubleshooting

### Problemas comuns:

1. **Porta já em uso**:
   ```bash
   # Verifique quais serviços estão usando as portas
   lsof -i :8000  # Django
   lsof -i :5432  # PostgreSQL  
   lsof -i :6379  # Redis
   ```

2. **Containers não iniciam**:
   ```bash
   # Rebuild completo
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **Problemas de permissão**:
   ```bash
   # Ajustar permissões dos arquivos
   sudo chown -R $USER:$USER .
   ```

4. **Limpar dados do banco**:
   ```bash
   # Remove volumes (CUIDADO: apaga todos os dados!)
   docker-compose down -v
   ```

## 🎯 Para Entrevistas

Este setup é otimizado para demonstrações rápidas:

1. **Setup em segundos**: `./setup-docker.sh`
2. **Todos os serviços funcionais**: PostgreSQL, Redis, Celery
3. **API pronta para testes**: Swagger UI disponível
4. **Logs acessíveis**: `docker-compose logs -f`

## 📝 Próximos Passos

1. Configure as variáveis de ambiente no `.env` conforme necessário
2. Execute `docker-compose exec backend python manage.py createsuperuser` para criar um admin
3. Acesse http://localhost:8000/sintonar para verificar se tudo está funcionando
4. Teste as APIs através do Swagger UI

Boa sorte na sua entrevista! 🚀
