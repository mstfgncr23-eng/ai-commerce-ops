# AI Commerce Ops — başvuru vaka özeti

**Aday:** Mustafa Gencer  
**GitHub:** [github.com/mstfgncr23-eng](https://github.com/mstfgncr23-eng)  
**LinkedIn:** [linkedin.com/in/mustafa-gencer-dev](https://www.linkedin.com/in/mustafa-gencer-dev/)

## Problem

Yeni medikal ürünlerin e-ticaret kataloğuna alınması; tedarikçi formu, Excel kontrolü, içerik üretimi, panel kaydı ve ekip onayı arasında çok sayıda manuel devir içeriyor. Bu yapı bekleme, tutarsız veri ve görünmeyen hata riski yaratıyor.

## Çözüm

Ürün formu n8n webhook'u ile alınır. n8n girdiyi LangChain/FastAPI servisine yönlendirir. Servis Pydantic şemasıyla structured output üretir; kategori, SEO içeriği, güven puanı ve risk işaretlerini döndürür. Güven puanı düşükse veya risk varsa kayıt insan incelemesine, aksi durumda Shopify Dev Dashboard uygulamasından access token alınır ve GraphQL Admin API üzerinden gerçek bir `DRAFT` ürün oluşturulur. Her karar aynı idempotent `request_id` ile PostgreSQL audit tablosuna yazılır.

## Neden bu mimari?

- **n8n:** tetikleyici, retry ve iş akışı görünürlüğü
- **LangChain:** model sağlayıcısından bağımsız structured output katmanı
- **FastAPI:** doğrulanabilir sözleşme, test edilebilir iş mantığı ve API ayrımı
- **PostgreSQL:** tekrar çalıştırma, karar geçmişi ve denetlenebilirlik
- **Human-in-the-loop:** düşük güvenli veya riskli ürünlerin otomatik yayınlanmasını engelleme

## Tamamlanmışlık kriteri

- İçe aktarılabilir n8n workflow JSON
- Docker Compose ile n8n, API ve PostgreSQL
- Deterministik demo ve iki karar dalı
- Opsiyonel gerçek LangChain çağrısı
- Hata tekrar denemesi, idempotency ve audit log
- Gerçek Shopify GraphQL Admin API ile DRAFT ürün kaydı
- Remotion ile yaklaşık 50 saniyelik proje anlatımı

## Görüşme demosu

Önce eksiksiz örnek ürün gönderilir ve Shopify üzerinde gerçek `DRAFT` ürün oluşturulduğu, dönen product GID ile birlikte gösterilir. Ardından stok sıfır ve görsel eksik olan örnek gönderilerek insan onayı dalı çalıştırılır. Son olarak aynı SKU tekrar gönderilir; audit kaydının çoğalmadığı, mevcut `request_id` üzerinden güncellendiği açıklanır.

## Dürüst sunum notu

Shopify entegrasyonu Dev Dashboard + client credentials + GraphQL `productCreate` ile gerçek mağazaya `DRAFT` ürün yazar. Slack/e-posta inceleme kanalı ise halen adaptör noktasıdır; onu canlı entegrasyon gibi sunma. Ürünlerin DRAFT kalması güvenli demo sınırıdır.
