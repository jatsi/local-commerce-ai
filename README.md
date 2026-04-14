# Local Commerce AI (Multiagente local)

Sistema modular multiagente para operar Shopify, Etsy, web propia, scraping de competencia, generación de contenido local (Ollama), ads y analytics.

## Stack
- Python 3.11
- FastAPI
- SQLAlchemy 2.0 + Alembic
- PostgreSQL
- Redis + Celery
- Qdrant
- Ollama
- Playwright
- httpx
- Docker Compose
- React dashboard interno

## Arquitectura
- **API Gateway**: FastAPI con endpoints de jobs, aprobaciones y dashboard.
- **Orquestador**: planifica y ejecuta pasos por agentes.
- **Agentes**: catalog, content, shopify, etsy, web, competitor, ads, analytics, compliance.
- **Conectores**: Shopify, Etsy, web CMS, Google Ads, Meta Ads, Playwright, Ollama, Qdrant.
- **Persistencia**: tablas requeridas y auditoría.
- **Aprobaciones humanas**: gate por políticas.
- **Policy engine**: evaluación de riesgo y compliance.
- **RAG**: recuperación contextual en Qdrant para contenido.
- **Scraping**: Playwright vía conector encapsulado.
- **Competitor agent**: scraping web + análisis heurístico de precio/keywords para proponer mejoras en páginas de venta.
- **Dashboard**: React para estado de jobs/aprobaciones.

## Ejecutar
```bash
cp .env.example .env
./scripts/bootstrap.sh
```

Servicios:
- API: http://localhost:8000
- Dashboard: http://localhost:5173
- Qdrant: http://localhost:6333/dashboard

## Migraciones
```bash
docker compose exec api alembic upgrade head
```

## Tests
```bash
pytest -q
```

## Documento de arquitectura detallado
- Ver `docs/arquitectura-multiagente-ecommerce.md` para la propuesta completa por capas, políticas, contratos y roadmap por fases.


## ¿Dónde pongo las URLs de competidores?
Puedes pasarlas de dos formas:

1. **Por job payload (recomendado)** en `payload.competitor_urls`:
```json
{
  "name": "launch_product",
  "payload": {
    "product": {"title": "Mi tracker", "price": 39.9},
    "competitor_urls": [
      "https://competidor.com/producto-a",
      "https://competidor.com/producto-b"
    ]
  }
}
```

2. **Por variable de entorno** `COMPETITOR_URLS` en `.env` (separadas por coma), útil como fallback global.
