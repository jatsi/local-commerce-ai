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

Este flujo crea un job asíncrono y lo ejecuta con el orquestador. El orden actual es:

1. `niche_analytics`: detecta productos tendencia por nicho.
2. `ads`: arma campañas y presupuesto por canal.
3. `content`: genera título/copy comercial con Ollama antes de Shopify.
4. `shopify`: crea o actualiza el producto en Shopify usando la Admin API real.
5. `email`: responde mensajes básicos de soporte.
6. `wan_creator`: genera la metadata de assets de anuncios que ya existía en el proyecto.
7. `wan_publisher`: agenda esos assets en canales sociales configurados.
8. `analytics`: agrega métricas finales del flujo.

> Importante: Shopify ya no responde como simulación. Si `SHOPIFY_STORE` o `SHOPIFY_ACCESS_TOKEN` no están configurados, el job falla en el paso `shopify` con un error de configuración.

### 1) Configura variables de entorno

Copia el ejemplo y edita `.env`:

```bash
cp .env.example .env
```

Variables mínimas para que el flujo llegue a Shopify real:

```dotenv
SHOPIFY_STORE=tu-tienda.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SHOPIFY_API_VERSION=2026-01
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
```

Notas:

- `SHOPIFY_STORE` debe ser el dominio `.myshopify.com`, sin `https://`.
- `SHOPIFY_ACCESS_TOKEN` debe tener permisos de Admin API para crear/editar productos.
- Si quieres actualizar un producto existente en lugar de crear uno nuevo, envía `shopify_product_id` en el payload.
- Ollama debe tener descargado el modelo configurado, por ejemplo:

```bash
ollama pull llama3.1:8b
```

### 2) Levanta servicios

```bash
./scripts/bootstrap.sh
```

Si estás usando Docker Compose, aplica migraciones cuando los servicios estén arriba:

```bash
docker compose exec api alembic upgrade head
```

### 3) Crea un job completo

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "name": "dropshipping_flow",
    "payload": {
      "niches": ["electronicos", "accesorios_auto"],
      "max_products_per_niche": 2,
      "product": {
        "title": "Tracker GPS para Auto",
        "description": "Localizador compacto para monitoreo del vehículo.",
        "price": 39.9,
        "compare_at_price": 59.9,
        "sku": "GPS-AUTO-001",
        "vendor": "Local Commerce AI",
        "product_type": "Accesorios para auto",
        "tags": ["gps", "auto", "seguridad"],
        "image_url": "https://cdn.example.com/products/gps-auto.jpg",
        "benefits": [
          "Monitoreo práctico para el vehículo.",
          "Presentación clara orientada a conversión.",
          "Ideal para clientes que buscan seguridad y control."
        ]
      },
      "campaign_name": "Lanzamiento GPS Auto",
      "ads_budget": {"google": 120, "facebook": 90, "tiktok": 80},
      "social_channels": ["youtube", "tiktok", "facebook_reels"],
      "inbox_messages": [
        "¿Cuánto tarda el envío?",
        "¿Tienen garantía?"
      ]
    }
  }'
```

Respuesta inmediata esperada:

```json
{
  "job_id": "6f5d8a9a-1111-4444-8888-123456789abc",
  "status": "queued"
}
```

### 4) Consulta estado y resultado

Lista los jobs recientes:

```bash
curl http://localhost:8000/jobs
```

Consulta el detalle del job con el `job_id` devuelto al crearlo:

```bash
curl http://localhost:8000/jobs/6f5d8a9a-1111-4444-8888-123456789abc
```

### 5) Ejemplo de respuesta esperada del flujo completo

Cuando el worker termina correctamente, el detalle del job debe verse así. Los IDs, textos generados por Ollama, métricas y datos devueltos por Shopify cambian en cada ejecución:

```json
{
  "id": "6f5d8a9a-1111-4444-8888-123456789abc",
  "name": "dropshipping_flow",
  "status": "completed",
  "payload": {
    "niches": ["electronicos", "accesorios_auto"],
    "max_products_per_niche": 2,
    "product": {
      "title": "Tracker GPS para Auto",
      "description": "Localizador compacto para monitoreo del vehículo.",
      "price": 39.9,
      "compare_at_price": 59.9,
      "sku": "GPS-AUTO-001"
    },
    "campaign_name": "Lanzamiento GPS Auto",
    "ads_budget": {"google": 120, "facebook": 90, "tiktok": 80},
    "social_channels": ["youtube", "tiktok", "facebook_reels"],
    "inbox_messages": ["¿Cuánto tarda el envío?", "¿Tienen garantía?"]
  },
  "result": {
    "job": "dropshipping_flow",
    "executed": [
      {
        "agent": "niche_analytics",
        "result": {
          "niche_analysis": {
            "niches": ["electronicos", "accesorios_auto"],
            "trending_products": {
              "electronicos": ["electronicos-trend-1", "electronicos-trend-2"],
              "accesorios_auto": ["accesorios_auto-trend-1", "accesorios_auto-trend-2"]
            },
            "source": "marketplace+competitor_signals"
          }
        }
      },
      {
        "agent": "ads",
        "result": {
          "ads": {
            "google": {
              "status": "stub_ready",
              "platform": "google_ads",
              "campaign": {"name": "Lanzamiento GPS Auto", "budget": 120}
            },
            "facebook": {
              "status": "stub_ready",
              "platform": "meta_ads",
              "campaign": {"name": "Lanzamiento GPS Auto", "budget": 90}
            },
            "tiktok": {
              "platform": "tiktok",
              "campaign_name": "Lanzamiento GPS Auto",
              "budget": 80,
              "status": "created"
            },
            "total_budget": 290
          }
        }
      },
      {
        "agent": "content",
        "result": {
          "content": {
            "title": "Tracker GPS para Auto Premium",
            "copy": "Copy comercial generado por Ollama para destacar beneficios, confianza y compra.",
            "references": [
              {
                "source": "knowledge_base",
                "snippet": "context for Tracker GPS para Auto"
              }
            ]
          },
          "product_marketing": {
            "title": "Tracker GPS para Auto Premium"
          }
        }
      },
      {
        "agent": "shopify",
        "result": {
          "shopify": {
            "status": "published",
            "channel": "shopify",
            "endpoint": "https://tu-tienda.myshopify.com/admin/api/2026-01/products.json",
            "product": {
              "id": 987654321,
              "title": "Tracker GPS para Auto Premium",
              "status": "active",
              "variants": [{"id": 123456789, "sku": "GPS-AUTO-001", "price": "39.9"}]
            },
            "request_product": {
              "title": "Tracker GPS para Auto Premium",
              "body_html": "<section class='ai-product-hero'>...</section>",
              "status": "active",
              "tags": "gps, auto, seguridad, electronicos, accesorios_auto, ai-optimized, shopify",
              "variants": [{"price": "39.9", "compare_at_price": "59.9", "sku": "GPS-AUTO-001"}],
              "images": [{"src": "https://cdn.example.com/products/gps-auto.jpg"}]
            }
          }
        }
      },
      {
        "agent": "email",
        "result": {
          "email_support": {
            "answered": [
              {
                "question": "¿Cuánto tarda el envío?",
                "answer": "Gracias por escribirnos. Te respondemos con soporte comercial."
              },
              {
                "question": "¿Tienen garantía?",
                "answer": "Gracias por escribirnos. Te respondemos con soporte comercial."
              }
            ],
            "count": 2
          }
        }
      },
      {
        "agent": "wan_creator",
        "result": {
          "wan_assets": [
            {"niche": "electronicos", "product": "electronicos-trend-1", "asset": "wan_ad_electronicos_1.mp4"},
            {"niche": "electronicos", "product": "electronicos-trend-2", "asset": "wan_ad_electronicos_2.mp4"},
            {"niche": "accesorios_auto", "product": "accesorios_auto-trend-1", "asset": "wan_ad_accesorios_auto_1.mp4"},
            {"niche": "accesorios_auto", "product": "accesorios_auto-trend-2", "asset": "wan_ad_accesorios_auto_2.mp4"}
          ]
        }
      },
      {
        "agent": "wan_publisher",
        "result": {
          "social_distribution": [
            {"asset": "wan_ad_electronicos_1.mp4", "channels": ["youtube", "tiktok", "facebook_reels"], "status": "scheduled"},
            {"asset": "wan_ad_electronicos_2.mp4", "channels": ["youtube", "tiktok", "facebook_reels"], "status": "scheduled"}
          ]
        }
      },
      {
        "agent": "analytics",
        "result": {
          "analytics": {
            "roas": 2.1,
            "ctr": 0.042,
            "status": "tracked"
          }
        }
      }
    ],
    "context": {
      "niches": ["electronicos", "accesorios_auto"],
      "product": {"title": "Tracker GPS para Auto", "price": 39.9, "sku": "GPS-AUTO-001"},
      "niche_analysis": {"niches": ["electronicos", "accesorios_auto"]},
      "ads": {"total_budget": 290},
      "content": {"title": "Tracker GPS para Auto Premium"},
      "product_marketing": {"title": "Tracker GPS para Auto Premium"},
      "shopify": {"status": "published", "channel": "shopify"},
      "email_support": {"count": 2},
      "wan_assets": [{"asset": "wan_ad_electronicos_1.mp4"}],
      "social_distribution": [{"asset": "wan_ad_electronicos_1.mp4", "status": "scheduled"}],
      "analytics": {"roas": 2.1, "ctr": 0.042, "status": "tracked"}
    }
  },
  "steps": [
    {"agent": "niche_analytics", "order": 1, "status": "completed"},
    {"agent": "ads", "order": 2, "status": "completed"},
    {"agent": "content", "order": 3, "status": "completed"},
    {"agent": "shopify", "order": 4, "status": "completed"},
    {"agent": "email", "order": 5, "status": "completed"},
    {"agent": "wan_creator", "order": 6, "status": "completed"},
    {"agent": "wan_publisher", "order": 7, "status": "completed"},
    {"agent": "analytics", "order": 8, "status": "completed"}
  ]
}
```

### 6) Si el job falla en Shopify

Si las credenciales no están configuradas, el worker marcará el job como `failed`. Revisa:

```bash
curl http://localhost:8000/jobs/<JOB_ID>
```

Causas comunes:

- `SHOPIFY_STORE` sigue en `your-store.myshopify.com`.
- `SHOPIFY_ACCESS_TOKEN` está vacío o es inválido.
- El token no tiene permisos para escribir productos.
- `SHOPIFY_API_VERSION` no coincide con una versión disponible.

### 7) Pruebas rápidas de código

```bash
PYTHONPATH=. pytest -q tests/unit/test_planner.py tests/unit/test_shopify_client.py tests/unit/test_content_agent.py
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
