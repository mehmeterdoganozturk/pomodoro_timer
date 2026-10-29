# Pomodoro Focus Pro 🍅
**Ubuntu 26.04 (Wayland + GNOME 50) için Modern Pomodoro ve Ders Çalışma Sayacı**

Gelişmiş görsel halka (circular progress), karanlık mod, zarif kristal çan sesli uyarıları, Ubuntu masaüstü bildirimleri ve günlük istatistik takibi ile ders çalışırken ve çalışırken odağınızı en üst seviyeye çıkarmak için tasarlandı.

---

## ✨ Özellikler

1. **Görsel Dairesel Sayaç (Cairo Vector Graphics)**:
   - 60 FPS pürüzsüz animasyonlu halka ilerleme çubuğu.
   - Büyük ve net dijital zaman göstergesi (`25:00`).
   - Döngü göstergesi (4 seanslık döngü takibi).
2. **Modlar ve Renk Temaları**:
   - 🍅 **Pomodoro (Odaklanma)**: Canlı Mercan/Kırmızı (`#FF5252`). Varsayılan 25 dk.
   - ☕ **Kısa Mola**: Zümrüt Yeşili (`#10B981`). Varsayılan 5 dk.
   - 🌴 **Uzun Mola**: Kraliyet İndigo / Moru (`#6366F1`). Varsayılan 15 dk.
3. **Akıllı Bildirim ve Ses Sistemi**:
   - Seans ve mola bittiğinde kristal çan melodisi çalar (`pw-play` / `paplay` / `canberra`).
   - Ubuntu GNOME masaüstü afiş bildirimi gönderir (`notify-send`).
4. **Çalışma Konusu Takibi (Ders / Görev Etiketi)**:
   - "🎯 Ders Çalışma", "Matematik Sınavı", "Kodlama" gibi konunuzu tek tıkla girip değiştirebilirsiniz.
5. **Kompakt / Mini Mod (PiP)**:
   - Başlık çubuğundaki küçültme butonuna (veya `M` tuşuna) basarak pencereyi küçük bir mini-sayaca dönüştürebilir, ders çalışırken veya video izlerken ekranın köşesinde tutabilirsiniz.
6. **Günlük İstatistikler (Referans Görseldeki Gibi)**:
   - 🍅 **Seanslar**: Bugün tamamlanan pomodoro sayısı ve hedef (Örn: 4 / 8).
   - ⏱️ **Odaklanma**: Bugün geçirilen toplam net odaklanma süresi (Örn: 1s 40dk).
   - ☕ **Molalar**: Bugün verilen mola sayısı.
7. **Özelleştirilebilir Ayarlar**:
   - Odak, kısa mola ve uzun mola süreleri (dakika bazında ayarlanabilir).
   - Uzun mola aralığı (kaç pomodoroda bir).
   - Otomatik mola / otomatik seans başlatma seçenekleri.
   - Ses ve bildirim açma/kapatma.
8. **Klavye Kısayolları**:
   - `Boşluk (Space)`: Başlat / Duraklat
   - `R`: Sayacı Başa Al (Sıfırla)
   - `N` veya `S`: Sonraki Aşamaya Geç (Atla)
   - `M`: Mini Mod / Tam Ekran Değiştir

---

## 🚀 Kurulum Seçenekleri

### Seçenek 1: Hızlı Kullanıcı Kurulumu (Önerilen - sudo gerektirmez)
```bash
cd /home/erdogan/Projects/pomodoro_timer
./install.sh
```
Kurulum anında tamamlanır; uygulama menüsünden **"Pomodoro Focus Pro"** adıyla aratarak veya terminalden `pomodoro-focus-pro` yazarak açabilirsiniz.

### Seçenek 2: Debian (.deb) Paketi ile Sistem Geneline Kurulum
Paket oluşturulmuştur:
```bash
cd /home/erdogan/Projects/pomodoro_timer
sudo apt install ./pomodoro-focus-pro_1.0.0_all.deb
```

---

## 🗑️ Kaldırma
```bash
cd /home/erdogan/Projects/pomodoro_timer
./uninstall.sh
```
Veya deb ile kurulduysa:
```bash
sudo apt remove pomodoro-focus-pro
```
