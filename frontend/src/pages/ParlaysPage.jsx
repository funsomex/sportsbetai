import React, { useState, useEffect } from "react";
import { Layout } from "../components/Layout";
import { api } from "../App";
import { toast } from "sonner";
import {
  Plus,
  Trash,
  ShoppingCart,
  X,
  Calculator,
  TelegramLogo,
  CheckCircle
} from "@phosphor-icons/react";

export default function ParlaysPage() {
  const [matches, setMatches] = useState([]);
  const [parlays, setParlays] = useState([]);
  const [selections, setSelections] = useState([]);
  const [parlayName, setParlayName] = useState("");
  const [stake, setStake] = useState("");
  const [loading, setLoading] = useState(true);
  const [showCart, setShowCart] = useState(false);

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadData = async () => {
    try {
      const [matchesRes, parlaysRes] = await Promise.all([
        api.get("/matches?status=upcoming&limit=30"),
        api.get("/parlays")
      ]);
      setMatches(matchesRes.data.matches || []);
      setParlays(parlaysRes.data.parlays || []);
    } catch (error) {
      toast.error("Error cargando datos");
    } finally {
      setLoading(false);
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
    let best = { bookmaker: "", value: 0 };
    for (const [bookmaker, markets] of Object.entries(odds)) {
      if (markets[market] > best.value) {
        best = { bookmaker, value: markets[market] };
      }
    }
    return best;
  };

  const MatchCard = ({ match }) => {
    const bestHome = getBestOdds(match.odds, "home");
    const bestDraw = getBestOdds(match.odds, "draw");
    const bestAway = getBestOdds(match.odds, "away");
    const isSelected = selections.find(s => s.match_id === match.id);

    return (
      <div className={`bg-[#0A0A0A] border ${isSelected ? "border-[#CCFF00]" : "border-[#27272A]"} transition-colors`}>
        <div className="px-4 py-2 border-b border-[#27272A] bg-[#0F0F0F]">
          <span className="badge-league">{match.league}</span>
        </div>
        <div className="p-4">
          <div className="text-sm font-medium text-white mb-1">{match.home_team}</div>
          <div className="text-sm text-[#A1A1AA] mb-3">{match.away_team}</div>
          
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => addSelection(match, "home", match.home_team, bestHome.value)}
              className={`p-2 text-center border transition-colors ${
                isSelected?.market === "home"
                  ? "bg-[#CCFF00] border-[#CCFF00] text-black"
                  : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
              }`}
              data-testid="select-home"
            >
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">1</div>
              <div className="font-data font-bold">{bestHome.value}</div>
            </button>
            <button
              onClick={() => addSelection(match, "draw", "Empate", bestDraw.value)}
              className={`p-2 text-center border transition-colors ${
                isSelected?.market === "draw"
                  ? "bg-[#CCFF00] border-[#CCFF00] text-black"
                  : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
              }`}
              data-testid="select-draw"
            >
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">X</div>
              <div className="font-data font-bold">{bestDraw.value}</div>
            </button>
            <button
              onClick={() => addSelection(match, "away", match.away_team, bestAway.value)}
              className={`p-2 text-center border transition-colors ${
                isSelected?.market === "away"
                  ? "bg-[#CCFF00] border-[#CCFF00] text-black"
                  : "bg-[#050505] border-[#27272A] hover:border-[#CCFF00]/50"
              }`}
              data-testid="select-away"
            >
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">2</div>
              <div className="font-data font-bold">{bestAway.value}</div>
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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight text-white">
              Combinadas
            </h1>
            <p className="text-[#A1A1AA] text-sm mt-1">
              Crea combinadas de hasta 6 selecciones
            </p>
          </div>
          
          <button
            onClick={() => setShowCart(true)}
            className="relative bg-[#CCFF00] text-black p-2.5 hover:bg-[#B3E600] transition-colors"
            data-testid="cart-button"
          >
            <ShoppingCart size={24} weight="bold" />
            {selections.length > 0 && (
              <span className="absolute -top-2 -right-2 w-5 h-5 bg-[#FF2E2E] text-white text-xs font-bold flex items-center justify-center">
                {selections.length}
              </span>
            )}
          </button>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Matches Section */}
          <div className="lg:col-span-2 space-y-4">
            <h2 className="font-heading text-lg font-bold uppercase tracking-wider text-white">
              Próximos Partidos
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

          {/* Saved Parlays */}
          <div className="space-y-4">
            <h2 className="font-heading text-lg font-bold uppercase tracking-wider text-white">
              Mis Combinadas
            </h2>
            
            {parlays.length > 0 ? (
              <div className="space-y-3">
                {parlays.map((parlay) => (
                  <div key={parlay.id} className="bg-[#0A0A0A] border border-[#27272A] p-4">
                    <div className="flex items-center justify-between mb-3">
                      <span className="font-medium text-white">{parlay.name}</span>
                      <button
                        onClick={() => deleteParlay(parlay.id)}
                        className="text-[#A1A1AA] hover:text-[#FF2E2E] transition-colors"
                        data-testid="delete-parlay"
                      >
                        <Trash size={16} />
                      </button>
                    </div>
                    <div className="space-y-2 mb-3">
                      {parlay.selections.map((sel, idx) => (
                        <div key={idx} className="text-xs text-[#A1A1AA] flex justify-between">
                          <span>{sel.selection}</span>
                          <span className="font-data">{sel.odds}</span>
                        </div>
                      ))}
                    </div>
                    <div className="pt-3 border-t border-[#27272A] flex justify-between items-center">
                      <span className="text-xs text-[#A1A1AA]">{parlay.selections.length} sel.</span>
                      <span className="font-data text-lg font-bold text-[#CCFF00]">@{parlay.total_odds}</span>
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

        {/* Cart Drawer */}
        {showCart && (
          <div className="fixed inset-0 z-50 flex">
            <div className="absolute inset-0 bg-black/50" onClick={() => setShowCart(false)} />
            <div className="absolute right-0 top-0 bottom-0 w-full max-w-md bg-[#0A0A0A] border-l border-[#27272A] overflow-y-auto">
              <div className="sticky top-0 bg-[#0A0A0A] px-4 py-4 border-b border-[#27272A] flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShoppingCart size={20} className="text-[#CCFF00]" />
                  <span className="font-heading font-bold uppercase">Boleto</span>
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
                              <span className="font-data font-bold text-white">{sel.odds}</span>
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
                          placeholder="100"
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
