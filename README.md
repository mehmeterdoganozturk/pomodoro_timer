# Pomodoro Focus Pro 🍅
**Masaüstü (Linux / GNOME) & Mobil (Android) Odaklanma, Ders Çalışma ve Zinciri Kırma Sistemi**

Pomodoro Focus Pro; ders çalışırken, kod yazarken veya proje yönetirken odaklanmanızı en üst seviyeye taşımak için geliştirilmiş çift platformlu (Ubuntu/Linux masaüstü + Yerel Android mobil uygulaması) profesyonel bir ekosistemdir.

---

## 📑 İçindekiler
- [✨ Genel Özellikler](#-genel-özellikler)
- [🖥️ Masaüstü Uygulaması (Linux / GNOME)](#️-masaüstü-uygulaması-linux--gnome)
  - [Masaüstü Özellikleri](#masaüstü-özellikleri)
  - [Masaüstü Kurulum & Çalıştırma](#masaüstü-kurulum--çalıştırma)
  - [Debian (.deb) Paketi Derleme](#debian-deb-paketi-derleme)
  - [GNOME Shell Üst Bar Uzantısı](#gnome-shell-üst-bar-uzantısı)
- [📱 Android Uygulaması (Jetpack Compose)](#-android-uygulaması-jetpack-compose)
  - [Android Mimarisi & Özellikler](#android-mimarisi--özellikler)
  - [Android Ana Ekran Widget'ı (AppWidget)](#android-ana-ekran-widgetı-appwidget)
  - [Android Projesi Derleme & APK Üretme (Çok Detaylı)](#android-projesi-derleme--apk-üretme-çok-detaylı)
    - [1. Gereksinimler](#1-gereksinimler)
    - [2. Debug APK Derleme (Hızlı Test)](#2-debug-apk-derleme-hızlı-test)
    - [3. Cihaza Doğrudan Yükleme (ADB)](#3-cihaza-doğrudan-yükleme-adb)
    - [4. İmzalı Release APK / AAB Üretimi](#4-imzalı-release-apk--aab-üretimi)
    - [5. Birim Testlerini Çalıştırma](#5-birim-testlerini-çalıştırma)
- [📂 Proje Dizin Yapısı](#-proje-dizin-yapısı)
- [📜 Lisans](#-lisans)

---

## ✨ Genel Özellikler

* 🍅 **Çoklu Zamanlayıcı Modları**:
  * **Pomodoro**: 25 dk (ayarlanabilir) odaklanma seansı.
  * **Kısa Mola**: 5 dk zihni dinlendirme molası.
  * **Uzun Mola**: 15 dk derin dinlenme.
  * **Test / Sınav Sayacı**: 20, 30 ve 40 dakikalık hazır sınav / deneme süreleri.
  * **Kronometre**: Serbest çalışma ve zaman takibi.
* 🎓 **Çalışma Profilleri & Ders Takibi**:
  * **YKS / Sınav**: Matematik, Geometri, Fizik, Kimya, Biyoloji, Türkçe Paragraf, Deneme.
  * **Mühendislik & IT**: Kodlama, Algoritma, Sistem Mimarisi, Debugging, Dokümantasyon, DevOps.
  * **İş & Yönetim**: Strateji, Toplantı, Raporlama, Operasyon, E-Posta.
  * İsteğe özel sınırsız ders ekleme, etiket (badge) ve renk belirleme.
* 🔥 **Zinciri Kırma (Streak) & 28 Günlük Isı Haritası**:
  * Günlük seans hedefine göre zincir hesaplama ve rekor takibi.
  * 4 hafta × 7 gün (Pzt-Paz) yoğunluk haritası ve ders süre dağılım çubukları.
* 🔔 **Ses ve Titreşim Bildirimleri**: Orijinal çan ve tamamlama tonları (`focus_complete.wav`, `break_complete.wav`).

---

## 🖥️ Masaüstü Uygulaması (Linux / GNOME)

Ubuntu 26.04 (Wayland + GNOME Shell) için GTK4 / Libadwaita ve Cairo 2D vektör grafikleriyle geliştirilmiştir.

### Masaüstü Özellikleri
* **Cairo 60 FPS Dairesel Sayaç**: Yumuşak animasyonlu yay ilerleme halkası.
* **Mini Mod (PiP)**: Ekran köşesine sabitlenen kompakt mod (`M` tuşu ile).
* **D-Bus Entegrasyonu**: GNOME Shell üst bar uzantısı ile anlık çift yönlü haberleşme.
* **Klavye Kısayolları**:
  * `Boşluk (Space)`: Başlat / Duraklat
  * `R`: Sayacı Başa Al (Sıfırla)
  * `N` / `S`: Sonraki seansa / molaya geç
  * `M`: Mini Mod / Normal Mod geçişi

### Masaüstü Kurulum & Çalıştırma

#### Kaynak Koddan Doğrudan Çalıştırma:
```bash
cd /home/erdogan/Projects/pomodoro_timer
python3 main.py
```

#### Kullanıcı Dizinine Tek Tıkla Kurulum (Önerilen):
```bash
chmod +x install.sh
./install.sh
```
Bu işlem uygulamayı `~/.local/share/pomodoro-focus-pro` altına kurar, masaüstü ikonunu ve menü kısayolunu (`pomodoro-focus-pro.desktop`) otomatik ekler.

#### Masaüstü Uygulamasını Kaldırma:
```bash
./uninstall.sh
```

### Debian (.deb) Paketi Derleme

Sistem geneline (`/usr/bin`, `/usr/share`) kurulabilir `.deb` paketi oluşturmak için:

```bash
chmod +x build_deb.sh
./build_deb.sh
```
Betik çalıştığında `pomodoro-focus-pro_1.0.0_all.deb` paketi üretilir. Paketi kurmak için:
```bash
sudo apt install ./pomodoro-focus-pro_1.0.0_all.deb
```

Kaldırmak için:
```bash
sudo apt remove pomodoro-focus-pro
```

### GNOME Shell Üst Bar Uzantısı

GNOME Shell üst panelinde `🍅 24:35` şeklinde anlık süreyi gösterir.
* Uzantı dizini: `gnome_extension/pomodoro-focus-pro@erdogan.github.com`
* Kurulum ve etkinleştirme:
  ```bash
  mkdir -p ~/.local/share/gnome-shell/extensions/
  cp -r gnome_extension/pomodoro-focus-pro@erdogan.github.com ~/.local/share/gnome-shell/extensions/
  gnome-extensions enable pomodoro-focus-pro@erdogan.github.com
  ```

---

## 📱 Android Uygulaması (Jetpack Compose)

Android uygulaması, masaüstü sürümün tüm özelliklerini yerel Android deneyimine taşır. Tamamen modern **Jetpack Compose**, **Material 3** ve **Kotlin Coroutines / Flow** mimarisiyle sıfırdan geliştirilmiştir.

### Android Mimarisi & Özellikler
* **Yazılım Mimarisi**: MVVM + Repository Pattern + Clean Architecture.
* **Minimum / Hedef SDK**: `minSdk = 24` (Android 7.0+), `compileSdk = 36` / `targetSdk = 36` (Android 16 Uyumlu).
* **Ekranlar & Sekmeler**:
  1. `TimerTab`: Dairesel Canvas halkası, dijital sayaç, mod değiştirici, seçili ders chip'leri, başlat/durdur/sıfırla/atla kontrolleri ve istatistik kartları.
  2. `StreakTab`: Ateş banner'ı, 28 günlük (4×7) renk tonlu aktivite haritası (Heatmap), bugünkü ders dağılım barları.
  3. `WorkspacesTab`: YKS, Mühendislik ve İş profilleri, ders ekleme / silme / gizleme paneli.
* **Arka Plan Servisi (`TimerService`)**:
  * Telefon kilitlendiğinde veya başka uygulamaya geçildiğinde sayaç asla durmaz.
  * Bildirim çubuğunda anlık geri sayım ve hızlı duraklat/sıfırla butonları sunar.
* **Adaptive App Icon**: Her Android başlatıcısında (Pixel, Samsung One UI, Xiaomi vb.) uyumlu `#141722` koyu zemin üzerinde kırmızı Pomodoro halkası ve yaprağı.

### Android Ana Ekran Widget'ı (AppWidget)
* **Görünüm**: AMOLED koyu temalı, `4x2` veya `3x2` boyutlanabilir şık kart.
* **Bileşenler**:
  * 🍅 Uygulama logosu ve seçili ders rozeti (örn: `📐 Matematik`).
  * 🔥 Güncel zincir rekoru (örn: `🔥 5 Gün`).
  * Büyük dijital sayaç (`25:00`).
  * Aktif mod, döngü seansı ve günlük hedef bilgisi.
* **Doğrudan Kontrol**: Uygulamayı açmadan ana ekrandan **▶️ Başlat / ⏸️ Duraklat**, **🔄 Sıfırla** ve **🚀 Aç**.

---

### Android Projesi Derleme & APK Üretme (Çok Detaylı)

#### 1. Gereksinimler
* **Java Development Kit (JDK)**: JDK 17 veya üzeri (`openjdk-17-jdk` önerilir).
  ```bash
  sudo apt install openjdk-17-jdk
  java -version
  ```
* **Android SDK**: `cmdline-tools` ve `platforms;android-36`.
  * Ortam değişkenleri (`~/.bashrc`):
    ```bash
    export ANDROID_HOME=$HOME/Android/Sdk
    export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
    ```

#### 2. Debug APK Derleme (Hızlı Test)

1. Terminalde `android_app` klasörüne girin:
   ```bash
   cd /home/erdogan/Projects/pomodoro_timer/android_app
   ```
2. Gradle Wrapper'a çalıştırma yetkisi verin (gerekirse):
   ```bash
   chmod +x gradlew
   ```
3. Debug APK derlemesini başlatın:
   ```bash
   ./gradlew assembleDebug
   ```
4. **Oluşturulan APK Dosyası**:
   Derleme tamamlandığında APK dosyanız şu konumda hazır olur:
   ```bash
   app/build/outputs/apk/debug/app-debug.apk
   ```
   Bu dosyayı telefonunuza USB kablosu, Bluetooth veya WhatsApp/Telegram ile gönderip doğrudan kurabilirsiniz.

#### 3. Cihaza Doğrudan Yükleme (ADB)

Telefonunuzda **Geliştirici Seçenekleri** ve **USB Hata Ayıklama** açıksa:

1. Telefonu bilgisayara USB ile bağlayın ve tanındığını doğrulayın:
   ```bash
   adb devices
   ```
2. Tek komutla hem derleyin hem telefona yükleyin:
   ```bash
   cd /home/erdogan/Projects/pomodoro_timer/android_app
   ./gradlew installDebug
   ```
   *(Veya önceden derlenen APK'yı yüklemek için: `adb install -r app/build/outputs/apk/debug/app-debug.apk`)*

#### 4. İmzalı Release APK / AAB Üretimi

Google Play Store'a yüklemek veya imzalı release APK elde etmek için:

##### Adım A: İlerleme Anahtarı (Keystore) Oluşturma (İlk sefere mahsus):
```bash
keytool -genkey -v -keystore release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias pomodorokey
```

##### Adım B: `app/build.gradle.kts` İçinde Signing Config Tanımlama:
```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file("../release-key.jks")
            storePassword = "ŞİFRENİZ"
            keyAlias = "pomodorokey"
            keyPassword = "ŞİFRENİZ"
        }
    }
    buildTypes {
        release {
            isMinifyEnabled = true
            signingConfig = signingConfigs.getByName("release")
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

##### Adım C: Release Paketini Derleme:
* **Release APK için**:
  ```bash
  ./gradlew assembleRelease
  # Çıktı: app/build/outputs/apk/release/app-release.apk
  ```
* **Play Store için Android App Bundle (.aab)**:
  ```bash
  ./gradlew bundleRelease
  # Çıktı: app/build/outputs/bundle/release/app-release.aab
  ```

#### 5. Birim Testlerini Çalıştırma
Model, profil ve sayaç mantığı testlerini çalıştırmak için:
```bash
cd /home/erdogan/Projects/pomodoro_timer/android_app
./gradlew test
```

---

## 📂 Proje Dizin Yapısı

```
pomodoro_timer/
├── README.md                      # Proje ana dokümantasyonu
├── install.sh                     # Masaüstü hızlı kurulum betiği
├── uninstall.sh                   # Masaüstü kaldırma betiği
├── build_deb.sh                   # Debian (.deb) paketleme betiği
├── main.py                        # Masaüstü GTK4 başlatıcı
├── pomodoro-focus-pro.desktop     # Linux masaüstü kısayol dosyası
├── pomodoro_focus_pro/            # Masaüstü Python kaynak kodları
│   ├── app.py                     # Ana GTK4/Libadwaita penceresi
│   ├── timer.py                   # Zamanlayıcı çekirdek motoru
│   ├── dbus_service.py            # GNOME Shell IPC D-Bus servisi
│   └── assets/                    # İkon ve ses dosyaları
├── gnome_extension/               # GNOME Shell Üst Panel Uzantısı
│   └── pomodoro-focus-pro@...     # extension.js, metadata.json
└── android_app/                   # 📱 Native Android Projesi
    ├── build.gradle.kts           # Kök Gradle yapılandırması
    ├── gradlew                    # Gradle Linux wrapper betiği
    └── app/
        ├── build.gradle.kts       # Modül derleme yapılandırması
        └── src/
            ├── main/
            │   ├── AndroidManifest.xml   # İzinler, servis ve widget tanımları
            │   ├── kotlin/.../
            │   │   ├── MainActivity.kt   # Jetpack Compose ana aktivite
            │   │   ├── engine/           # TimerEngine singleton motoru
            │   │   ├── service/          # TimerService arka plan servisi
            │   │   ├── widget/           # PomodoroWidgetProvider
            │   │   ├── model/            # Models.kt ve DefaultData.kt
            │   │   ├── data/             # PomodoroRepository.kt
            │   │   └── ui/               # TimerTab, StreakTab, WorkspacesTab
            │   └── res/
            │       ├── drawable/         # Widget arka plan ve buton şekilleri
            │       ├── layout/           # widget_pomodoro.xml
            │       ├── mipmap-*/         # Adaptive & Legacy App Launcher İkonları
            │       ├── raw/              # focus_complete.wav, break_complete.wav
            │       └── xml/              # pomodoro_widget_info.xml
            └── test/                     # Birim testleri
```

---

## 📜 Lisans
Bu proje [MIT Lisansı](LICENSE) kapsamında açık kaynak olarak geliştirilmiştir.
İstediğiniz gibi özelleştirebilir, geliştirebilir ve paylaşabilirsiniz.
