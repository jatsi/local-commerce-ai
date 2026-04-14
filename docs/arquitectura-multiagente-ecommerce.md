# Arquitectura completa para un sistema multiagente local de e-commerce

## 1. Objetivo del sistema

El sistema se diseña como una **plataforma de orquestación**, no como un único agente monolítico. La plataforma incluye:

- Orquestador central.
- Agentes especializados por dominio.
- Capa de conectores para APIs externas.
- Memoria operativa (estado + memoria semántica).
- Capa de seguridad, revisión y auditoría.
- Capa de ejecución programada y por eventos.

Todo puede operar localmente, pero las acciones sobre Shopify, Etsy y Ads se realizan por APIs oficiales.

## 2. Vista general de arquitectura

```text
┌──────────────────────────────────────────────────────────────┐
│                     PANEL DE CONTROL LOCAL                   │
│  Dashboard / Aprobaciones / Logs / KPIs / Jobs / Alertas    │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    API GATEWAY (FASTAPI)                    │
│  Auth local | Webhooks | REST interno | UI backend | RBAC   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│                    ORQUESTADOR CENTRAL                       │
│  Planner | Router | Policy Engine | Scheduler | Executor    │
└──────────────────────────────────────────────────────────────┘
      │                 │                 │                 │
      ▼                 ▼                 ▼                 ▼
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
│ Agente     │   │ Agente     │   │ Agente     │   │ Agente     │
│ Catálogo   │   │ Contenido  │   │ Competencia│   │ Ads        │
└────────────┘   └────────────┘   └────────────┘   └────────────┘
      │                 │                 │                 │
      ▼                 ▼                 ▼                 ▼
┌────────────┐   ┌────────────┐   ┌────────────┐   ┌────────────┐
│ Agente     │   │ Agente Web │   │ Agente     │   │ Agente     │
│ Shopify    │   │ / SEO      │   │ Etsy       │   │ Analytics  │
└────────────┘   └────────────┘   └────────────┘   └────────────┘
      │                 │                 │                 │
      └──────────────┬──┴───────────┬─────┴───────────┬─────┘
                     ▼              ▼                 ▼
         ┌────────────────┐ ┌───────────────┐ ┌───────────────┐
         │ PostgreSQL     │ │ Qdrant/Vector │ │ Redis / Queue │
         │ estado y logs  │ │ memoria RAG   │ │ jobs y locks  │
         └────────────────┘ └───────────────┘ └───────────────┘
                     │              │                 │
                     ▼              ▼                 ▼
              ┌────────────┐  ┌────────────┐   ┌───────────────┐
              │ Ollama     │  │ Playwright │   │ Workers/CRON  │
              │ modelos IA │  │ scraping   │   │ tareas        │
              └────────────┘  └────────────┘   └───────────────┘
```

## 3. Componentes principales

### 3.1 API Gateway / Backend central

**Responsabilidad**
- Recibir órdenes del dashboard.
- Exponer endpoints internos.
- Validar autenticación y roles.
- Recibir webhooks de Shopify.
- Exponer jobs, métricas y aprobaciones.
- Centralizar logs.

**Tecnología**
- FastAPI
- Uvicorn / Gunicorn
- Pydantic
- JWT local o autenticación detrás de reverse proxy

**Endpoints sugeridos**
```text
POST   /jobs/create
GET    /jobs/{id}
POST   /approvals/{id}/approve
POST   /approvals/{id}/reject
POST   /webhooks/shopify
POST   /agents/run/{agent_name}
GET    /products/master/{sku}
GET    /analytics/dashboard
POST   /campaigns/propose
POST   /campaigns/execute
```

### 3.2 Orquestador central

Submódulos recomendados:
- `planner`
- `task_router`
- `policy_engine`
- `approval_gate`
- `job_executor`
- `event_handler`
- `scheduler`

Funciones:
- Planificar tareas y dividir objetivos.
- Enrutar subtareas a agentes.
- Imponer políticas y pedir aprobación humana en acciones de riesgo.
- Reintentar fallos y encadenar workflows.

### 3.3 Capa de agentes

- **Catálogo Maestro**: fuente de verdad del producto.
- **Shopify**: traducción y sincronización para Shopify.
- **Etsy**: adaptación a taxonomía y reglas Etsy.
- **Web/SEO**: landing pages, blog, bloques home, FAQ.
- **Contenido**: copy para canales, ads y soporte SEO.
- **Competencia**: scraping público, snapshots y tendencias.
- **Ads**: propuestas, ajustes controlados y reportes.
- **Analytics**: métricas de rendimiento y optimización.
- **Cumplimiento**: políticas, bloqueo de riesgo y auditoría.

## 4. Capas de datos

### 4.1 PostgreSQL (estado estructurado)
Tablas clave:
- `products_master`
- `product_channel_versions`
- `product_assets`
- `jobs`
- `job_steps`
- `approvals`
- `audit_logs`
- `campaigns`
- `analytics_snapshots`
- `competitor_snapshots`

### 4.2 Qdrant (memoria semántica)
Casos de uso:
- RAG sobre fichas históricas, FAQs y políticas.
- Recuperación de campañas ganadoras y benchmarks.
- Reutilización de prompts y documentos técnicos.

### 4.3 Redis (cola y coordinación)
- Jobs, locks, cache corta, rate-limits y retries.

## 5. Model serving local

### 5.1 Ollama
Separación recomendada por rol:
- Planner model.
- Writer model.
- Critic model.
- Classifier model.
- Embedder model.

## 6. Conectores

- **Shopify Connector**: productos, inventario, colecciones, webhooks, publicación.
- **Etsy Connector**: drafts, inventory, imágenes, taxonomía, publicación.
- **Web Connector**: landing/blog/pages según stack.
- **Ads Connectors**: módulos separados para Meta y Google Ads.

## 7. Scheduler y eventos

Dos tipos de disparadores:
- **Tiempo**: tareas periódicas (KPIs, competencia, reindexación).
- **Eventos**: webhooks, cambios de stock, aprobaciones, cambios de precio.

## 8. Políticas de control

### Sin aprobación humana
- Crear borradores.
- Generar copy/assets.
- Scraping público.
- Proponer cambios.

### Con aprobación humana
- Publicar productos/listings.
- Cambios masivos de precio.
- Incrementos de presupuesto > X%.
- Archivado/borrado en canales productivos.

### Regla de rollback
Cada publicación debe persistir:
- Before
- After
- Payload enviado
- Respuesta API
- Responsable (usuario/agente)

## 9. Flujo de trabajo completo (tracker nuevo)

1. Ingreso de especificación.
2. Creación de job por orquestador.
3. Ficha maestra (catálogo).
4. Benchmark competencia.
5. Enriquecimiento de contenido.
6. Generación de assets.
7. Draft Shopify.
8. Draft Etsy.
9. Landing web.
10. Validación de cumplimiento.
11. Solicitud de aprobación.
12. Publicación tras aprobación.
13. Inicio de seguimiento analytics.
14. Propuesta de Ads (con aprobación para gasto).

## 10. Estructura de carpetas recomendada

```text
local-commerce-ai/
├── apps/
├── core/
├── orchestrator/
├── agents/
├── connectors/
├── memory/
├── models/
├── data/
├── infra/
├── tests/
├── scripts/
├── .env
├── docker-compose.yml
└── README.md
```

## 11. Docker Compose base

El `docker-compose.yml` debe incluir como mínimo:
- `api`
- `worker`
- `scheduler`
- `dashboard`
- `postgres`
- `redis`
- `qdrant`
- `ollama`

Con volúmenes persistentes para Postgres, Qdrant y Ollama.

## 12. Contratos internos entre agentes

Entrada estándar por tarea:
- `job_id`
- `task_type`
- `context`
- `constraints`
- `memory_refs`

Respuesta estándar:
- `job_id`
- `agent`
- `status`
- `result`
- `audit_ref`

## 13. Base de datos mínima inicial

- `products_master`
- `product_assets`
- `product_channel_versions`
- `jobs`
- `job_steps`
- `approvals`
- `audit_logs`
- `competitor_snapshots`
- `campaigns`
- `analytics_snapshots`
- `settings`

## 14. Dashboard recomendado

Vistas mínimas:
- Operaciones
- Productos
- Competencia
- Ads
- Auditoría

## 15. Seguridad

- Segmentación de secretos por plataforma.
- RBAC por perfiles (`admin`, `editor`, `reviewer`, `read_only`, `agent_service`).
- Idempotencia en jobs y webhooks.
- Rate limiting interno por conector/API.

## 16. Observabilidad

- Logs estructurados JSON.
- Métricas Prometheus.
- Trazabilidad por `job_id`.
- Grafana + alertas operativas (publicación, presupuesto ads).

## 17. MVP por fases

- **Fase 1**: FastAPI + Postgres + Redis + Ollama + Shopify + aprobación humana.
- **Fase 2**: Etsy + contenido + competencia + Qdrant (RAG).
- **Fase 3**: Web/SEO + Ads con límites + analytics avanzado.
- **Fase 4**: Optimización continua, A/B testing, scoring predictivo.

## 18. Recomendación final de implementación

- Backend: FastAPI.
- Orquestación: Python + workers + Redis.
- LLM local: Ollama.
- DB principal: PostgreSQL.
- Memoria semántica: Qdrant.
- Scraping: Playwright.
- UI: React/Next.js.
- Infra inicial: Docker Compose.
- Integraciones productivas: Shopify GraphQL + Etsy Open API v3.
- Guardrails: aprobación humana para publicación y gasto ads.
