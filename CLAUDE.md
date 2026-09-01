# Online CV SaaS - proje notları

## Amaç
Kullanıcıların aylık abonelikle profesyonel online CV hazırlamasını ve özel public CV linki paylaşmasını sağlamak.

## Kararlar
- Ücretsiz demo yok.
- Kullanıcılar aylık abonelik ödesin.
- Abonelik aktifken CV düzenlenebilir.
- AI destekli yazı iyileştirme özelliği kullanılabilsin.
- Abonelik süresi dolduğunda düzenleme kapansın.
- Public CV linki çalışmaya devam etsin; read-only modda kalsın.
- Abonelik yenilenince düzenleme ve AI tekrar açılsın.

## Ürün mantığı
- Her kullanıcı için ayrı profil ve ayrı CV kaydı olacak.
- Her kullanıcının public URL'si olacak.
- Dashboard üzerinden kullanıcı CV'ini güncelleyebilecek.
- AI, kullanıcının kendini tanıtan paragrafını daha profesyonel hale getirecek.
- Kullanıcı AI seçeneklerinden birini seçebilecek.

## AI önerisi
- Profesyonel ton
- Kısa ve etkili ton
- Teknik / uzman ton
- Modern / girişimci ton

## Abonelik mantığı
- `has_active_subscription` alanı olacak.
- `subscription_expires_at` alanı olacak.
- aktif ise edit + AI + template customization açık.
- expired ise public link canlı ama edit kapalı.
- yeniden ödeme sonrası süre uzatılır.

## Fiyatlandırma fikri
- Aylık abonelik
- Premium plan dahilinde AI ve düzenleme açık.
- Public link canlı kalır, düzenleme read-only olur.

## Öncelikli geliştirme sırası
1. Kullanıcı kaydı / login
2. CV dashboard
3. Public CV link
4. Aylık abonelik sistemi
5. AI optimize etme modülü
6. Expired read-only kontrolü
7. Premium template ve PDF export

## Notlar
- Bu proje bir portfolio sitesi değil, bir SaaS ürünüdür.
- Fark yaratacak unsur: AI destekli CV optimize etme ve özel link üretimi.
- Ücretsiz demo yerine premium odaklı yapı daha güçlü olur.

## Konuşma özeti
Kullanıcılar CV oluşturup özel link alacak; aylık ödeyecek; aktifken CV'lerini güncelleyebilecek; süre dolunca düzenleme kapanacak ama public link açık kalacak; AI ile başlık ve özeti profesyonelleştirebilecek; kullanıcı istediği AI versiyonunu seçecek.
