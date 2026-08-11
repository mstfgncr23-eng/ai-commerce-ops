# AI Commerce Ops · Live Demo

Public portfolio surface for the AI Commerce Ops project.

## What it demonstrates

- controlled product intake presets
- LangChain structured enrichment using `gpt-5.6-luna`
- deterministic human-in-the-loop risk gate
- optional PostgreSQL/Supabase audit persistence
- Shopify Admin GraphQL DRAFT upsert via `productSet`
- optional handoff to an n8n Cloud production webhook

## Vercel root directory

Set the Vercel project **Root Directory** to `live-demo`.

## Required environment variables

Copy the values from your private local environment into Vercel project settings. Never commit the real secrets.

```text
OPENAI_API_KEY
OPENAI_MODEL=gpt-5.6-luna
SHOPIFY_SHOP
SHOPIFY_CLIENT_ID
SHOPIFY_CLIENT_SECRET
SHOPIFY_API_VERSION=2026-07
```

Optional:

```text
DATABASE_URL
N8N_WEBHOOK_URL
```

Without `N8N_WEBHOOK_URL`, `/api/run` executes the same stages directly so the deployment can be verified before n8n Cloud is connected. The UI reports the orchestrator mode instead of pretending n8n ran.
