# Local Commerce AI Base — siguiente capa

Esta versión agrega:

- persistencia real inicial con **SQLAlchemy 2.0**
- cola de jobs con **Celery + Redis**
- endpoints para jobs, approvals y products
- modelos de base de datos iniciales
- conectores Shopify y Etsy en modo **stub_ready**
- arranque automático de tablas al iniciar la API

## Componentes nuevos

### Base de datos
Modelos incluidos:

- `jobs`
- `approvals`
- `products_master`
- `product_channel_versions`

### Cola de jobs
La API ya no procesa el job directamente. Ahora:

1. crea el job en PostgreSQL
2. lo encola en Celery
3. el worker lo procesa
4. el resultado vuelve a la tabla `jobs`

### Integración inicial Shopify
El conector deja preparado el payload para `productCreate` en GraphQL Admin API.

### Integración inicial Etsy
El conector deja preparado el payload para el endpoint base de listings de Etsy Open API v3.

## Cómo iniciar

```bash
cp .env.example .env
docker compose up --build
```

## Endpoints

- `GET /health`
- `POST /jobs/create`
- `GET /jobs/{job_id}`
- `GET /approvals/{approval_id}`
- `POST /approvals/{approval_id}/approve`
- `POST /approvals/{approval_id}/reject`
- `GET /products/master`
- `GET /products/channels`

## Ejemplo para crear job

```bash
curl -X POST http://localhost:8000/jobs/create \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "publish_product",
    "context": {
      "sku": "TRK-001",
      "title": "IMU Tracker Pro"
    },
    "constraints": {
      "require_approval": true
    }
  }'
```

## Qué falta todavía

- relaciones ORM más completas
- Alembic con migraciones reales
- aprobaciones generadas automáticamente por políticas
- persistir catálogo maestro desde agentes
- cliente real Shopify con `httpx`
- cliente real Etsy con OAuth refresh flow
- panel frontend de aprobaciones
- auditoría detallada
- integración real de Ollama / embeddings / Qdrant

## Referencias de implementación

La estructura está pensada para trabajar con:

- SQLAlchemy ORM 2.0 style
- Celery usando Redis como broker/backend
- Shopify Admin GraphQL
- Etsy Open API v3

