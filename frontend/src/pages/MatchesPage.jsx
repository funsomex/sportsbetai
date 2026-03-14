import React, { useState, useEffect } from "react";
import { Layout } from "../components/Layout";
import { api } from "../App";
import { toast } from "sonner";
import {
  SoccerBall,
  Basketball,
  TennisBall,
  Baseball,
  MagnetStraight,
  HandFist,
  GameController,
  Funnel,
  MagnifyingGlass,
  Lightning,
  Clock,
  CheckCircle
} from "@phosphor-icons/react";

const sportIcons = {
  football: SoccerBall,
  basketball: Basketball,
  tennis: TennisBall,
  baseball: Baseball,
  hockey: MagnetStraight,
  mma: HandFist,
  esports: GameController,
};

const sportNames = {
  football: "Fútbol",
  basketball: "Baloncesto",
  tennis: "Tenis",
  baseball: "Béisbol",
  hockey: "Hockey",
  mma: "MMA / UFC",
  esports: "Esports",
};

export default function MatchesPage() {
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSport, setSelectedSport] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    loadMatches();
  }, [selectedSport, selectedStatus]);

  const loadMatches = async () => {
    setLoading(true);
    try {
      let url = "/matches?limit=50";
      if (selectedSport) url += `&sport=${selectedSport}`;
      if (selectedStatus) url += `&status=${selectedStatus}`;
      const response = await api.get(url);
      setMatches(response.data.matches || []);
    } catch (error) {
      toast.error("Error cargando partidos");
    } finally {
      setLoading(false);
    }
  };

  const filteredMatches = matches.filter((match) => {
    if (!searchTerm) return true;
    const search = searchTerm.toLowerCase();
    return (
      match.home_team.toLowerCase().includes(search) ||
      match.away_team.toLowerCase().includes(search) ||
      match.league.toLowerCase().includes(search)
    );
  });

  const formatTime = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString("es-ES", { hour: "2-digit", minute: "2-digit" });
  };

  const formatDate = (isoString) => {
    const date = new Date(isoString);
    return date.toLocaleDateString("es-ES", { day: "numeric", month: "short" });
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
    const SportIcon = sportIcons[match.sport] || SoccerBall;
    const bestHome = getBestOdds(match.odds, "home");
    const bestDraw = getBestOdds(match.odds, "draw");
    const bestAway = getBestOdds(match.odds, "away");

    return (
      <div className="bg-[#0A0A0A] border border-[#27272A] hover:border-[#CCFF00]/30 transition-colors" data-testid="match-card">
        {/* Header */}
        <div className="px-4 py-3 border-b border-[#27272A] flex items-center justify-between bg-[#0F0F0F]">
          <div className="flex items-center gap-2">
            <SportIcon size={16} className="text-[#A1A1AA]" />
            <span className="badge-league">{match.league}</span>
          </div>
          <div className="flex items-center gap-2">
            {match.status === "live" && (
              <span className="badge-live live-indicator">EN VIVO</span>
            )}
            {match.status === "upcoming" && (
              <span className="flex items-center gap-1 text-xs text-[#A1A1AA]">
                <Clock size={12} />
                {formatDate(match.start_time)} {formatTime(match.start_time)}
              </span>
            )}
            {match.status === "finished" && (
              <span className="flex items-center gap-1 text-xs text-[#52525B]">
                <CheckCircle size={12} />
                Finalizado
              </span>
            )}
          </div>
        </div>

        {/* Teams & Score */}
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-white truncate">{match.home_team}</div>
              <div className="text-sm text-[#A1A1AA] truncate">{match.away_team}</div>
            </div>
            {(match.status === "live" || match.status === "finished") && (
              <div className="text-right ml-4">
                <div className="font-data text-xl font-bold text-white">{match.home_score ?? 0}</div>
                <div className="font-data text-xl font-bold text-[#A1A1AA]">{match.away_score ?? 0}</div>
              </div>
            )}
          </div>

          {/* Odds */}
          <div className="grid grid-cols-3 gap-2">
            <div className="bg-[#050505] border border-[#27272A] p-2 text-center hover:border-[#CCFF00]/50 cursor-pointer transition-colors">
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">1</div>
              <div className="font-data text-lg font-bold text-white">{bestHome.value}</div>
              <div className="text-[9px] text-[#52525B] truncate">{bestHome.bookmaker}</div>
            </div>
            <div className="bg-[#050505] border border-[#27272A] p-2 text-center hover:border-[#CCFF00]/50 cursor-pointer transition-colors">
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">X</div>
              <div className="font-data text-lg font-bold text-white">{bestDraw.value}</div>
              <div className="text-[9px] text-[#52525B] truncate">{bestDraw.bookmaker}</div>
            </div>
            <div className="bg-[#050505] border border-[#27272A] p-2 text-center hover:border-[#CCFF00]/50 cursor-pointer transition-colors">
              <div className="text-[10px] text-[#A1A1AA] uppercase mb-1">2</div>
              <div className="font-data text-lg font-bold text-white">{bestAway.value}</div>
              <div className="text-[9px] text-[#52525B] truncate">{bestAway.bookmaker}</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="matches-page">
        {/* Header */}
        <div>
          <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight text-white">
            Partidos
          </h1>
          <p className="text-[#A1A1AA] text-sm mt-1">
            Explora partidos y cuotas en tiempo real
          </p>
        </div>

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <MagnifyingGlass size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#52525B]" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Buscar equipo o liga..."
              className="w-full bg-[#050505] border border-[#27272A] text-white pl-10 pr-4 h-10 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors text-sm"
              data-testid="search-input"
            />
          </div>

          {/* Sport Filter */}
          <select
            value={selectedSport}
            onChange={(e) => setSelectedSport(e.target.value)}
            className="bg-[#050505] border border-[#27272A] text-white px-4 h-10 focus:border-[#CCFF00] outline-none text-sm min-w-[150px]"
            data-testid="sport-filter"
          >
            <option value="">Todos los deportes</option>
            {Object.entries(sportNames).map(([key, name]) => (
              <option key={key} value={key}>{name}</option>
            ))}
          </select>

          {/* Status Filter */}
          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="bg-[#050505] border border-[#27272A] text-white px-4 h-10 focus:border-[#CCFF00] outline-none text-sm min-w-[150px]"
            data-testid="status-filter"
          >
            <option value="">Todos los estados</option>
            <option value="live">En vivo</option>
            <option value="upcoming">Próximos</option>
            <option value="finished">Finalizados</option>
          </select>
        </div>

        {/* Sport Pills */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          <button
            onClick={() => setSelectedSport("")}
            className={`flex items-center gap-2 px-4 py-2 text-sm font-medium whitespace-nowrap transition-colors ${
              selectedSport === ""
                ? "bg-[#CCFF00] text-black"
                : "bg-[#1E1E1E] text-[#A1A1AA] hover:text-white border border-[#27272A]"
            }`}
          >
            Todos
          </button>
          {Object.entries(sportNames).map(([key, name]) => {
            const Icon = sportIcons[key];
            return (
              <button
                key={key}
                onClick={() => setSelectedSport(key)}
                className={`flex items-center gap-2 px-4 py-2 text-sm font-medium whitespace-nowrap transition-colors ${
                  selectedSport === key
                    ? "bg-[#CCFF00] text-black"
                    : "bg-[#1E1E1E] text-[#A1A1AA] hover:text-white border border-[#27272A]"
                }`}
              >
                <Icon size={16} />
                {name}
              </button>
            );
          })}
        </div>

        {/* Matches Grid */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-[#CCFF00] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filteredMatches.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredMatches.map((match) => (
              <MatchCard key={match.id} match={match} />
            ))}
          </div>
        ) : (
          <div className="bg-[#0A0A0A] border border-[#27272A] p-12 text-center">
            <SoccerBall size={48} className="mx-auto text-[#27272A] mb-4" />
            <p className="text-[#A1A1AA]">No se encontraron partidos</p>
          </div>
        )}
      </div>
    </Layout>
  );
}
