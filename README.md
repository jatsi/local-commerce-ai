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


## Probar flujo completo (end-to-end)

1) Levanta la plataforma:
```bash
cp .env.example .env
./scripts/bootstrap.sh
```

2) Crea un job con el flujo dropshipping:
```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "dropshipping_flow",
    "payload": {
      "niches": ["cosmeticos", "electronicos"],
      "max_products_per_niche": 2,
      "campaign_name": "Lanzamiento Mayo",
      "ads_budget": {"google": 120, "facebook": 90, "tiktok": 80},
      "social_channels": ["youtube", "tiktok", "facebook_reels"],
      "inbox_messages": [
        "¿Cuanto tarda el envio?",
        "¿Tienen garantia?"
      ]
    }
  }'
```

3) Consulta el estado del job (reemplaza `<JOB_ID>`):
```bash
curl http://localhost:8000/jobs
curl http://localhost:8000/jobs/<JOB_ID>
```

4) Verifica en la respuesta `result.context` que hayan corrido estos pasos:
- `niche_analysis` (productos tendencia por nicho)
- `ads` (campañas Google/Facebook/TikTok + presupuesto total)
- `shopify` (publicación de producto vía conector)
- `email_support` (respuestas a inbox)
- `wan_assets` (assets de anuncios)
- `social_distribution` (programación en redes)
- `analytics` (métricas de cierre)

5) (Opcional) pruebas rápidas de código:
```bash
PYTHONPATH=. pytest -q tests/unit/test_planner.py
```

> Nota: la compra de dominio, publicación real en cuentas productivas de Ads/Shopify y subida real a redes depende de credenciales externas y conectores en modo producción.

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
