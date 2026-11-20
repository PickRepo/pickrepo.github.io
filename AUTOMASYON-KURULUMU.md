# PickRepo otomatik yayın — tek seferlik kurulum

Bu paket yüklendikten sonra GitHub Actions, her gün yaklaşık 10:15 (Türkiye saati) civarında:

1. GitHub’daki proje listelerini yeniler.
2. Her repoda önce README’de uygun görsel arar; bulamazsa GitHub’daki repo dosyalarını da tarar.
3. Uygun görsel bulamazsa sitede temsili illüstrasyon gösterir.
4. Statik siteyi yeniden oluşturur ve GitHub Pages’e yayımlar.

Bundan sonra günlük liste ve görsel yenilemesi için sizin komut çalıştırmanız gerekmez. Yayımlama statik dosyalardır; web sunucusu, hesap, AI, veritabanı veya ücretli hizmet eklenmez.

## İlk kurulum

1. ZIP dosyasını bilgisayarınıza indirin ve içeriğini bir klasöre çıkarın.
2. GitHub’da `PickRepo/pickrepo.github.io` deposunu açın. `main` dalında **Add file → Upload files** seçin; çıkardığınız klasörlerdeki dosya ve klasörleri depo köküne sürükleyin. `.github/workflows/pages.yml` dosyasının da yüklendiğini kontrol edin. Ardından değişiklikleri **Commit changes** ile kaydedin.
3. Depoda **Settings → Pages → Build and deployment → Source** bölümünde **GitHub Actions** seçin.
4. **Actions** sekmesini açın. **Refresh and publish PickRepo** iş akışını seçin. İlk yüklemeden önce çalıştırılmışsa ve hata verdiyse, Pages kaynağını değiştirdikten sonra **Run workflow** ile bir kez daha başlatın.

İş akışının ilk tamamlanması birkaç dakika sürebilir. Sonraki çalıştırmalar zamanlanmış şekilde otomatik yapılır. İsterseniz bir listeyi beklemeden yenilemek için Actions sekmesinden aynı iş akışını elle de çalıştırabilirsiniz.

## Görseller hakkında

Uygun görsel önce repo sahibinin README’sinden, orada bulunamazsa GitHub’daki dosyalarından seçilir ve siteye yerel dosya olarak eklenir. Karttaki kaynak bağlantısı README’ye veya görselin bulunduğu GitHub dosyasına gider. Görsel bulunamaz ya da indirilemezse otomatik illüstrasyon kullanılır. Ziyaretçinin tarayıcısı görsel almak için üçüncü taraf sunucuya bağlanmaz.
