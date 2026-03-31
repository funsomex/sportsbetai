import React, { useState, useEffect } from "react";
import { Layout } from "../components/Layout";
import { api } from "../App";
import { toast } from "sonner";
import {
  Scales,
  ArrowsClockwise,
  CaretUp,
  CaretDown,
  Trophy
} from "@phosphor-icons/react";

const BOOKMAKERS = ["BetPlay", "Bet365", "1xBet", "Pinnacle", "Betfair"];

export default function OddsComparisonPage() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMatch, setSelectedMatch] = useState(null);

  useEffect(() => {
    loadMatches();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadMatches = async () => {
    setLoading(true);
    try {
      const response = await api.get("/matches?status=upcoming&limit=20");
      setMatches(response.data.matches || []);
      if (response.data.matches?.length > 0) {
        setSelectedMatch(response.data.matches[0]);
      }
    } catch (error) {
      toast.error("Error cargando partidos");
    } finally {
      setLoading(false);
    }
  };

  const getBestOdds = (market) => {
    if (!selectedMatch?.odds) return { bookmaker: "", value: 0 };
    let best = { bookmaker: "", value: 0 };
    for (const [bookmaker, markets] of Object.entries(selectedMatch.odds)) {
      if (markets[market] > best.value) {
        best = { bookmaker, value: markets[market] };
      }
    }
    return best;
  };

  const OddsRow = ({ bookmaker, odds, bestOdds }) => (
    <tr className="border-b border-[#27272A]/50 hover:bg-[#0F0F0F]">
      <td className="py-3 px-4">
        <span className="text-sm text-white">{bookmaker}</span>
      </td>
      <td className="py-3 px-4 text-center">
        <span className={`font-data font-bold ${bestOdds.home === bookmaker ? "text-[#CCFF00]" : "text-white"}`}>
          {odds.home}
          {bestOdds.home === bookmaker && <Trophy size={12} className="inline ml-1 text-[#CCFF00]" />}
        </span>
      </td>
      <td className="py-3 px-4 text-center">
        <span className={`font-data font-bold ${bestOdds.draw === bookmaker ? "text-[#CCFF00]" : "text-white"}`}>
          {odds.draw}
          {bestOdds.draw === bookmaker && <Trophy size={12} className="inline ml-1 text-[#CCFF00]" />}
        </span>
      </td>
      <td className="py-3 px-4 text-center">
        <span className={`font-data font-bold ${bestOdds.away === bookmaker ? "text-[#CCFF00]" : "text-white"}`}>
          {odds.away}
          {bestOdds.away === bookmaker && <Trophy size={12} className="inline ml-1 text-[#CCFF00]" />}
        </span>
      </td>
      <td className="py-3 px-4 text-center">
        <span className={`font-data font-bold ${bestOdds.over === bookmaker ? "text-[#00E5FF]" : "text-white"}`}>
          {odds["over_2.5"]}
        </span>
      </td>
      <td className="py-3 px-4 text-center">
        <span className={`font-data font-bold ${bestOdds.under === bookmaker ? "text-[#00E5FF]" : "text-white"}`}>
          {odds["under_2.5"]}
        </span>
      </td>
    </tr>
  );

  const getBestByMarket = () => {
    if (!selectedMatch?.odds) return {};
    const markets = ["home", "draw", "away", "over_2.5", "under_2.5"];
    const result = {};
    markets.forEach(market => {
      let best = { bookmaker: "", value: 0 };
      for (const [bookmaker, odds] of Object.entries(selectedMatch.odds)) {
        if (odds[market] > best.value) {
          best = { bookmaker, value: odds[market] };
        }
      }
      result[market.replace("_2.5", "")] = best.bookmaker;
    });
    return result;
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="odds-comparison-page">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight text-white flex items-center gap-3">
              <Scales size={36} className="text-[#00E5FF]" />
              Comparador
            </h1>
            <p className="text-[#A1A1AA] text-sm mt-1">
              Compara cuotas entre casas de apuestas
            </p>
          </div>
          <button
            onClick={loadMatches}
            disabled={loading}
            className="inline-flex items-center gap-2 bg-[#1E1E1E] text-white font-bold uppercase tracking-wider text-sm h-10 px-6 hover:bg-[#2A2A2A] border border-[#27272A] transition-colors disabled:opacity-50"
            data-testid="refresh-button"
          >
            <ArrowsClockwise size={18} className={loading ? "animate-spin" : ""} />
            Actualizar
          </button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-[#CCFF00] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="grid lg:grid-cols-4 gap-6">
            {/* Match List */}
            <div className="lg:col-span-1 space-y-2">
              <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-[#A1A1AA] mb-3">
                Partidos
              </h2>
              <div className="space-y-2 max-h-[600px] overflow-y-auto">
                {matches.map((match) => (
                  <button
                    key={match.id}
                    onClick={() => setSelectedMatch(match)}
                    className={`w-full text-left p-3 border transition-colors ${
                      selectedMatch?.id === match.id
                        ? "bg-[#CCFF00]/5 border-[#CCFF00]"
                        : "bg-[#0A0A0A] border-[#27272A] hover:border-[#CCFF00]/30"
                    }`}
                    data-testid="match-selector"
                  >
                    <div className="text-[10px] text-[#52525B] uppercase mb-1">{match.league}</div>
                    <div className="text-sm text-white">{match.home_team}</div>
                    <div className="text-sm text-[#A1A1AA]">{match.away_team}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Odds Table */}
            <div className="lg:col-span-3">
              {selectedMatch ? (
                <div className="bg-[#0A0A0A] border border-[#27272A]">
                  {/* Match Header */}
                  <div className="px-4 py-4 border-b border-[#27272A] bg-[#0F0F0F]">
                    <div className="text-[10px] text-[#52525B] uppercase mb-1">{selectedMatch.league}</div>
                    <div className="text-xl font-bold text-white">
                      {selectedMatch.home_team} vs {selectedMatch.away_team}
                    </div>
                    <div className="text-xs text-[#A1A1AA] mt-1">
                      {new Date(selectedMatch.start_time).toLocaleDateString("es-ES", {
                        weekday: "long",
                        day: "numeric",
                        month: "long",
                        hour: "2-digit",
                        minute: "2-digit"
                      })}
                    </div>
                  </div>

                  {/* Best Odds Summary */}
                  <div className="px-4 py-3 border-b border-[#27272A] grid grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">Mejor 1</div>
                      <div className="font-data text-2xl font-bold text-[#CCFF00]">{getBestOdds("home").value}</div>
                      <div className="text-xs text-[#52525B]">{getBestOdds("home").bookmaker}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">Mejor X</div>
                      <div className="font-data text-2xl font-bold text-[#CCFF00]">{getBestOdds("draw").value}</div>
                      <div className="text-xs text-[#52525B]">{getBestOdds("draw").bookmaker}</div>
                    </div>
                    <div className="text-center">
                      <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">Mejor 2</div>
                      <div className="font-data text-2xl font-bold text-[#CCFF00]">{getBestOdds("away").value}</div>
                      <div className="text-xs text-[#52525B]">{getBestOdds("away").bookmaker}</div>
                    </div>
                  </div>

                  {/* Odds Table */}
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-[#27272A]">
                          <th className="text-left text-[10px] uppercase tracking-wider text-[#A1A1AA] font-medium py-3 px-4">Casa</th>
                          <th className="text-center text-[10px] uppercase tracking-wider text-[#A1A1AA] font-medium py-3 px-4">1</th>
                          <th className="text-center text-[10px] uppercase tracking-wider text-[#A1A1AA] font-medium py-3 px-4">X</th>
                          <th className="text-center text-[10px] uppercase tracking-wider text-[#A1A1AA] font-medium py-3 px-4">2</th>
                          <th className="text-center text-[10px] uppercase tracking-wider text-[#A1A1AA] font-medium py-3 px-4">Over 2.5</th>
                          <th className="text-center text-[10px] uppercase tracking-wider text-[#A1A1AA] font-medium py-3 px-4">Under 2.5</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedMatch.odds && Object.entries(selectedMatch.odds).map(([bookmaker, odds]) => (
                          <OddsRow 
                            key={bookmaker} 
                            bookmaker={bookmaker} 
                            odds={odds} 
                            bestOdds={getBestByMarket()}
                          />
                        ))}
                      </tbody>
                    </table>
                  </div>

                  {/* Stats */}
                  {selectedMatch.stats && (
                    <div className="px-4 py-4 border-t border-[#27272A]">
                      <h3 className="font-heading text-sm font-bold uppercase tracking-wider text-white mb-4">
                        Estadísticas
                      </h3>
                      <div className="grid grid-cols-2 gap-6">
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-[#A1A1AA]">Posesión</span>
                            <span className="font-data text-sm text-white">{selectedMatch.stats.home.possession}%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-[#A1A1AA]">xG</span>
                            <span className="font-data text-sm text-white">{selectedMatch.stats.home.xG}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-[#A1A1AA]">Forma</span>
                            <div className="flex gap-1">
                              {selectedMatch.stats.home.form.map((f, i) => (
                                <span 
                                  key={i}
                                  className={`w-5 h-5 flex items-center justify-center text-[10px] font-bold ${
                                    f === "W" ? "bg-[#CCFF00] text-black" : 
                                    f === "D" ? "bg-[#A1A1AA] text-black" : 
                                    "bg-[#FF2E2E] text-white"
                                  }`}
                                >
                                  {f}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-[#A1A1AA]">Posesión</span>
                            <span className="font-data text-sm text-white">{selectedMatch.stats.away.possession}%</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-[#A1A1AA]">xG</span>
                            <span className="font-data text-sm text-white">{selectedMatch.stats.away.xG}</span>
                          </div>
                          <div className="flex justify-between items-center">
                            <span className="text-xs text-[#A1A1AA]">Forma</span>
                            <div className="flex gap-1">
                              {selectedMatch.stats.away.form.map((f, i) => (
                                <span 
                                  key={i}
                                  className={`w-5 h-5 flex items-center justify-center text-[10px] font-bold ${
                                    f === "W" ? "bg-[#CCFF00] text-black" : 
                                    f === "D" ? "bg-[#A1A1AA] text-black" : 
                                    "bg-[#FF2E2E] text-white"
                                  }`}
                                >
                                  {f}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-[#0A0A0A] border border-[#27272A] p-12 text-center text-[#A1A1AA]">
                  Selecciona un partido para ver la comparación de cuotas
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}
