import React, { useState, useEffect } from "react";
import { Layout } from "../components/Layout";
import { api } from "../App";
import { toast } from "sonner";
import {
  Plus,
  Trash,
  ShoppingCart,
  X,
  Lightning,
  CheckCircle,
  CaretDown,
  Trophy,
  Target,
  Fire,
  ArrowRight,
  Sparkle,
  Calendar,
  CalendarBlank,
  TrendUp,
  TrendDown,
  Clock,
  CurrencyDollar,
  ChartLine,
  Medal,
  XCircle
} from "@phosphor-icons/react";

export default function ParlaysPage() {
  const [matches, setMatches] = useState([]);
  const [parlays, setParlays] = useState([]);
  const [parlayStats, setParlayStats] = useState(null);
  const [selections, setSelections] = useState([]);
  const [parlayName, setParlayName] = useState("");
  const [stake, setStake] = useState("");
  const [loading, setLoading] = useState(true);
  const [showCart, setShowCart] = useState(false);
  const [activeTab, setActiveTab] = useState("all"); // all, pending, won, lost
  
  // Auto generator state
  const [showGenerator, setShowGenerator] = useState(false);
  const [generatorLoading, setGeneratorLoading] = useState(false);
  const [generatedParlay, setGeneratedParlay] = useState(null);
  const [genConfig, setGenConfig] = useState({
    num_selections: 3,
    risk_level: "medium",
    sports: [],
    stake: 10000,
    date_filter: "all"
  });
  const [customDate, setCustomDate] = useState("");

  const sportOptions = [
    { value: "football", label: "Fútbol" },
    { value: "basketball", label: "Baloncesto" },
    { value: "baseball", label: "Béisbol" },
    { value: "hockey", label: "Hockey" },
    { value: "mma", label: "MMA/UFC" },
    { value: "tennis", label: "Tenis" }
  ];

  const dateOptions = [
    { value: "today", label: "Hoy", icon: Calendar },
    { value: "tomorrow", label: "Mañana", icon: CalendarBlank },
    { value: "week", label: "Esta semana", icon: CalendarBlank },
    { value: "all", label: "Todos", icon: CalendarBlank }
  ];

  // Get today and tomorrow dates for display
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);
  
  const formatDateLabel = (date) => {
    return date.toLocaleDateString('es', { weekday: 'short', day: 'numeric', month: 'short' });
  };

  useEffect(() => {
    loadData();
    loadStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadStats = async () => {
    try {
      const response = await api.get("/parlays/stats");
      setParlayStats(response.data);
    } catch (error) {
      console.error("Error loading stats:", error);
    }
  };

  const loadData = async () => {
    try {
      const [matchesRes, parlaysRes] = await Promise.all([
        api.get("/matches?limit=30"),
        api.get("/parlays?limit=50")
      ]);
      setMatches(matchesRes.data.matches || []);
      setParlays(parlaysRes.data.parlays || []);
    } catch (error) {
      toast.error("Error cargando datos");
    } finally {
      setLoading(false);
    }
  };

  const markParlayResult = async (parlayId, result) => {
    try {
      await api.put(`/parlays/${parlayId}/result`, { result });
      toast.success(result === "won" ? "¡Combinada ganada!" : "Combinada perdida");
      loadData();
      loadStats();
    } catch (error) {
      toast.error("Error actualizando resultado");
    }
  };

  const generateAutoParlay = async () => {
    setGeneratorLoading(true);
    try {
      // Prepare config with date filter
      const configToSend = {
        ...genConfig,
        date_filter: genConfig.date_filter === "custom" ? customDate : genConfig.date_filter
      };
      const response = await api.post("/parlays/generate", configToSend);
      setGeneratedParlay(response.data);
      toast.success("¡Combinada generada con éxito!");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error generando combinada");
    } finally {
      setGeneratorLoading(false);
    }
  };

  const saveGeneratedParlay = async () => {
    if (!generatedParlay) return;
    
    try {
      await api.post("/parlays", {
        selections: generatedParlay.selections,
        name: generatedParlay.name,
        stake: genConfig.stake
      });
      toast.success("Combinada guardada");
      setGeneratedParlay(null);
      setShowGenerator(false);
      loadData();
      loadStats();
    } catch (error) {
      toast.error("Error guardando combinada");
    }
  };

  const addSelection = (match, market, selection, odds) => {
    if (selections.length >= 6) {
      toast.error("Máximo 6 selecciones por combinada");
      return;
    }
    
    const exists = selections.find(s => s.match_id === match.id);
    if (exists) {
      toast.error("Ya tienes una selección de este partido");
      return;
    }

    setSelections([...selections, {
      match_id: match.id,
      home_team: match.home_team,
      away_team: match.away_team,
      league: match.league,
      market,
      selection,
      odds
    }]);
    setShowCart(true);
    toast.success("Selección añadida");
  };

  const removeSelection = (matchId) => {
    setSelections(selections.filter(s => s.match_id !== matchId));
  };

  const getTotalOdds = () => {
    return selections.reduce((acc, sel) => acc * sel.odds, 1).toFixed(2);
  };

  const getPotentialProfit = () => {
    const stakeNum = parseFloat(stake) || 0;
    return (stakeNum * parseFloat(getTotalOdds())).toFixed(2);
  };

  const createParlay = async () => {
    if (selections.length < 2) {
      toast.error("Mínimo 2 selecciones para crear combinada");
      return;
    }

    try {
      await api.post("/parlays", {
        selections: selections,
        name: parlayName || "Mi Combinada",
        stake: parseFloat(stake) || null
      });
      toast.success("Combinada creada");
      setSelections([]);
      setParlayName("");
      setStake("");
      setShowCart(false);
      loadData();
    } catch (error) {
      toast.error("Error creando combinada");
    }
  };

  const deleteParlay = async (parlayId) => {
    try {
      await api.delete(`/parlays/${parlayId}`);
      toast.success("Combinada eliminada");
      loadData();
    } catch (error) {
      toast.error("Error eliminando combinada");
    }
  };

  const getBestOdds = (odds, market) => {
    if (!odds) return { bookmaker: "", value: 0 };
    let best = { bookmaker: "", value: 0 };
    for (const [bookmaker, markets] of Object.entries(odds)) {
      if (markets[market] > best.value) {
        best = { bookmaker, value: markets[market] };
      }
    }
    return best;
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return "";
    const date = new Date(dateStr);
    return date.toLocaleDateString('es', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
  };

  const RiskBadge = ({ level }) => {
    const config = {
      low: { color: "bg-green-500/20 text-green-400 border-green-500/30", label: "BAJO", icon: Target },
      medium: { color: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30", label: "MEDIO", icon: Trophy },
      high: { color: "bg-red-500/20 text-red-400 border-red-500/30", label: "ALTO", icon: Fire }
    };
    const cfg = config[level] || config.medium;
    const Icon = cfg.icon;
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium border ${cfg.color}`}>
        <Icon size={12} weight="fill" />
        {cfg.label}
      </span>
    );
  };

  const SelectionWithAnalysis = ({ sel, idx }) => {
    const [expanded, setExpanded] = useState(false);
    
    return (
      <div className="bg-[#050505] border border-[#27272A] overflow-hidden">
        {/* Main Selection Info */}
        <div 
          className="p-4 cursor-pointer hover:bg-[#0A0A0A] transition-colors"
          onClick={() => setExpanded(!expanded)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="w-5 h-5 bg-[#CCFF00] text-black text-xs font-bold flex items-center justify-center">
                  {idx + 1}
                </span>
                <span className="text-[10px] uppercase tracking-wider text-[#52525B]">{sel.league}</span>
                <span className="text-[10px] text-[#00E5FF]">{sel.confidence}% conf.</span>
              </div>
              <div className="text-sm text-white">{sel.match}</div>
              <div className="text-sm text-[#CCFF00] font-medium mt-1">
                <ArrowRight size={12} className="inline mr-1" />
                {sel.selection}
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="font-data text-xl font-bold text-white">{sel.odds?.toFixed(2)}</div>
                <div className="text-[10px] text-[#52525B]">{sel.bookmaker}</div>
              </div>
              <CaretDown 
                size={16} 
                className={`text-[#A1A1AA] transition-transform ${expanded ? 'rotate-180' : ''}`}
              />
            </div>
          </div>
        </div>
        
        {/* Expanded Analysis */}
        {expanded && sel.analysis && (
          <div className="border-t border-[#27272A] p-4 bg-[#0A0A0A] space-y-4">
            {/* Summary */}
            <div className="flex items-start gap-2">
              <Sparkle size={16} className="text-[#CCFF00] mt-0.5 flex-shrink-0" />
              <p className="text-sm text-white">{sel.analysis.summary}</p>
            </div>
            
            {/* Reasons */}
            <div className="space-y-2">
              <h4 className="text-xs uppercase tracking-wider text-[#A1A1AA] font-medium">
                Por qué esta selección:
              </h4>
              <ul className="space-y-1.5">
                {sel.analysis.reasons?.map((reason, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-[#A1A1AA]">
                    <CheckCircle size={14} className="text-[#CCFF00] mt-0.5 flex-shrink-0" />
                    <span>{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Metrics Grid */}
            {sel.analysis.metrics && (
              <div className="grid grid-cols-3 gap-2">
                <div className="bg-[#050505] p-2 text-center">
                  <div className="text-[10px] text-[#52525B] uppercase">Prob. Implícita</div>
                  <div className="font-data text-lg font-bold text-white">
                    {sel.analysis.metrics.implied_probability}%
                  </div>
                </div>
                <div className="bg-[#050505] p-2 text-center">
                  <div className="text-[10px] text-[#52525B] uppercase">Valor</div>
                  <div className={`font-data text-lg font-bold ${
                    sel.analysis.metrics.value_pct > 3 ? 'text-[#CCFF00]' : 'text-white'
                  }`}>
                    +{sel.analysis.metrics.value_pct}%
                  </div>
                </div>
                <div className="bg-[#050505] p-2 text-center">
                  <div className="text-[10px] text-[#52525B] uppercase">Casas</div>
                  <div className="font-data text-lg font-bold text-white">
                    {sel.analysis.metrics.bookmakers_analyzed}
                  </div>
                </div>
              </div>
            )}
            
            {/* Odds Comparison */}
            {sel.analysis.odds_comparison && sel.analysis.odds_comparison.length > 0 && (
              <div>
                <h4 className="text-xs uppercase tracking-wider text-[#A1A1AA] font-medium mb-2">
                  Comparación de cuotas:
                </h4>
                <div className="flex flex-wrap gap-2">
                  {sel.analysis.odds_comparison.map((comp, i) => (
                    <div 
                      key={i}
                      className={`px-2 py-1 text-xs ${
                        i === 0 
                          ? 'bg-[#CCFF00]/20 border border-[#CCFF00]/50 text-[#CCFF00]' 
                          : 'bg-[#1A1A1A] text-[#A1A1AA]'
                      }`}
                    >
                      {comp.bookmaker}: <span className="font-data font-bold">{comp.odds?.toFixed(2)}</span>
                      {i === 0 && <span className="ml-1 text-[10px]">MEJOR</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Recommendation */}
            {sel.analysis.recommendation && (
              <div className="bg-[#00E5FF]/10 border border-[#00E5FF]/30 p-3">
                <p className="text-xs text-[#00E5FF]">
                  <Lightning size={12} className="inline mr-1" weight="fill" />
                  {sel.analysis.recommendation}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    );
  };

  const MatchCard = ({ match }) => {
    const bestHome = getBestOdds(match.odds, "home");
    const bestDraw = getBestOdds(match.odds, "draw");
    const bestAway = getBestOdds(match.odds, "away");
    const isSelected = selections.find(s => s.match_id === match.id);

    return (
      <div className={`bg-[#0A0A0A] border ${isSelected ? "border-[#CCFF00]" : "border-[#27272A]"} transition-colors`}>
        <div className="px-4 py-2 border-b border-[#27272A] bg-[#0F0F0F] flex justify-between items-center">
          <span className="badge-league">{match.league}</span>
          <span className="text-[10px] text-[#52525B]">{formatDate(match.start_time)}</span>
        </div>
        <div className="p-4">
          <div className="text-sm font-medium text-white mb-1">{match.home_team}</div>
          <div className="text-sm text-[#A1A1AA] mb-3">{match.away_team}</div>
          
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => bestHome.value > 0 && addSelection(match, "home", match.home_team, bestHome.value)}
              disabled={bestHome.value === 0}
              className={`p-2 text-center border transition-colors ${
                isSelected?.market === "home"
                  ? "bg-[#CCFF00] border-[#CCFF00] text-black"
                  : bestHome.value > 0 
                    ? "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                    : "bg-[#050505] border-[#27272A] opacity-50 cursor-not-allowed"
              }`}
              data-testid="select-home"
            >
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">1</div>
              <div className="font-data font-bold">{bestHome.value > 0 ? bestHome.value.toFixed(2) : "-"}</div>
            </button>
            <button
              onClick={() => bestDraw.value > 0 && addSelection(match, "draw", "Empate", bestDraw.value)}
              disabled={bestDraw.value === 0}
              className={`p-2 text-center border transition-colors ${
                isSelected?.market === "draw"
                  ? "bg-[#CCFF00] border-[#CCFF00] text-black"
                  : bestDraw.value > 0
                    ? "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                    : "bg-[#050505] border-[#27272A] opacity-50 cursor-not-allowed"
              }`}
              data-testid="select-draw"
            >
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">X</div>
              <div className="font-data font-bold">{bestDraw.value > 0 ? bestDraw.value.toFixed(2) : "-"}</div>
            </button>
            <button
              onClick={() => bestAway.value > 0 && addSelection(match, "away", match.away_team, bestAway.value)}
              disabled={bestAway.value === 0}
              className={`p-2 text-center border transition-colors ${
                isSelected?.market === "away"
                  ? "bg-[#CCFF00] border-[#CCFF00] text-black"
                  : bestAway.value > 0
                    ? "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                    : "bg-[#050505] border-[#27272A] opacity-50 cursor-not-allowed"
              }`}
              data-testid="select-away"
            >
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">2</div>
              <div className="font-data font-bold">{bestAway.value > 0 ? bestAway.value.toFixed(2) : "-"}</div>
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="parlays-page">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight text-white">
              Combinadas
            </h1>
            <p className="text-[#A1A1AA] text-sm mt-1">
              Crea combinadas manuales o genera automáticamente con IA
            </p>
          </div>
          
          <div className="flex items-center gap-3">
            <button
              onClick={() => setShowGenerator(true)}
              className="bg-gradient-to-r from-[#CCFF00] to-[#00E5FF] text-black font-bold uppercase tracking-wider px-4 h-11 hover:opacity-90 transition-opacity flex items-center gap-2"
              data-testid="auto-generate-button"
            >
              <Sparkle size={20} weight="fill" />
              Generar Auto
            </button>
            
            <button
              onClick={() => setShowCart(true)}
              className="relative bg-[#0A0A0A] border border-[#27272A] text-white p-2.5 hover:border-[#CCFF00]/50 transition-colors"
              data-testid="cart-button"
            >
              <ShoppingCart size={24} />
              {selections.length > 0 && (
                <span className="absolute -top-2 -right-2 w-5 h-5 bg-[#CCFF00] text-black text-xs font-bold flex items-center justify-center">
                  {selections.length}
                </span>
              )}
            </button>
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Matches Section */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="font-heading text-lg font-bold uppercase tracking-wider text-white">
              Selección Manual
            </h2>
            
            {loading ? (
              <div className="flex items-center justify-center h-64">
                <div className="w-8 h-8 border-2 border-[#CCFF00] border-t-transparent rounded-full animate-spin" />
              </div>
            ) : matches.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-4">
                {matches.map((match) => (
                  <MatchCard key={match.id} match={match} />
                ))}
              </div>
            ) : (
              <div className="bg-[#0A0A0A] border border-[#27272A] p-8 text-center text-[#A1A1AA]">
                No hay partidos disponibles
              </div>
            )}
          </div>

          {/* Stats and Parlays Section */}
          <div className="space-y-4">
            {/* ROI Stats Panel */}
            {parlayStats && (parlayStats.total_parlays > 0 || parlays.length > 0) && (
              <div className="bg-[#0A0A0A] border border-[#27272A] p-4">
                <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white mb-4 flex items-center gap-2">
                  <ChartLine size={16} className="text-[#CCFF00]" />
                  Mi Rendimiento
                </h2>
                
                {/* Main Stats Grid */}
                <div className="grid grid-cols-2 gap-2 mb-4">
                  <div className="bg-[#050505] p-3 text-center">
                    <div className="text-[10px] text-[#52525B] uppercase mb-1">Win Rate</div>
                    <div className={`font-data text-2xl font-bold ${
                      parlayStats.win_rate >= 50 ? 'text-[#CCFF00]' : 'text-[#A1A1AA]'
                    }`}>
                      {parlayStats.win_rate}%
                    </div>
                  </div>
                  <div className="bg-[#050505] p-3 text-center">
                    <div className="text-[10px] text-[#52525B] uppercase mb-1">ROI</div>
                    <div className={`font-data text-2xl font-bold ${
                      parlayStats.roi >= 0 ? 'text-[#CCFF00]' : 'text-[#FF2E2E]'
                    }`}>
                      {parlayStats.roi >= 0 ? '+' : ''}{parlayStats.roi}%
                    </div>
                  </div>
                </div>
                
                {/* Profit/Loss */}
                <div className={`p-3 mb-4 ${
                  parlayStats.total_profit >= 0 
                    ? 'bg-[#CCFF00]/10 border border-[#CCFF00]/30' 
                    : 'bg-[#FF2E2E]/10 border border-[#FF2E2E]/30'
                }`}>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-[#A1A1AA]">Beneficio Total</span>
                    <span className={`font-data text-xl font-bold ${
                      parlayStats.total_profit >= 0 ? 'text-[#CCFF00]' : 'text-[#FF2E2E]'
                    }`}>
                      {parlayStats.total_profit >= 0 ? '+' : ''}${parlayStats.total_profit?.toLocaleString()}
                    </span>
                  </div>
                  <div className="text-[10px] text-[#52525B] mt-1">
                    De ${parlayStats.total_staked?.toLocaleString()} apostados
                  </div>
                </div>
                
                {/* Win/Loss Stats */}
                <div className="grid grid-cols-3 gap-2 mb-4">
                  <div className="bg-[#050505] p-2 text-center">
                    <div className="flex items-center justify-center gap-1 text-[#CCFF00]">
                      <CheckCircle size={14} weight="fill" />
                      <span className="font-data text-lg font-bold">{parlayStats.won}</span>
                    </div>
                    <div className="text-[10px] text-[#52525B]">Ganadas</div>
                  </div>
                  <div className="bg-[#050505] p-2 text-center">
                    <div className="flex items-center justify-center gap-1 text-[#FF2E2E]">
                      <XCircle size={14} weight="fill" />
                      <span className="font-data text-lg font-bold">{parlayStats.lost}</span>
                    </div>
                    <div className="text-[10px] text-[#52525B]">Perdidas</div>
                  </div>
                  <div className="bg-[#050505] p-2 text-center">
                    <div className="flex items-center justify-center gap-1 text-[#A1A1AA]">
                      <Clock size={14} />
                      <span className="font-data text-lg font-bold">{parlayStats.pending}</span>
                    </div>
                    <div className="text-[10px] text-[#52525B]">Pendientes</div>
                  </div>
                </div>
                
                {/* Current Streak */}
                {parlayStats.current_streak?.count > 0 && (
                  <div className={`p-2 text-center text-xs ${
                    parlayStats.current_streak.type === 'won' 
                      ? 'bg-[#CCFF00]/10 text-[#CCFF00]' 
                      : 'bg-[#FF2E2E]/10 text-[#FF2E2E]'
                  }`}>
                    {parlayStats.current_streak.type === 'won' ? '🔥' : '❄️'} 
                    Racha actual: {parlayStats.current_streak.count} {parlayStats.current_streak.type === 'won' ? 'victorias' : 'derrotas'}
                  </div>
                )}
              </div>
            )}

            {/* Parlays List */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-heading text-lg font-bold uppercase tracking-wider text-white">
                  Mis Combinadas
                </h2>
              </div>
              
              {/* Filter Tabs */}
              <div className="flex gap-1 mb-4">
                {[
                  { key: "all", label: "Todas" },
                  { key: "pending", label: "Pendientes" },
                  { key: "won", label: "Ganadas" },
                  { key: "lost", label: "Perdidas" }
                ].map(tab => (
                  <button
                    key={tab.key}
                    onClick={() => setActiveTab(tab.key)}
                    className={`px-3 py-1.5 text-xs uppercase tracking-wider transition-colors ${
                      activeTab === tab.key
                        ? 'bg-[#CCFF00] text-black'
                        : 'bg-[#050505] text-[#A1A1AA] hover:text-white'
                    }`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
              
              {parlays.length > 0 ? (
                <div className="space-y-3">
                  {parlays
                    .filter(p => activeTab === "all" || p.status === activeTab || (activeTab === "pending" && p.status === "active"))
                    .map((parlay) => (
                    <div key={parlay.id} className={`bg-[#0A0A0A] border transition-colors ${
                      parlay.status === 'won' ? 'border-[#CCFF00]/50' :
                      parlay.status === 'lost' ? 'border-[#FF2E2E]/50' :
                      'border-[#27272A]'
                    }`}>
                      {/* Header */}
                      <div className="p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium text-white">{parlay.name}</span>
                            {/* Status Badge */}
                            {parlay.status === 'won' && (
                              <span className="px-2 py-0.5 text-[10px] uppercase bg-[#CCFF00]/20 text-[#CCFF00] border border-[#CCFF00]/30">
                                Ganada
                              </span>
                            )}
                            {parlay.status === 'lost' && (
                              <span className="px-2 py-0.5 text-[10px] uppercase bg-[#FF2E2E]/20 text-[#FF2E2E] border border-[#FF2E2E]/30">
                                Perdida
                              </span>
                            )}
                            {(parlay.status === 'pending' || parlay.status === 'active') && (
                              <span className="px-2 py-0.5 text-[10px] uppercase bg-[#A1A1AA]/20 text-[#A1A1AA] border border-[#A1A1AA]/30">
                                Pendiente
                              </span>
                            )}
                          </div>
                          <button
                            onClick={() => deleteParlay(parlay.id)}
                            className="text-[#A1A1AA] hover:text-[#FF2E2E] transition-colors"
                            data-testid="delete-parlay"
                          >
                            <Trash size={16} />
                          </button>
                        </div>
                        
                        {/* Selections */}
                        <div className="space-y-1.5 mb-3">
                          {parlay.selections?.slice(0, 3).map((sel, idx) => (
                            <div key={idx} className="text-xs text-[#A1A1AA] flex justify-between">
                              <span className="truncate mr-2">{sel.selection || sel.match}</span>
                              <span className="font-data">{(sel.odds || 0).toFixed(2)}</span>
                            </div>
                          ))}
                          {parlay.selections?.length > 3 && (
                            <div className="text-xs text-[#52525B]">+{parlay.selections.length - 3} más</div>
                          )}
                        </div>
                        
                        {/* Footer */}
                        <div className="pt-3 border-t border-[#27272A]">
                          <div className="flex justify-between items-center mb-2">
                            <div>
                              <span className="text-xs text-[#A1A1AA]">{parlay.selections?.length || 0} sel.</span>
                              {parlay.stake && (
                                <span className="text-xs text-[#52525B] ml-2">
                                  Apuesta: ${parlay.stake?.toLocaleString()}
                                </span>
                              )}
                            </div>
                            <span className="font-data text-lg font-bold text-[#CCFF00]">@{parlay.total_odds}</span>
                          </div>
                          
                          {/* Result or Action Buttons */}
                          {parlay.status === 'won' && (
                            <div className="bg-[#CCFF00]/10 p-2 text-center">
                              <span className="text-[#CCFF00] font-data font-bold">
                                +${parlay.actual_profit?.toLocaleString()}
                              </span>
                            </div>
                          )}
                          {parlay.status === 'lost' && (
                            <div className="bg-[#FF2E2E]/10 p-2 text-center">
                              <span className="text-[#FF2E2E] font-data font-bold">
                                -${Math.abs(parlay.actual_profit || parlay.stake || 0)?.toLocaleString()}
                              </span>
                            </div>
                          )}
                          {(parlay.status === 'pending' || parlay.status === 'active') && (
                            <div className="grid grid-cols-2 gap-2">
                              <button
                                onClick={() => markParlayResult(parlay.id, 'won')}
                                className="py-2 bg-[#CCFF00]/20 border border-[#CCFF00]/50 text-[#CCFF00] text-xs font-bold uppercase hover:bg-[#CCFF00]/30 transition-colors flex items-center justify-center gap-1"
                                data-testid="mark-won"
                              >
                                <CheckCircle size={14} weight="bold" />
                                Ganó
                              </button>
                              <button
                                onClick={() => markParlayResult(parlay.id, 'lost')}
                                className="py-2 bg-[#FF2E2E]/20 border border-[#FF2E2E]/50 text-[#FF2E2E] text-xs font-bold uppercase hover:bg-[#FF2E2E]/30 transition-colors flex items-center justify-center gap-1"
                                data-testid="mark-lost"
                              >
                                <XCircle size={14} weight="bold" />
                                Perdió
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-[#0A0A0A] border border-[#27272A] p-8 text-center text-[#A1A1AA] text-sm">
                  No tienes combinadas guardadas
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Auto Generator Modal */}
        {showGenerator && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/70" onClick={() => !generatorLoading && setShowGenerator(false)} />
            <div className="relative bg-[#0A0A0A] border border-[#27272A] w-full max-w-lg max-h-[90vh] overflow-y-auto">
              {/* Header */}
              <div className="sticky top-0 bg-[#0A0A0A] px-6 py-4 border-b border-[#27272A] flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-[#CCFF00] to-[#00E5FF] flex items-center justify-center">
                    <Lightning size={24} weight="fill" className="text-black" />
                  </div>
                  <div>
                    <h3 className="font-heading font-bold uppercase text-white">Generador Automático</h3>
                    <p className="text-xs text-[#A1A1AA]">IA analiza y sugiere la mejor combinada</p>
                  </div>
                </div>
                <button
                  onClick={() => !generatorLoading && setShowGenerator(false)}
                  className="text-[#A1A1AA] hover:text-white"
                >
                  <X size={24} />
                </button>
              </div>

              <div className="p-6 space-y-6">
                {!generatedParlay ? (
                  <>
                    {/* Configuration */}
                    <div className="space-y-4">
                      {/* Number of selections */}
                      <div>
                        <label className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-2 block">
                          Número de Partidos
                        </label>
                        <div className="grid grid-cols-5 gap-2">
                          {[2, 3, 4, 5, 6].map(num => (
                            <button
                              key={num}
                              onClick={() => setGenConfig({...genConfig, num_selections: num})}
                              className={`h-12 font-data text-lg font-bold border transition-colors ${
                                genConfig.num_selections === num
                                  ? "bg-[#CCFF00] border-[#CCFF00] text-black"
                                  : "bg-[#050505] border-[#27272A] text-white hover:border-[#CCFF00]/50"
                              }`}
                            >
                              {num}
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Risk Level */}
                      <div>
                        <label className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-2 block">
                          Nivel de Riesgo
                        </label>
                        <div className="grid grid-cols-3 gap-2">
                          {[
                            { value: "low", label: "Bajo", desc: "Cuotas 1.15-1.60", icon: Target, color: "green" },
                            { value: "medium", label: "Medio", desc: "Cuotas 1.40-2.20", icon: Trophy, color: "yellow" },
                            { value: "high", label: "Alto", desc: "Cuotas 1.80-3.50", icon: Fire, color: "red" }
                          ].map(risk => (
                            <button
                              key={risk.value}
                              onClick={() => setGenConfig({...genConfig, risk_level: risk.value})}
                              className={`p-3 border transition-colors text-left ${
                                genConfig.risk_level === risk.value
                                  ? "bg-[#CCFF00]/10 border-[#CCFF00]"
                                  : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                              }`}
                            >
                              <risk.icon size={20} weight="fill" className={`mb-2 ${
                                risk.color === "green" ? "text-green-400" :
                                risk.color === "yellow" ? "text-yellow-400" : "text-red-400"
                              }`} />
                              <div className="text-sm font-medium text-white">{risk.label}</div>
                              <div className="text-[10px] text-[#52525B]">{risk.desc}</div>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Sports Filter */}
                      <div>
                        <label className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-2 block">
                          Deportes (opcional)
                        </label>
                        <div className="flex flex-wrap gap-2">
                          {sportOptions.map(sport => (
                            <button
                              key={sport.value}
                              onClick={() => {
                                const current = genConfig.sports || [];
                                const updated = current.includes(sport.value)
                                  ? current.filter(s => s !== sport.value)
                                  : [...current, sport.value];
                                setGenConfig({...genConfig, sports: updated});
                              }}
                              className={`px-3 py-1.5 text-xs border transition-colors ${
                                genConfig.sports?.includes(sport.value)
                                  ? "bg-[#CCFF00] border-[#CCFF00] text-black"
                                  : "bg-[#050505] border-[#27272A] text-[#A1A1AA] hover:border-[#CCFF00]/50"
                              }`}
                            >
                              {sport.label}
                            </button>
                          ))}
                        </div>
                        <p className="text-[10px] text-[#52525B] mt-1">Deja vacío para incluir todos</p>
                      </div>

                      {/* Date Filter */}
                      <div>
                        <label className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-2 block flex items-center gap-2">
                          <Calendar size={14} />
                          Fecha de Partidos
                        </label>
                        <div className="grid grid-cols-2 gap-2 mb-2">
                          <button
                            onClick={() => setGenConfig({...genConfig, date_filter: "today"})}
                            className={`p-3 border transition-colors text-left ${
                              genConfig.date_filter === "today"
                                ? "bg-[#CCFF00]/10 border-[#CCFF00]"
                                : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                            }`}
                          >
                            <div className="text-sm font-medium text-white">Hoy</div>
                            <div className="text-[10px] text-[#52525B]">{formatDateLabel(today)}</div>
                          </button>
                          <button
                            onClick={() => setGenConfig({...genConfig, date_filter: "tomorrow"})}
                            className={`p-3 border transition-colors text-left ${
                              genConfig.date_filter === "tomorrow"
                                ? "bg-[#CCFF00]/10 border-[#CCFF00]"
                                : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                            }`}
                          >
                            <div className="text-sm font-medium text-white">Mañana</div>
                            <div className="text-[10px] text-[#52525B]">{formatDateLabel(tomorrow)}</div>
                          </button>
                          <button
                            onClick={() => setGenConfig({...genConfig, date_filter: "week"})}
                            className={`p-3 border transition-colors text-left ${
                              genConfig.date_filter === "week"
                                ? "bg-[#CCFF00]/10 border-[#CCFF00]"
                                : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                            }`}
                          >
                            <div className="text-sm font-medium text-white">Esta semana</div>
                            <div className="text-[10px] text-[#52525B]">Próximos 7 días</div>
                          </button>
                          <button
                            onClick={() => setGenConfig({...genConfig, date_filter: "all"})}
                            className={`p-3 border transition-colors text-left ${
                              genConfig.date_filter === "all"
                                ? "bg-[#CCFF00]/10 border-[#CCFF00]"
                                : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                            }`}
                          >
                            <div className="text-sm font-medium text-white">Todos</div>
                            <div className="text-[10px] text-[#52525B]">Sin filtro de fecha</div>
                          </button>
                        </div>
                        
                        {/* Custom date picker */}
                        <div className="mt-3">
                          <button
                            onClick={() => setGenConfig({...genConfig, date_filter: "custom"})}
                            className={`w-full p-2 border transition-colors text-left ${
                              genConfig.date_filter === "custom"
                                ? "bg-[#CCFF00]/10 border-[#CCFF00]"
                                : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-white">Elegir fecha específica</span>
                              <CalendarBlank size={16} className="text-[#A1A1AA]" />
                            </div>
                          </button>
                          {genConfig.date_filter === "custom" && (
                            <input
                              type="date"
                              value={customDate}
                              onChange={(e) => setCustomDate(e.target.value)}
                              min={today.toISOString().split('T')[0]}
                              className="w-full mt-2 bg-[#050505] border border-[#CCFF00] text-white px-4 h-12 focus:outline-none"
                            />
                          )}
                        </div>
                      </div>

                      {/* Stake */}
                      <div>
                        <label className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-2 block">
                          Monto a Apostar ($)
                        </label>
                        <input
                          type="number"
                          value={genConfig.stake}
                          onChange={(e) => setGenConfig({...genConfig, stake: parseFloat(e.target.value) || 0})}
                          className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 font-data text-lg focus:border-[#CCFF00] outline-none"
                          placeholder="10000"
                        />
                      </div>
                    </div>

                    {/* Generate Button */}
                    <button
                      onClick={generateAutoParlay}
                      disabled={generatorLoading}
                      className="w-full bg-gradient-to-r from-[#CCFF00] to-[#00E5FF] text-black font-bold uppercase tracking-wider h-14 hover:opacity-90 transition-opacity flex items-center justify-center gap-2 disabled:opacity-50"
                      data-testid="generate-parlay-button"
                    >
                      {generatorLoading ? (
                        <>
                          <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                          Analizando partidos...
                        </>
                      ) : (
                        <>
                          <Lightning size={24} weight="fill" />
                          Generar Combinada
                        </>
                      )}
                    </button>
                  </>
                ) : (
                  /* Generated Result */
                  <div className="space-y-4">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-heading font-bold text-white uppercase">{generatedParlay.name}</h4>
                        <div className="flex items-center gap-2 mt-1">
                          <RiskBadge level={generatedParlay.risk_level} />
                          <span className="text-xs text-[#A1A1AA]">{generatedParlay.selections?.length} selecciones</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-[#A1A1AA]">Cuota Total</div>
                        <div className="font-data text-3xl font-bold text-[#CCFF00]">@{generatedParlay.total_odds}</div>
                      </div>
                    </div>

                    {/* Recommendation */}
                    {generatedParlay.recommendation && (
                      <div className={`p-4 border ${
                        generatedParlay.recommendation.rating === "ALTA" ? "bg-green-500/10 border-green-500/30" :
                        generatedParlay.recommendation.rating === "MEDIA" ? "bg-yellow-500/10 border-yellow-500/30" :
                        "bg-red-500/10 border-red-500/30"
                      }`}>
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-lg">{generatedParlay.recommendation.emoji}</span>
                          <span className="font-bold text-white">Probabilidad: {generatedParlay.recommendation.win_probability}%</span>
                        </div>
                        <p className="text-sm text-[#A1A1AA]">{generatedParlay.recommendation.message}</p>
                        <p className="text-xs text-[#00E5FF] mt-2">{generatedParlay.recommendation.tip}</p>
                      </div>
                    )}

                    {/* Selections with Analysis */}
                    <div className="space-y-3">
                      {generatedParlay.selections?.map((sel, idx) => (
                        <SelectionWithAnalysis key={idx} sel={sel} idx={idx} />
                      ))}
                    </div>

                    {/* Potential Profit */}
                    <div className="bg-[#050505] border border-[#CCFF00]/30 p-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <div className="text-xs text-[#A1A1AA]">Apuesta</div>
                          <div className="font-data text-xl text-white">${genConfig.stake?.toLocaleString()}</div>
                        </div>
                        <ArrowRight size={24} className="text-[#CCFF00]" />
                        <div className="text-right">
                          <div className="text-xs text-[#A1A1AA]">Ganancia Potencial</div>
                          <div className="font-data text-2xl font-bold text-[#CCFF00]">
                            ${generatedParlay.potential_profit?.toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        onClick={() => setGeneratedParlay(null)}
                        className="bg-[#050505] border border-[#27272A] text-white font-bold uppercase tracking-wider h-12 hover:border-[#CCFF00]/50 transition-colors"
                      >
                        Regenerar
                      </button>
                      <button
                        onClick={saveGeneratedParlay}
                        className="bg-[#CCFF00] text-black font-bold uppercase tracking-wider h-12 hover:bg-[#B3E600] transition-colors flex items-center justify-center gap-2"
                      >
                        <CheckCircle size={20} weight="bold" />
                        Guardar
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Cart Drawer */}
        {showCart && (
          <div className="fixed inset-0 z-50 flex">
            <div className="absolute inset-0 bg-black/50" onClick={() => setShowCart(false)} />
            <div className="absolute right-0 top-0 bottom-0 w-full max-w-md bg-[#0A0A0A] border-l border-[#27272A] overflow-y-auto">
              <div className="sticky top-0 bg-[#0A0A0A] px-4 py-4 border-b border-[#27272A] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShoppingCart size={20} className="text-[#CCFF00]" />
                  <span className="font-heading font-bold uppercase">Boleto Manual</span>
                </div>
                <button
                  onClick={() => setShowCart(false)}
                  className="text-[#A1A1AA] hover:text-white"
                >
                  <X size={24} />
                </button>
              </div>

              <div className="p-4 space-y-4">
                {selections.length > 0 ? (
                  <>
                    {/* Selections */}
                    <div className="space-y-2">
                      {selections.map((sel) => (
                        <div key={sel.match_id} className="bg-[#050505] border border-[#27272A] p-3">
                          <div className="flex items-start justify-between">
                            <div className="flex-1 min-w-0">
                              <div className="text-xs text-[#52525B] mb-1">{sel.league}</div>
                              <div className="text-sm text-white truncate">
                                {sel.home_team} vs {sel.away_team}
                              </div>
                              <div className="text-sm text-[#CCFF00] mt-1">{sel.selection}</div>
                            </div>
                            <div className="flex items-center gap-2 ml-2">
                              <span className="font-data font-bold text-white">{sel.odds?.toFixed(2)}</span>
                              <button
                                onClick={() => removeSelection(sel.match_id)}
                                className="text-[#A1A1AA] hover:text-[#FF2E2E]"
                              >
                                <X size={16} />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>

                    {/* Summary */}
                    <div className="bg-[#050505] border border-[#27272A] p-4">
                      <div className="flex justify-between mb-3">
                        <span className="text-sm text-[#A1A1AA]">Cuota Total</span>
                        <span className="font-data text-2xl font-bold text-[#CCFF00]">@{getTotalOdds()}</span>
                      </div>
                      
                      <div className="mb-3">
                        <label className="text-xs text-[#A1A1AA] uppercase mb-1 block">Nombre</label>
                        <input
                          type="text"
                          value={parlayName}
                          onChange={(e) => setParlayName(e.target.value)}
                          placeholder="Mi Combinada"
                          className="w-full bg-[#0A0A0A] border border-[#27272A] text-white px-3 h-10 text-sm focus:border-[#CCFF00] outline-none"
                        />
                      </div>

                      <div className="mb-4">
                        <label className="text-xs text-[#A1A1AA] uppercase mb-1 block">Apuesta ($)</label>
                        <input
                          type="number"
                          value={stake}
                          onChange={(e) => setStake(e.target.value)}
                          placeholder="10000"
                          className="w-full bg-[#0A0A0A] border border-[#27272A] text-white px-3 h-10 text-sm focus:border-[#CCFF00] outline-none font-data"
                        />
                      </div>

                      {stake && (
                        <div className="flex justify-between items-center py-3 border-t border-[#27272A]">
                          <span className="text-sm text-[#A1A1AA]">Ganancia Potencial</span>
                          <span className="font-data text-xl font-bold text-white">${getPotentialProfit()}</span>
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <button
                      onClick={createParlay}
                      className="w-full bg-[#CCFF00] text-black font-bold uppercase tracking-wider h-12 hover:bg-[#B3E600] transition-colors flex items-center justify-center gap-2"
                      data-testid="create-parlay-button"
                    >
                      <CheckCircle size={20} weight="bold" />
                      Guardar Combinada
                    </button>
                  </>
                ) : (
                  <div className="text-center py-8 text-[#A1A1AA]">
                    <ShoppingCart size={48} className="mx-auto mb-4 text-[#27272A]" />
                    <p>Tu boleto está vacío</p>
                    <p className="text-xs text-[#52525B] mt-1">Selecciona cuotas para crear tu combinada</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
