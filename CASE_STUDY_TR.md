# AI Commerce Ops — Türkçe vaka özeti

**Canlı demo:** https://ai-commerce-ops-demo.vercel.app  
**GitHub:** https://github.com/mstfgncr23-eng/ai-commerce-ops

## Proje özeti

AI Commerce Ops, tedarikçiden gelen ürün verisini e-ticaret kataloğuna hazırlayan çok adımlı bir otomasyon demosudur. Sistem ürün bilgisini alır, LangChain + OpenAI ile yapılandırılmış içerik ve risk çıktısı üretir, n8n Cloud üzerinde karar dalına yönlendirir, sonucu Supabase PostgreSQL'e audit kaydı olarak yazar ve yalnızca güvenli senaryolarda Shopify'a `DRAFT` ürün olarak senkronize eder.

Amaç, tek prompt kullanan bir AI demosu yerine gerçek bir workflow mimarisini göstermekti: **al → zenginleştir → doğrula → kaydet → koşullu olarak Shopify'a yaz**.

## Canlı akış

```text
Browser / Vercel UI
        ↓
FastAPI /api/run
        ↓
n8n Cloud Webhook
        ↓
FastAPI /api/n8n/enrich
        ↓
LangChain + OpenAI structured output
        ↓
n8n Risk Gate
   ┌────┴────┐
   ↓         ↓
Human     Auto-draft
review       ↓
   └────┬────┘
        ↓
FastAPI /api/n8n/finalize
        ↓
Supabase PostgreSQL audit
        ↓
Server-side risk re-check
   ┌────┴────┐
   ↓         ↓
Blocked   Shopify GraphQL
             ↓
        Shopify DRAFT
```

## Neden bu mimari?

- **n8n Cloud:** webhook, akış görünürlüğü, branching ve HTTP node retry davranışı.
- **FastAPI:** API sınırlarını, iş mantığını ve entegrasyon katmanlarını ayrı tutmak.
- **LangChain + Pydantic:** model çıktısını serbest metin yerine doğrulanan structured output olarak almak.
- **Supabase PostgreSQL:** her çalışmanın ürün girdisini ve karar payload'ını kalıcı audit kaydı olarak saklamak.
- **Human-in-the-loop:** regüle veya yüksek riskli ürünlerin otomatik olarak Shopify'a geçmesini engellemek.
- **Shopify Admin GraphQL:** güvenli senaryolarda gerçek mağazaya yalnızca `DRAFT` durumunda ürün yazmak.
- **Vercel:** canlı demo arayüzü ile FastAPI backend'ini tek erişilebilir portföy demosunda sunmak.

## Karar mantığı

AI katmanı şu alanları structured output olarak üretir:

- kategori
- SEO title
- SEO description
- normalize edilmiş ürün açıklaması
- 0–100 risk skoru
- risk flag'leri

Ardından workflow iki seviyede korunur:

1. n8n, `approval_required` sonucuna göre insan onayı veya otomatik taslak dalına gider.
2. FastAPI finalize endpoint'i kararı sunucu tarafında tekrar hesaplar. Böylece değiştirilmiş bir istekle risk gate'in atlanması engellenir.

Regüle ürünler veya risk skoru `70+` olan ürünler insan incelemesine gider.

## Canlı demo senaryoları

### 1. Disposable Exam Table Paper

Düşük riskli klinik sarf malzemesi.

**Beklenen sonuç:**

```text
LangChain enrichment ✅
Risk gate: düşük risk ✅
Supabase PostgreSQL audit ✅
Shopify DRAFT upsert ✅
```

Shopify tarafında aynı SKU için sabit handle kullanılır. GraphQL `productSet` sayesinde tekrar çalıştırıldığında yeni kopyalar üretmek yerine aynı demo taslağı güncellenir.

### 2. Portable Patient Monitor

Regüle medikal cihaz ve tanısal izleme bağlamı içerir.

**Beklenen sonuç:**

```text
LangChain enrichment ✅
Risk gate: yüksek risk ⚠️
Human approval required ⚠️
Supabase PostgreSQL audit ✅
Shopify write blocked ✅
```

Bu senaryo, workflow'un her AI çıktısını kör şekilde downstream sisteme göndermediğini ve human-in-the-loop kontrolünün gerçekten çalıştığını gösterir.

### 3. Stainless Steel Clinic Trolley

Medikal iddia taşımayan klinik mobilyası.

**Beklenen sonuç:** düşük risk → audit → Shopify `DRAFT` upsert.

## Teknik olarak gösterilenler

- n8n Cloud üzerinde çok adımlı orchestration
- webhook tabanlı workflow tetikleme
- true/false branching ile insan onayı rotası
- HTTP node retry davranışı
- Python + FastAPI REST endpoint'leri
- LangChain structured output
- Pydantic schema validation
- OpenAI model entegrasyonu
- deterministic risk kuralı + AI risk sinyali
- server-side approval re-check
- Supabase PostgreSQL + JSONB audit persistence
- Shopify client credentials authentication
- Shopify Admin GraphQL `productSet`
- idempotent Shopify DRAFT upsert
- Vercel production deployment
- secret'ların environment variable üzerinden yönetilmesi

## Audit yapısı

Her finalize çalışması Supabase PostgreSQL'deki `product_automation_audit` tablosuna aşağıdaki bilgileri yazar:

```text
request_id
sku
input_payload
decision_payload
created_at
updated_at
```

`input_payload`, workflow'a giren ürün verisini; `decision_payload` ise enrichment sonucu ile `approval_required` kararını saklar. Audit kayıtları böylece her execution için izlenebilir bir karar geçmişi oluşturur.

## Shopify güvenlik sınırı

Demo hiçbir ürünü otomatik olarak `ACTIVE` veya yayınlanmış duruma getirmez. Shopify yazma işlemleri yalnızca `DRAFT` ile sınırlıdır.

Ayrıca riskli senaryoda Shopify API çağrısı yapılmadan önce akış durdurulur. Bu sayede demo, yalnızca API entegrasyonunu değil, kontrollü otomasyon mantığını da gösterir.

## Demo kontrollü olan kısım

Ürün seçenekleri portföy demosunun tekrar edilebilir olması için önceden tanımlanmış üç örnek üründür. Buna karşılık n8n Cloud orkestrasyonu, LangChain/OpenAI çağrısı, Supabase audit kaydı, risk routing'i ve Shopify `DRAFT` senkronizasyonu canlı entegrasyonlar üzerinden çalışır.

## Kaynaklar

- Canlı demo: https://ai-commerce-ops-demo.vercel.app
- Cloud n8n workflow: `automation/n8n/ai-commerce-ops.cloud.workflow.json`
- FastAPI backend: `live-demo/api/index.py`
- Demo UI: `live-demo/index.html`

## Geliştirici

**Mustafa Gencer**  
GitHub: https://github.com/mstfgncr23-eng  
LinkedIn: https://www.linkedin.com/in/mustafa-gencer-dev/
