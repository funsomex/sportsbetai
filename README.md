# SportsBetAI 🎯

Sistema Predictivo de Apuestas Deportivas con Inteligencia Artificial

![SportsBetAI Dashboard](https://images.unsplash.com/photo-1709078477781-3f885189ecbf?w=800)

## ✨ Características

- 🏆 **7 Deportes**: Fútbol, Baloncesto, Tenis, Béisbol, Hockey, MMA/UFC, Esports
- 📊 **Value Bets**: Detección automática de apuestas con valor positivo
- 🏠 **5 Casas de Apuestas**: BetPlay, Bet365, 1xBet, Pinnacle, Betfair
- 🤖 **Análisis IA**: Predicciones con GPT-5.2
- 📱 **Alertas Telegram**: Notificaciones en tiempo real
- 📈 **Combinadas**: Generador de parlays (1-6 selecciones)
- 📉 **Estadísticas**: ROI, Win Rate, Historial completo

## 🛠️ Stack Tecnológico

- **Frontend**: React, Tailwind CSS, Recharts
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **IA**: Emergent LLM (GPT-5.2)
- **Notificaciones**: Telegram Bot API

## 🚀 Deployment Gratuito

Ver **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** para instrucciones completas.

### Opción Rápida:
| Servicio | Plataforma | Costo |
|----------|------------|-------|
| Frontend | Vercel | GRATIS |
| Backend | Railway | GRATIS |
| Database | MongoDB Atlas | GRATIS |

## 💻 Desarrollo Local

### Requisitos
- Node.js 18+
- Python 3.11+
- MongoDB

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8001
```

### Frontend
```bash
cd frontend
yarn install
yarn start
```

## 📁 Estructura del Proyecto

```
sportsbetai/
├── backend/
│   ├── server.py          # API FastAPI
│   ├── requirements.txt   # Dependencias Python
│   ├── Procfile          # Para Railway/Heroku
│   └── .env              # Variables de entorno
├── frontend/
│   ├── src/
│   │   ├── pages/        # Páginas React
│   │   ├── components/   # Componentes UI
│   │   └── App.js        # App principal
│   ├── package.json
│   ├── vercel.json       # Config Vercel
│   └── .env              # Variables de entorno
└── DEPLOYMENT_GUIDE.md   # Guía de deployment
```

## 🔑 Variables de Entorno

### Backend
```env
MONGO_URL=mongodb+srv://...
DB_NAME=sportsbetai
CORS_ORIGINS=*
JWT_SECRET=your_secret
TELEGRAM_BOT_TOKEN=your_bot_token
EMERGENT_LLM_KEY=your_llm_key
```

### Frontend
```env
REACT_APP_BACKEND_URL=https://your-backend-url
```

## 📱 Páginas

| Ruta | Descripción |
|------|-------------|
| `/` | Dashboard principal |
| `/matches` | Lista de partidos |
| `/value-bets` | Detector de value bets |
| `/parlays` | Generador de combinadas |
| `/odds` | Comparador de cuotas |
| `/history` | Historial de predicciones |
| `/settings` | Configuración y Telegram |

## 📄 Licencia

MIT License - Uso libre para proyectos personales y comerciales.

---

Desarrollado con ❤️ usando [Emergent](https://emergent.sh)
