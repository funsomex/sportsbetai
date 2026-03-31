# 📱 MANUAL COMPLETO - SportsBetAI

## 🌐 ACCESO A TU APP

**URL:** https://mellifluous-sherbet-50a651.netlify.app

---

## 📝 CÓMO CREAR UNA CUENTA

1. Abre la URL de tu app
2. Haz click en **"Regístrate"** (debajo del botón "ENTRAR")
3. Completa el formulario:
   - **Nombre:** Tu nombre
   - **Email:** Tu correo electrónico
   - **Contraseña:** Mínimo 6 caracteres
   - **Confirmar contraseña:** Repite la contraseña
4. Click en **"Crear Cuenta"**
5. ¡Listo! Serás redirigido al Dashboard

---

## 🔐 CÓMO INICIAR SESIÓN

1. Abre la URL de tu app
2. Ingresa tu **Email** y **Contraseña**
3. Click en **"ENTRAR"**

---

## 📊 FUNCIONALIDADES DE LA APP

### 1. DASHBOARD (Página Principal)
- Resumen de tus predicciones
- Estadísticas: Win Rate, ROI, Profit
- Top Value Bets del momento
- Partidos en vivo
- Gráfico de rendimiento semanal

### 2. PARTIDOS (/matches)
- Lista de todos los partidos disponibles
- Filtros por deporte: Fútbol, Baloncesto, Tenis, Béisbol, Hockey, MMA, Esports
- Filtros por estado: En vivo, Próximos, Finalizados
- Cuotas de las 5 casas de apuestas

### 3. VALUE BETS (/value-bets)
- Apuestas con valor positivo detectadas por IA
- Muestra:
  - Probabilidad real calculada
  - Probabilidad implícita de la casa
  - Porcentaje de valor (+%)
  - Nivel de confianza
- Filtrar por valor mínimo (+1%, +3%, +5%, +10%)
- Botón para enviar alertas a Telegram

### 4. COMBINADAS (/parlays)
- Crea combinadas de 1 a 6 selecciones
- Selecciona cuotas de diferentes partidos
- Calcula cuota total automáticamente
- Guarda tus combinadas favoritas

### 5. COMPARADOR DE CUOTAS (/odds)
- Compara cuotas entre las 5 casas:
  - BetPlay
  - Bet365
  - 1xBet
  - Pinnacle
  - Betfair
- Muestra la mejor cuota para cada mercado
- Estadísticas del partido (xG, posesión, forma)

### 6. HISTORIAL (/history)
- Todas tus predicciones pasadas
- Filtrar: Ganadas, Perdidas, Pendientes
- Gráfico de evolución del profit
- Estadísticas totales

### 7. CONFIGURACIÓN (/settings)
- Perfil de usuario
- **Configurar Telegram** para alertas
- Notificaciones
- Información del sistema

---

## 📱 CONFIGURAR ALERTAS DE TELEGRAM

### Paso 1: Crear/Obtener tu Chat ID
1. Abre Telegram
2. Busca el bot **@userinfobot**
3. Envía cualquier mensaje
4. El bot te responderá con tu **Chat ID** (es un número)

### Paso 2: Configurar en la App
1. Ve a **Configuración** (/settings)
2. En la sección "Telegram Alerts"
3. Ingresa tu **Chat ID**
4. Click en **"Guardar"**
5. Click en **"Probar"** para verificar

### Paso 3: Recibir Alertas
- Cuando detectes un Value Bet, haz click en "Enviar a Telegram"
- Recibirás la alerta en tu chat de Telegram

---

## 📲 INSTALAR COMO APP EN TU CELULAR

### Para iPhone (iOS):

1. Abre **Safari** (debe ser Safari, no Chrome)
2. Ve a: `https://mellifluous-sherbet-50a651.netlify.app`
3. Toca el botón **Compartir** (el cuadrado con flecha hacia arriba)
4. Desliza hacia abajo y toca **"Agregar a pantalla de inicio"**
5. Escribe el nombre: **SportsBetAI**
6. Toca **"Agregar"**
7. ¡Listo! Verás el ícono en tu pantalla de inicio

### Para Android:

1. Abre **Chrome**
2. Ve a: `https://mellifluous-sherbet-50a651.netlify.app`
3. Toca los **3 puntos** (menú) arriba a la derecha
4. Toca **"Añadir a pantalla de inicio"** o **"Instalar aplicación"**
5. Escribe el nombre: **SportsBetAI**
6. Toca **"Añadir"**
7. ¡Listo! Verás el ícono en tu pantalla de inicio

---

## 🎯 CÓMO USAR LOS VALUE BETS

### ¿Qué es un Value Bet?
Es una apuesta donde la probabilidad real (calculada por IA) es **mayor** que la probabilidad implícita en las cuotas. Esto significa una **ventaja matemática** a largo plazo.

### Ejemplo:
- **Cuota:** 2.50
- **Probabilidad implícita:** 40% (1/2.50)
- **Probabilidad real calculada:** 50%
- **Valor:** +10% ✅

### Cómo interpretarlos:
- **+3% a +5%:** Valor moderado
- **+5% a +10%:** Buen valor
- **+10% o más:** Excelente valor (glow verde)

### Confianza:
- **80%+:** Alta confianza (verde)
- **60-80%:** Confianza media (azul)
- **<60%:** Confianza baja (gris)

---

## 📈 DEPORTES DISPONIBLES

| Deporte | Ligas |
|---------|-------|
| ⚽ Fútbol | Premier League, La Liga, Serie A, Bundesliga, Champions League |
| 🏀 Baloncesto | NBA, EuroLeague, ACB |
| 🎾 Tenis | ATP Tour, WTA Tour, Grand Slam |
| ⚾ Béisbol | MLB, NPB, KBO |
| 🏒 Hockey | NHL, KHL, SHL |
| 🥊 MMA | UFC, Bellator, ONE Championship |
| 🎮 Esports | League of Legends, CS2, Dota 2, Valorant |

---

## 🏠 CASAS DE APUESTAS ANALIZADAS

1. **BetPlay** 🇨🇴
2. **Bet365** 🌍
3. **1xBet** 🌍
4. **Pinnacle** 🌍
5. **Betfair** 🇬🇧

---

## ⚠️ NOTAS IMPORTANTES

1. **Datos Simulados:** Actualmente los datos son simulados (mock). Para datos reales necesitas integrar APIs como API-Football y The Odds API.

2. **Apuestas Responsables:** Esta herramienta es solo para análisis. Apuesta responsablemente y solo lo que puedas permitirte perder.

3. **No es consejo financiero:** Las predicciones son probabilísticas. No garantizan ganancias.

---

## 🔧 SOPORTE TÉCNICO

### URLs de tus servicios:
- **Frontend:** https://mellifluous-sherbet-50a651.netlify.app
- **Backend:** https://sportsbetai.onrender.com

### Si la app no carga:
1. El backend en Render se "duerme" después de 15 min de inactividad
2. La primera visita puede tardar ~30 segundos en despertar
3. Recarga la página y espera

---

## 📊 ESTADÍSTICAS QUE VERÁS

- **Win Rate:** Porcentaje de predicciones ganadas
- **ROI:** Retorno sobre la inversión
- **Profit:** Ganancia/pérdida total
- **xG:** Expected Goals (goles esperados)
- **Forma:** Últimos 5 resultados (W=Ganado, D=Empate, L=Perdido)

---

¡Disfruta de SportsBetAI! 🎯🏆
