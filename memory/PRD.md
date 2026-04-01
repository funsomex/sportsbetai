# SportsBetAI - Product Requirements Document

## Descripción del Proyecto
Sistema predictivo de apuestas deportivas con Inteligencia Artificial que utiliza datos estadísticos reales, machine learning y análisis de cuotas para identificar apuestas con valor esperado positivo (value bets).

## URLs de Producción
- **Frontend**: https://mellifluous-sherbet-50a651.netlify.app
- **Backend**: https://sportsbetai.onrender.com

## Stack Tecnológico
- **Frontend**: React.js + Tailwind CSS + Shadcn/UI
- **Backend**: FastAPI (Python)
- **Base de Datos**: MongoDB Atlas
- **APIs Externas**: The Odds API (cuotas reales)
- **Hosting**: Netlify (Frontend) + Render (Backend)

## Funcionalidades Implementadas

### ✅ Autenticación
- [x] Registro de usuarios
- [x] Login con JWT
- [x] Recuperación de contraseña (con código por Telegram)

### ✅ Dashboard
- [x] Métricas: Predicciones, Win Rate, ROI, Profit
- [x] Gráfico de rendimiento semanal
- [x] Próximos partidos con cuotas reales
- [x] Top Value Bets

### ✅ Partidos (Datos Reales - The Odds API)
- [x] Lista de partidos por deporte
- [x] Cuotas de 27+ casas de apuestas
- [x] Deportes: Fútbol, Baloncesto, Béisbol, Hockey, MMA, Tenis

### ✅ Value Bets
- [x] Detección automática de value bets
- [x] Cálculo de probabilidad real vs implícita
- [x] Nivel de confianza
- [x] Mejor casa de apuestas para cada selección

### ✅ Generador Automático de Combinadas (IA)
- [x] Configuración de número de partidos (2-6)
- [x] Niveles de riesgo: Bajo, Medio, Alto
- [x] Filtro por deportes
- [x] **Filtro por fecha: Hoy, Mañana, Esta semana, Fecha específica**
- [x] **Análisis detallado de cada selección**:
  - Razones de la selección
  - Métricas (probabilidad, valor, confianza)
  - Comparación de cuotas entre casas
  - Recomendación de dónde apostar
- [x] Cálculo de ganancia potencial
- [x] Probabilidad de ganar estimada

### ✅ Comparador de Cuotas
- [x] Comparación entre múltiples bookmakers
- [x] Identificación de mejor cuota por mercado

### ✅ Historial
- [x] Registro de predicciones
- [x] Filtros por fecha y resultado

### ✅ Configuración
- [x] Integración con Telegram para alertas
- [x] Configuración de notificaciones

### ✅ Integración con Telegram
- [x] Alertas de value bets
- [x] Códigos de recuperación de contraseña

## APIs Integradas
- **The Odds API**: Cuotas reales de 27+ casas de apuestas (500 req/mes gratis)

## Limitaciones Conocidas
- The Odds API no proporciona partidos EN VIVO (solo pre-partido)
- Límite de 500 requests/mes en tier gratuito
- Para partidos en vivo se necesitaría API-Football (adicional)

## Próximas Mejoras Potenciales (Backlog)
- [ ] Integrar API-Football para partidos en vivo y estadísticas
- [ ] Notificaciones push en navegador
- [ ] Historial de resultados de combinadas
- [ ] Exportar predicciones a Excel/PDF
- [ ] Sistema de rachas y estadísticas avanzadas

## Fecha de Última Actualización
2026-04-01
