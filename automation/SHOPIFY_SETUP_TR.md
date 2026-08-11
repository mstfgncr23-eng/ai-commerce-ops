# Shopify API Kurulum Kontrol Listesi

## Dev Dashboard / Sürüm

- **Uygulama URL'si:** `https://shopify.dev/apps/default-app-home`
- **Uygulamayı Shopify yöneticisine ekle:** Kapalı
- **Web kancası API sürümü:** `2026-07`
- **Gerekli kapsam:** `write_products`
- **İsteğe bağlı kapsamlar:** Boş
- **Yönlendirme URL'leri:** Boş
- **POS / Uygulama ara sunucusu:** Gerekmez
- **Yayınla / Release**

## Kurulum

1. App Home → **Install app**
2. Kendi mağazanı seç
3. `write_products` iznini onayla
4. App Settings → **Client ID** ve **Client Secret** değerlerini al

## Yerel `.env`

```dotenv
SHOPIFY_SHOP=your-store.myshopify.com
SHOPIFY_CLIENT_ID=...
SHOPIFY_CLIENT_SECRET=...
SHOPIFY_API_VERSION=2026-07
```

> Client Secret'ı GitHub'a, README'ye, ekran görüntüsüne veya n8n workflow JSON'una yapıştırma.
