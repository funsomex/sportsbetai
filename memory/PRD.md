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
- [x] Filtro por fecha: Hoy, Mañana, Esta semana, Fecha específica
- [x] Análisis detallado de cada selección
- [x] Cálculo de ganancia potencial
- [x] Probabilidad de ganar estimada

### ✅ Sistema de Seguimiento de Combinadas y ROI
- [x] Estado de combinadas: Pendiente, Ganada, Perdida
- [x] Botones para marcar resultado (Ganó/Perdió)
- [x] Panel de estadísticas ROI:
  - Win Rate %
  - ROI %
  - Beneficio total
  - Total apostado
  - Ganadas/Perdidas/Pendientes
  - Racha actual
  - Mejor ganancia / Peor pérdida
- [x] Filtros: Todas, Pendientes, Ganadas, Perdidas
- [x] Historial de resultados

### ✅ Comparador de Cuotas
- [x] Comparación entre múltiples bookmakers
- [x] Identificación de mejor cuota por mercado

### ✅ Integración con Telegram
- [x] Alertas de value bets
- [x] Códigos de recuperación de contraseña

## APIs Integradas
- **The Odds API**: Cuotas reales de 27+ casas de apuestas (500 req/mes gratis)

## Limitaciones Conocidas
- The Odds API no proporciona partidos EN VIVO (solo pre-partido)
- Límite de 500 requests/mes en tier gratuito

## Próximas Mejoras Potenciales (Backlog)
- [ ] Integrar API-Football para partidos en vivo
- [ ] Notificaciones push en navegador
- [ ] Exportar estadísticas a Excel/PDF
- [ ] Gráficos de evolución del ROI mensual
- [ ] Comparador de rendimiento por deporte

## Fecha de Última Actualización
2026-04-02

## Estado Final
✅ Sistema 100% funcional en producción con datos reales
✅ Caché de 60 minutos implementado para proteger cuota de API
✅ Documentación completa generada: /app/SPORTSBETAI_INFO_COMPLETA.txt

## Versión 2.0.0 - Arquitectura Modular (2026-04-02)

### Nuevas Funcionalidades
- [x] Widget "Apuesta del Día" en Dashboard con opción de compartir
- [x] Exportación a Excel (.xlsx) con historial completo y estadísticas
- [x] Exportación a PDF con reporte de rendimiento

### Refactorización del Backend
- [x] Migración de server.py monolítico (1860 líneas) a arquitectura modular (78 líneas)
- [x] Estructura de carpetas: config/, models/, routes/, services/
- [x] Separación de responsabilidades por dominio
- [x] Mejor mantenibilidad y escalabilidad del código

### Fixes aplicados durante testing
- [x] Login bug: Frontend esperaba 'access_token', backend retornaba 'token' - corregido
- [x] Endpoint faltante: /api/parlays/stats añadido
- [x] Compatibilidad: PUT /api/parlays/{id}/result añadido para frontend
