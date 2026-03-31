import React, { useState, useEffect } from "react";
import { Layout } from "../components/Layout";
import { api } from "../App";
import { toast } from "sonner";
import {
  Lightning,
  TrendUp,
  Target,
  Funnel,
  TelegramLogo,
  ArrowsClockwise,
  CaretUp,
  Info
} from "@phosphor-icons/react";

export default function ValueBetsPage() {
  const [valueBets, setValueBets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [minValue, setMinValue] = useState(3);
  const [selectedSport, setSelectedSport] = useState("");
  const [sendingAlert, setSendingAlert] = useState(null);

  useEffect(() => {
    loadValueBets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [minValue, selectedSport]);

  const loadValueBets = async () => {
    setLoading(true);
    try {
      let url = `/value-bets?min_value=${minValue}`;
      if (selectedSport) url += `&sport=${selectedSport}`;
      const response = await api.get(url);
      setValueBets(response.data.value_bets || []);
    } catch (error) {
      toast.error("Error cargando value bets");
    } finally {
      setLoading(false);
    }
  };

  const sendToTelegram = async (bet) => {
    setSendingAlert(bet.id);
    try {
      await api.post("/telegram/send-alert", bet);
      toast.success("Alerta enviada a Telegram");
    } catch (error) {
      if (error.response?.data?.detail === "Telegram no configurado") {
        toast.error("Configura tu Telegram primero en Ajustes");
      } else {
        toast.error("Error enviando alerta");
      }
    } finally {
      setSendingAlert(null);
    }
  };

  const getValueColor = (value) => {
    if (value >= 10) return "text-[#CCFF00]";
    if (value >= 5) return "text-[#00E5FF]";
    return "text-white";
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return "bg-[#CCFF00]";
    if (confidence >= 60) return "bg-[#00E5FF]";
    return "bg-[#A1A1AA]";
  };

  const ValueBetCard = ({ bet }) => (
    <div 
      className={`bg-[#0A0A0A] border border-[#27272A] hover:border-[#CCFF00]/50 transition-colors ${
        bet.value_percentage >= 10 ? "value-glow" : ""
      }`}
      data-testid="value-bet-card"
    >
      {/* Header */}
      <div className="px-4 py-3 border-b border-[#27272A] flex items-center justify-between bg-[#0F0F0F]">
        <div className="flex items-center gap-2">
          <span className="badge-league">{bet.match.league}</span>
          <span className="text-[10px] text-[#52525B] uppercase">{bet.match.sport}</span>
        </div>
        <span className={`badge-value ${bet.value_percentage >= 10 ? "!bg-[#CCFF00]/20" : ""}`}>
          +{bet.value_percentage}% VALUE
        </span>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Match */}
        <div className="mb-4">
          <div className="text-sm font-medium text-white mb-1">
            {bet.match.home_team} vs {bet.match.away_team}
          </div>
          <div className="text-xs text-[#52525B]">
            {new Date(bet.match.start_time).toLocaleDateString("es-ES", {
              weekday: "short",
              day: "numeric",
              month: "short",
              hour: "2-digit",
              minute: "2-digit"
            })}
          </div>
        </div>

        {/* Selection & Odds */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <div className="text-[10px] text-[#A1A1AA] uppercase tracking-wider mb-1">Selección</div>
            <div className="text-lg font-bold text-[#CCFF00]">{bet.selection}</div>
            <div className="text-xs text-[#52525B]">Mercado: {bet.market}</div>
          </div>
          <div className="text-right">
            <div className="text-[10px] text-[#A1A1AA] uppercase tracking-wider mb-1">Cuota</div>
            <div className="font-data text-3xl font-bold text-white">{bet.odds}</div>
            <div className="text-xs text-[#52525B]">{bet.bookmaker}</div>
          </div>
        </div>

        {/* Probabilities */}
        <div className="grid grid-cols-2 gap-4 mb-4 p-3 bg-[#050505] border border-[#27272A]">
          <div>
            <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">Prob. Real</div>
            <div className="font-data text-lg font-bold text-[#CCFF00]">{bet.true_probability}%</div>
          </div>
          <div>
            <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">Prob. Implícita</div>
            <div className="font-data text-lg font-bold text-[#A1A1AA]">{bet.implied_probability}%</div>
          </div>
        </div>

        {/* Confidence Bar */}
        <div className="mb-4">
          <div className="flex justify-between items-center mb-1">
            <span className="text-[10px] text-[#A1A1AA] uppercase">Confianza</span>
            <span className="font-data text-sm font-bold text-white">{bet.confidence}%</span>
          </div>
          <div className="h-1.5 bg-[#1E1E1E] overflow-hidden">
            <div 
              className={`h-full ${getConfidenceColor(bet.confidence)}`}
              style={{ width: `${bet.confidence}%` }}
            />
          </div>
        </div>

        {/* Action */}
        <button
          onClick={() => sendToTelegram(bet)}
          disabled={sendingAlert === bet.id}
          className="w-full flex items-center justify-center gap-2 bg-[#1E1E1E] hover:bg-[#2A2A2A] text-white py-2.5 text-sm font-medium transition-colors border border-[#27272A] disabled:opacity-50"
          data-testid="send-telegram-button"
        >
          {sendingAlert === bet.id ? (
            <ArrowsClockwise size={16} className="animate-spin" />
          ) : (
            <TelegramLogo size={16} />
          )}
          Enviar a Telegram
        </button>
      </div>
    </div>
  );

  return (
    <Layout>
      <div className="space-y-6" data-testid="value-bets-page">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight text-white flex items-center gap-3">
              <Lightning size={36} weight="fill" className="text-[#CCFF00]" />
              Value Bets
            </h1>
            <p className="text-[#A1A1AA] text-sm mt-1">
              Apuestas con valor esperado positivo detectadas por IA
            </p>
          </div>
          <button
            onClick={loadValueBets}
            disabled={loading}
            className="inline-flex items-center gap-2 bg-[#1E1E1E] text-white font-bold uppercase tracking-wider text-sm h-10 px-6 hover:bg-[#2A2A2A] border border-[#27272A] transition-colors disabled:opacity-50"
            data-testid="refresh-button"
          >
            <ArrowsClockwise size={18} className={loading ? "animate-spin" : ""} />
            Actualizar
          </button>
        </div>

        {/* Info Banner */}
        <div className="bg-[#CCFF00]/5 border border-[#CCFF00]/20 p-4 flex gap-3">
          <Info size={20} className="text-[#CCFF00] flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <span className="text-[#CCFF00] font-medium">¿Qué es un Value Bet?</span>
            <span className="text-[#A1A1AA] ml-2">
              Es una apuesta donde la probabilidad real calculada es mayor que la implícita en las cuotas.
              Un valor positivo indica ventaja matemática a largo plazo.
            </span>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 items-start md:items-center">
          <div className="flex items-center gap-2">
            <Funnel size={18} className="text-[#A1A1AA]" />
            <span className="text-sm text-[#A1A1AA]">Filtros:</span>
          </div>

          <div className="flex flex-wrap gap-3">
            {/* Min Value Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-[#52525B] uppercase">Valor mín:</span>
              <select
                value={minValue}
                onChange={(e) => setMinValue(Number(e.target.value))}
                className="bg-[#050505] border border-[#27272A] text-white px-3 h-8 text-sm focus:border-[#CCFF00] outline-none"
                data-testid="min-value-filter"
              >
                <option value={1}>+1%</option>
                <option value={3}>+3%</option>
                <option value={5}>+5%</option>
                <option value={10}>+10%</option>
              </select>
            </div>

            {/* Sport Filter */}
            <div className="flex items-center gap-2">
              <span className="text-xs text-[#52525B] uppercase">Deporte:</span>
              <select
                value={selectedSport}
                onChange={(e) => setSelectedSport(e.target.value)}
                className="bg-[#050505] border border-[#27272A] text-white px-3 h-8 text-sm focus:border-[#CCFF00] outline-none"
                data-testid="sport-filter"
              >
                <option value="">Todos</option>
                <option value="football">Fútbol</option>
                <option value="basketball">Baloncesto</option>
                <option value="tennis">Tenis</option>
                <option value="mma">MMA</option>
                <option value="esports">Esports</option>
              </select>
            </div>
          </div>

          <div className="md:ml-auto">
            <span className="font-data text-sm text-[#A1A1AA]">
              {valueBets.length} value bets encontrados
            </span>
          </div>
        </div>

        {/* Value Bets Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-[#CCFF00] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : valueBets.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {valueBets.map((bet) => (
              <ValueBetCard key={bet.id} bet={bet} />
            ))}
          </div>
        ) : (
          <div className="bg-[#0A0A0A] border border-[#27272A] p-12 text-center">
            <Target size={48} className="mx-auto text-[#27272A] mb-4" />
            <p className="text-[#A1A1AA] mb-2">No se encontraron value bets</p>
            <p className="text-xs text-[#52525B]">Prueba bajando el filtro de valor mínimo</p>
          </div>
        )}
      </div>
    </Layout>
  );
}
