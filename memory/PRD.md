# SportsBetAI - Sistema Predictivo de Apuestas Deportivas con IA

## Problema Original
Crear un sistema automatizado de análisis predictivo para apuestas deportivas que utilice datos estadísticos, machine learning y análisis de cuotas para identificar apuestas con valor esperado positivo (value bets). El sistema debe analizar múltiples deportes y generar alertas automáticas en Telegram.

## Arquitectura
- **Backend**: FastAPI con Python
- **Frontend**: React con Tailwind CSS
- **Base de datos**: MongoDB
- **IA**: Emergent LLM Key (GPT-5.2)
- **Notificaciones**: Telegram Bot API

## User Personas
1. **Apostador Analítico**: Usuario que busca ventaja matemática mediante análisis de value bets
2. **Apostador Casual**: Usuario que quiere combinar selecciones de forma fácil
3. **Seguidor de Alertas**: Usuario que recibe notificaciones de oportunidades vía Telegram

## Core Requirements (Estático)
- [x] Sistema de autenticación JWT
- [x] Dashboard con estadísticas de rendimiento
- [x] Listado de partidos por deporte (7 deportes)
- [x] Detector de Value Bets con cálculo de probabilidades
- [x] Comparador de cuotas entre 5 casas de apuestas
- [x] Generador de combinadas (1-6 selecciones)
- [x] Historial de predicciones con ROI
- [x] Integración Telegram para alertas

## What's Been Implemented (14 Mar 2026)
### Backend
- Auth: Register, Login, JWT tokens
- Matches: Listado con filtros por deporte/estado
- Value Bets: Detector con cálculo de valor y confianza
- Parlays: CRUD de combinadas
- Predictions: Guardado de predicciones
- Stats: Estadísticas de usuario (win rate, ROI)
- Telegram: Configuración y envío de alertas
- AI Analysis: Análisis de partidos con GPT-5.2

### Frontend
- Login/Register con diseño oscuro
- Dashboard con gráficos de rendimiento
- Partidos con filtros y cuotas 1X2
- Value Bets con tarjetas detalladas
- Combinadas con carrito estilo shopping
- Comparador de cuotas por partido
- Historial con estadísticas
- Configuración de Telegram

### Design System
- Tema: "The Performance Pro" (estilo Bloomberg Terminal)
- Paleta: Deep Obsidian (#050505) + Electric Lime (#CCFF00)
- Tipografías: Barlow Condensed, JetBrains Mono, Manrope

## Datos MOCK (pendiente APIs reales)
- Estadísticas deportivas simuladas
- Cuotas generadas aleatoriamente
- Probabilidades calculadas con variación

## Backlog Priorizado
### P0 (Crítico)
- [ ] Integrar API-Football para datos reales de fútbol
- [ ] Integrar The Odds API para cuotas reales

### P1 (Importante)
- [ ] Modelo ML para predicciones más precisas
- [ ] Notificaciones push automáticas de value bets
- [ ] Histórico de movimientos de cuotas

### P2 (Mejoras)
- [ ] Dashboard móvil optimizado
- [ ] Exportar predicciones a CSV
- [ ] Gráficos de tendencias por deporte

## Próximos Pasos
1. Obtener API keys reales (API-Football, The Odds API)
2. Implementar scraping/API de cuotas en tiempo real
3. Entrenar modelo ML con datos históricos
4. Automatizar alertas de Telegram para value bets detectados
