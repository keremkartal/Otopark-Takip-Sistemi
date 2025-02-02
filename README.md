# Otopark Yönetim Sistemi

Bu proje, **araç giriş-çıkışlarını otomatik algılama** ve **otopark yönetimini** tamamen dijitalleştirme amacını taşır. Kamera görüntüsü üzerinden araç ve plaka tanıma (YOLO + EasyOCR) yapılır; kullanıcılar ise Django tabanlı web arayüzü üzerinden rezervasyon, ödeme ve bakiye işlemlerini yönetebilir.

## Özellikler

- **Araç Algılama ve Plaka Tanıma**  
  - YOLO ile araç tespiti  
  - EasyOCR ile plaka okuma  
  - Geçerli plakaların SQLite veritabanında kaydı

- **Rezervasyon ve Ödeme Yönetimi**  
  - Web arayüzü üzerinden rezervasyon oluşturma, düzenleme ve silme  
  - Otopark ücret hesaplama (süre bazlı)  
  - Kullanıcı bakiyesi ve ödeme işlemleri

- **Veritabanı Entegrasyonu (SQLite)**  
  - Giriş/çıkış bilgileri ve ücretlendirme kayıt altına alınır  
  - Kullanıcı, rezervasyon ve ödeme bilgileri tek noktada toplanır

## Kurulum ve Kullanım

1. Proje dosyalarını indirin ve gereksinimleri yükleyin.  
2. Django migrate işlemlerini tamamlayın ve sunucuyu başlatın.  
3. Tarayıcıda yerel sunucu adresine (ör. `http://127.0.0.1:8000/`) giderek kayıt veya giriş yapın.  
4. Otopark rezervasyonlarınızı yönetin, plaka bilgilerinizle ödeme durumunuzu takip edin.

## Test ve Doğrulama

- **Pytest** veya Django test komutları ile projeyi test edebilirsiniz.  
- Araç ve plaka tanıma ile rezervasyon, ödeme gibi kritik fonksiyonların işlevselliği kontrol edilir.

