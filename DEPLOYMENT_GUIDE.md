# SportsBetAI - Guía de Deployment Gratuito

## Arquitectura Recomendada (100% Gratis)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     VERCEL      │     │    RAILWAY      │     │  MONGODB ATLAS  │
│    (Frontend)   │────▶│    (Backend)    │────▶│   (Database)    │
│      FREE       │     │      FREE       │     │      FREE       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## PASO 1: Crear Base de Datos en MongoDB Atlas (Gratis)

1. Ve a https://www.mongodb.com/atlas
2. Crea una cuenta gratuita
3. Crea un cluster **FREE (M0 Sandbox)**
4. En "Database Access" → Crea un usuario con contraseña
5. En "Network Access" → Añade `0.0.0.0/0` (permitir todas las IPs)
6. En "Connect" → Obtén tu connection string:
   ```
   mongodb+srv://USUARIO:PASSWORD@cluster0.xxxxx.mongodb.net/sportsbetai?retryWrites=true&w=majority
   ```

---

## PASO 2: Desplegar Backend en Railway (Gratis)

1. Ve a https://railway.app
2. Crea cuenta con GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Selecciona tu repositorio → carpeta `backend`
5. Configura las variables de entorno:

   ```
   MONGO_URL=mongodb+srv://USUARIO:PASSWORD@cluster0.xxxxx.mongodb.net/sportsbetai?retryWrites=true&w=majority
   DB_NAME=sportsbetai
   CORS_ORIGINS=*
   JWT_SECRET=tu_jwt_secret_seguro_aqui
   TELEGRAM_BOT_TOKEN=8213075202:AAHrfhJ6ujpLSz8fdq2K0dRsTB0mkv0UJOQ
   EMERGENT_LLM_KEY=sk-emergent-9EfB68aB0D4AcCa9c6
   ```

6. Railway detectará automáticamente el Procfile y desplegará
7. Copia la URL del backend (ej: `https://sportsbetai-backend.up.railway.app`)

---

## PASO 3: Desplegar Frontend en Vercel (Gratis)

1. Ve a https://vercel.com
2. Crea cuenta con GitHub
3. Click "Add New" → "Project"
4. Importa tu repositorio → selecciona carpeta `frontend`
5. Configura:
   - **Framework Preset:** Create React App
   - **Root Directory:** `frontend`
   - **Build Command:** `yarn build`
   - **Output Directory:** `build`

6. Añade variable de entorno:
   ```
   REACT_APP_BACKEND_URL=https://tu-backend.up.railway.app
   ```

7. Click "Deploy"

---

## PASO 4: Configurar Dominio (Opcional)

- Vercel te da: `tu-app.vercel.app` (gratis)
- Railway te da: `tu-app.up.railway.app` (gratis)
- Puedes conectar tu propio dominio en ambas plataformas

---

## Variables de Entorno Requeridas

### Backend (Railway)
| Variable | Descripción |
|----------|-------------|
| `MONGO_URL` | Connection string de MongoDB Atlas |
| `DB_NAME` | `sportsbetai` |
| `CORS_ORIGINS` | `*` o URL de tu frontend |
| `JWT_SECRET` | Clave secreta para JWT |
| `TELEGRAM_BOT_TOKEN` | Token de tu bot de Telegram |
| `EMERGENT_LLM_KEY` | Key para análisis IA |

### Frontend (Vercel)
| Variable | Descripción |
|----------|-------------|
| `REACT_APP_BACKEND_URL` | URL de tu backend en Railway |

---

## Límites de los Planes Gratuitos

| Servicio | Límite Gratuito |
|----------|-----------------|
| MongoDB Atlas | 512 MB storage |
| Railway | 500 horas/mes, 512 MB RAM |
| Vercel | Ilimitado para proyectos personales |

---

## Comandos Útiles

### Desarrollo Local
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --port 8001

# Frontend
cd frontend
yarn install
yarn start
```

### Build para Producción
```bash
# Frontend
cd frontend
yarn build
```

---

## Soporte

- MongoDB Atlas Docs: https://docs.atlas.mongodb.com
- Railway Docs: https://docs.railway.app
- Vercel Docs: https://vercel.com/docs

---

**¡Tu app SportsBetAI estará corriendo 100% gratis!** 🚀
