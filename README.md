# Lexavia 

**Yapay Zeka Destekli Dil Öğrenme Platformu**

Lexavia, kişiselleştirilmiş dil öğrenimi deneyimi sunan modern bir web uygulamasıdır. Backend tarafında **FastAPI** ve AI özellikleri, Frontend tarafında ise **Next.js** kullanılarak geliştirilmiştir.

## 🚀 Özellikler

- **🤖 AI Tabanlı İçerik**: Seviyenize uygun kelime ve quizleri yapay zeka oluşturur.
- **🧠 Aralıklı Tekrar (SRS)**: Öğrendiğiniz kelimeleri unutmadan hemen önce size hatırlatır.
- **📊 Gelişmiş İstatistikler**: Detaylı grafiklerle ilerlemenizi günlük olarak takip edin.
- **🔐 Güvenli Altyapı**: Supabase Auth ile güvenli kullanıcı yönetimi.

## 🛠️ Teknolojiler

### Backend
- **Framework**: FastAPI (Python)
- **Veritabanı**: PostgreSQL + SQLAlchemy (Async)
- **AI/ML**: Google Gemini API entegrasyonu (Veya yerel modeller)

### Frontend
- **Framework**: Next.js 14 (React)
- **Styling**: Tailwind CSS
- **State**: React Hooks

---

## 🏁 Kurulum ve Başlatma

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyin.

### Ön Gereksinimler
- Python 3.10+
- Node.js 18+

### 1. Backend'i Ayağa Kaldırın

Veritabanı işlemleri ve API sunucusu için:

```bash
cd apps/backend
# Sanal ortamı aktifleştirin (Windows)
venv\Scripts\activate
# Bağımlılıkları yükleyin (İlk kurulumda)
pip install -r requirements.txt
# Sunucuyu başlatın
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
API şu adreste çalışacak: `http://localhost:8000`

### 2. Frontend'i Çalıştırın

Kullanıcı arayüzü için yeni bir terminalde:

```bash
cd apps/frontend
# Bağımlılıkları yükleyin (İlk kurulumda)
npm install
# Uygulamayı başlatın
npm run dev
```
Uygulama şu adreste çalışacak: `http://localhost:3000`

---

## 📂 Proje Yapısı

```
lexavia/
├── apps/
│   ├── backend/   # FastAPI uygulaması, veritabanı modelleri, API rotaları
│   └── frontend/  # Next.js arayüzü, sayfalar, bileşenler
├── scripts/       # Veritabanı kurulum ve başlangıç araçları
└── README.md      # Proje dokümantasyonu
```


