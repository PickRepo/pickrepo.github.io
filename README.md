# PickRepo

Bağımsız, ücretsiz GitHub projesi keşif sitesi. [GitHub Pages](https://pages.github.com/) üzerinden statik olarak yayımlanır.

## Neler içerir

- **Keşfet** — Yükselenler, Popüler, Erken keşif ve kaynaklı rehber listeleri; ad/açıklama/konu arama, dil ve konu filtreleri, farklı sıralamalar.
- **Kişiselleştirilebilir keşif puanı** — Arama uyumu, son güncelleme, yıldız/fork topluluğu, proje yaşı ve GitHub bilgilerinin doluluğu ağırlıklandırılır. Puan tarayıcıda hesaplanır; kalite veya güvenlik garantisi değildir.
- **Görseller** — Önce resmî README’de, sonra GitHub’daki repo dosyalarında uygun görsel aranır; bulunanlar siteye yerel dosya olarak eklenir. Görsel bulunamazsa temsilî illüstrasyon gösterilir.
- **Türkçe/İngilizce arayüz** — Tarayıcı diline göre açılır ve kullanıcı elle değiştirebilir. Repo açıklaması kaynağın özgün dilinde etiketlenir; doğrulanmış iki dilli özet yalnızca rehber içeriği bulunan projelerde gösterilir.
- **Rehberler** — Seçilmiş projeler için "Nedir? · Ne işe yarar? · Nasıl kullanılır?" rehberleri. Her rehberin altına resmî kaynak bağlantılarının eklenmesi yapılmıştır.
- **Sponsor** — Bağlantı alanı (henüz aktif sponsor yok).

## Siteyi yenileme

`site/data/catalog.json` ve `site/data/guides.json` dosyaları site içeriğidir.

Catalog'u GitHub API üzerinden yeniden oluşturmak için:

```bash
python scripts/update-catalog.py
```

Gerektirenler: Python 3 (standart kitaplık); isteğe bağlı `GITHUB_TOKEN` katalog ve repo dosya ağacı isteklerinde oran sınırını artırır. GitHub Actions iş akışı bu belirteci otomatik sağlar.

Görsel eşlemesini yenileyip siteyi üretmek için:

```bash
python scripts/prepare-repo-media.py
python scripts/build-site.py
```

Görsel hazırlama önce README’deki uygun görselleri, sonra GitHub’daki resmî repo dosyalarını tarar. GIF dâhil yaygın görsel türleri yerel olarak saklanır; ziyaretçilerin tarayıcısı dış görsel sunucularına istek göndermez.

Site klasörü `site/` içindir. `.github/workflows/pages.yml` dosyası GitHub Actions üzerinden yayımlar; listeleri, repo görsellerini ve siteyi her gün otomatik yeniler. İlk kurulumda depo ayarlarında **Settings → Pages → Source → GitHub Actions** seçilmelidir. Kullanıcı adımları `AUTOMASYON-KURULUMU.md` içindedir.

## Notlar

- Bu site sunucu tarafı veritabanı, hesap sistemi, kaydetme veya e-posta işlemi içermiyor. Arama ve puan tercihleri yalnızca açık sekmede çalışır; sunucuya gönderilmez ve saklanmaz.
- Keşif puanı herkese açık repo metaverilerinin ağırlıklı sıralamasıdır; kod, güvenlik veya kalite değerlendirmesi değildir. Geçmiş yıldız sayıları saklanmadığı için haftalık yıldız artışı ölçülmez.
- Rehberler editörel seçimleridir; kurulumlar bu sitede denenmemiştir. Resmî belgeler kaynak bağlantılarında verilmiştir.
- Marka/logolar, yazılar ve estil bu projeye aittir; GitHub ile bağlantılı değildir.
