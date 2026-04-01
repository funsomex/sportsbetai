import React, { useState, useEffect } from "react";
import { Layout } from "../components/Layout";
import { api } from "../App";
import { toast } from "sonner";
import {
  TrendUp,
  TrendDown,
  SoccerBall,
  Lightning,
  ChartLine,
  Target,
  ArrowRight,
  CaretUp,
  CaretDown
} from "@phosphor-icons/react";
import { Link } from "react-router-dom";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area
} from "recharts";

// Mock chart data
const performanceData = [
  { name: "Lun", value: 120 },
  { name: "Mar", value: 180 },
  { name: "Mie", value: 150 },
  { name: "Jue", value: 220 },
  { name: "Vie", value: 280 },
  { name: "Sab", value: 350 },
  { name: "Dom", value: 410 },
];

export default function DashboardPage() {
  const [stats, setStats] = useState({
    total_predictions: 0,
    won: 0,
    lost: 0,
    pending: 0,
    win_rate: 0,
    total_stake: 0,
    total_profit: 0,
    roi: 0
  });
  const [valueBets, setValueBets] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dataSource, setDataSource] = useState("real");

  useEffect(() => {
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statsRes, valueBetsRes, matchesRes] = await Promise.all([
        api.get("/stats"),
        api.get("/value-bets/top?limit=5"),
        api.get("/matches?limit=5")  // Changed: Get upcoming matches instead of live
      ]);
      setStats(statsRes.data);
      setValueBets(valueBetsRes.data.value_bets || []);
      setMatches(matchesRes.data.matches || []);
      setDataSource(matchesRes.data.source || "real");
    } catch (error) {
      console.error("Error loading dashboard:", error);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, icon: Icon, trend, trendValue, color = "default" }) => (
    <div className="bg-[#0A0A0A] border border-[#27272A] p-4 group hover:border-[#CCFF00]/30 transition-colors">
      <div className="flex items-start justify-between mb-3">
        <span className="text-[10px] uppercase tracking-wider text-[#A1A1AA]">{title}</span>
        <Icon 
          size={18} 
          className={color === "profit" ? "text-[#CCFF00]" : color === "loss" ? "text-[#FF2E2E]" : "text-[#A1A1AA]"} 
        />
      </div>
      <div className="flex items-end gap-2">
        <span className={`font-data text-3xl font-bold tracking-tighter ${
          color === "profit" ? "text-[#CCFF00]" : color === "loss" ? "text-[#FF2E2E]" : "text-white"
        }`}>
          {value}
        </span>
        {trend && (
          <span className={`flex items-center text-xs font-medium ${
            trend === "up" ? "text-[#CCFF00]" : "text-[#FF2E2E]"
          }`}>
            {trend === "up" ? <CaretUp size={14} /> : <CaretDown size={14} />}
            {trendValue}
          </span>
        )}
      </div>
    </div>
  );

  const ValueBetCard = ({ bet }) => (
    <div className="bg-[#0A0A0A] border border-[#27272A] p-4 hover:border-[#CCFF00]/50 transition-colors group cursor-pointer">
      <div className="flex items-center justify-between mb-2">
        <span className="badge-league">{bet.match.league}</span>
        <span className="badge-value">{bet.value_percentage}% VALUE</span>
      </div>
      <div className="mb-3">
        <div className="text-sm font-medium text-white">
          {bet.match.home_team} vs {bet.match.away_team}
        </div>
      </div>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-xs text-[#A1A1AA] mb-1">Selección</div>
          <div className="text-sm font-medium text-[#CCFF00]">{bet.selection}</div>
        </div>
        <div className="text-right">
          <div className="text-xs text-[#A1A1AA] mb-1">Cuota</div>
          <div className="font-data text-xl font-bold text-white">{bet.odds}</div>
        </div>
      </div>
      <div className="mt-3 pt-3 border-t border-[#27272A] flex justify-between text-xs">
        <span className="text-[#A1A1AA]">Casa: {bet.bookmaker}</span>
        <span className="text-[#00E5FF]">{bet.confidence}% confianza</span>
      </div>
    </div>
  );

  const LiveMatchCard = ({ match }) => (
    <div className="bg-[#0A0A0A] border border-[#27272A] p-4 hover:border-[#FF2E2E]/30 transition-colors">
      <div className="flex items-center justify-between mb-3">
        <span className="badge-league">{match.league}</span>
        <span className="badge-live live-indicator">EN VIVO</span>
      </div>
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <div className="text-sm text-white mb-1">{match.home_team}</div>
          <div className="text-sm text-[#A1A1AA]">{match.away_team}</div>
        </div>
        <div className="text-right">
          <div className="font-data text-2xl font-bold text-white">
            {match.home_score ?? 0}
          </div>
          <div className="font-data text-2xl font-bold text-[#A1A1AA]">
            {match.away_score ?? 0}
          </div>
        </div>
      </div>
    </div>
  );

  const UpcomingMatchCard = ({ match }) => {
    // Format date
    const formatDate = (dateStr) => {
      if (!dateStr) return "";
      const date = new Date(dateStr);
      const day = date.getDate();
      const month = date.toLocaleString('es', { month: 'short' });
      const time = date.toLocaleTimeString('es', { hour: '2-digit', minute: '2-digit' });
      return { day, month, time };
    };
    
    const dateInfo = formatDate(match.start_time);
    
    // Get best odds
    const getBestOdds = () => {
      if (!match.odds) return { home: "-", draw: "-", away: "-" };
      let bestHome = 0, bestDraw = 0, bestAway = 0;
      Object.values(match.odds).forEach(odds => {
        if (odds.home && odds.home > bestHome) bestHome = odds.home;
        if (odds.draw && odds.draw > bestDraw) bestDraw = odds.draw;
        if (odds.away && odds.away > bestAway) bestAway = odds.away;
      });
      return { 
        home: bestHome > 0 ? bestHome.toFixed(2) : "-", 
        draw: bestDraw > 0 ? bestDraw.toFixed(2) : "-", 
        away: bestAway > 0 ? bestAway.toFixed(2) : "-" 
      };
    };
    
    const bestOdds = getBestOdds();
    
    return (
      <div className="p-4 hover:bg-[#0F0F0F] transition-colors">
        <div className="flex items-center justify-between mb-2">
          <span className="badge-league">{match.league}</span>
          {match.is_real_data && (
            <span className="text-[8px] uppercase tracking-wider text-[#00E5FF] bg-[#00E5FF]/10 px-2 py-0.5">
              Datos reales
            </span>
          )}
        </div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex-1">
            <div className="text-sm text-white mb-1">{match.home_team}</div>
            <div className="text-sm text-[#A1A1AA]">{match.away_team}</div>
          </div>
          <div className="text-right text-xs text-[#A1A1AA]">
            <div className="text-[#CCFF00] font-medium">{dateInfo.day} {dateInfo.month}</div>
            <div>{dateInfo.time}</div>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="bg-[#1A1A1A] py-1 px-2">
            <div className="text-[10px] text-[#A1A1AA]">1</div>
            <div className="text-sm font-bold text-white">{bestOdds.home}</div>
          </div>
          <div className="bg-[#1A1A1A] py-1 px-2">
            <div className="text-[10px] text-[#A1A1AA]">X</div>
            <div className="text-sm font-bold text-white">{bestOdds.draw}</div>
          </div>
          <div className="bg-[#1A1A1A] py-1 px-2">
            <div className="text-[10px] text-[#A1A1AA]">2</div>
            <div className="text-sm font-bold text-white">{bestOdds.away}</div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-[#CCFF00] border-t-transparent rounded-full animate-spin" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6" data-testid="dashboard-page">
        {/* Demo Mode Banner */}
        {dataSource === "demo" && (
          <div className="bg-[#FF9500]/10 border border-[#FF9500]/30 p-4 flex items-center gap-3">
            <div className="w-2 h-2 bg-[#FF9500] rounded-full animate-pulse" />
            <div>
              <span className="text-[#FF9500] font-medium text-sm">Modo Demostración</span>
              <span className="text-[#A1A1AA] text-sm ml-2">
                La cuota de API se reinicia pronto. Los datos mostrados son de ejemplo.
              </span>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight text-white">
              Dashboard
            </h1>
            <p className="text-[#A1A1AA] text-sm mt-1">
              Resumen de tu actividad y oportunidades
            </p>
          </div>
          <Link
            to="/value-bets"
            className="inline-flex items-center gap-2 bg-[#CCFF00] text-black font-bold uppercase tracking-wider text-sm h-10 px-6 hover:bg-[#B3E600] transition-colors"
            data-testid="view-value-bets-button"
          >
            <Lightning size={18} weight="fill" />
            Ver Value Bets
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            title="Predicciones"
            value={stats.total_predictions}
            icon={Target}
          />
          <StatCard
            title="Win Rate"
            value={`${stats.win_rate}%`}
            icon={ChartLine}
            trend={stats.win_rate > 50 ? "up" : "down"}
            trendValue={`${Math.abs(stats.win_rate - 50).toFixed(1)}%`}
            color={stats.win_rate > 50 ? "profit" : "loss"}
          />
          <StatCard
            title="ROI"
            value={`${stats.roi}%`}
            icon={stats.roi >= 0 ? TrendUp : TrendDown}
            color={stats.roi >= 0 ? "profit" : "loss"}
          />
          <StatCard
            title="Profit"
            value={`$${stats.total_profit.toFixed(0)}`}
            icon={stats.total_profit >= 0 ? TrendUp : TrendDown}
            color={stats.total_profit >= 0 ? "profit" : "loss"}
          />
        </div>

        {/* Main Content Grid */}
        <div className="grid lg:grid-cols-3 gap-6">
          {/* Performance Chart */}
          <div className="lg:col-span-2 bg-[#0A0A0A] border border-[#27272A]">
            <div className="px-4 py-3 border-b border-[#27272A] flex justify-between items-center">
              <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white">
                Rendimiento Semanal
              </h2>
              <span className="text-xs text-[#CCFF00]">+15.3%</span>
            </div>
            <div className="p-4 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={performanceData}>
                  <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#CCFF00" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#CCFF00" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis 
                    dataKey="name" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#A1A1AA', fontSize: 10 }}
                  />
                  <YAxis 
                    hide 
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0A0A0A',
                      border: '1px solid #27272A',
                      borderRadius: 0,
                      color: '#EDEDED'
                    }}
                    labelStyle={{ color: '#A1A1AA' }}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke="#CCFF00"
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorValue)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Upcoming Matches */}
          <div className="bg-[#0A0A0A] border border-[#27272A]">
            <div className="px-4 py-3 border-b border-[#27272A] flex justify-between items-center">
              <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white">
                Próximos Partidos
              </h2>
              <Link to="/matches" className="text-xs text-[#A1A1AA] hover:text-[#CCFF00] flex items-center gap-1">
                Ver todos <ArrowRight size={12} />
              </Link>
            </div>
            <div className="divide-y divide-[#27272A]">
              {matches.length > 0 ? (
                matches.slice(0, 3).map((match) => (
                  <UpcomingMatchCard key={match.id} match={match} />
                ))
              ) : (
                <div className="p-8 text-center text-[#A1A1AA] text-sm">
                  No hay partidos próximos disponibles
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Value Bets Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading text-xl font-bold uppercase tracking-wider text-white">
              Top Value Bets
            </h2>
            <Link
              to="/value-bets"
              className="text-xs text-[#A1A1AA] hover:text-[#CCFF00] flex items-center gap-1"
            >
              Ver todos <ArrowRight size={12} />
            </Link>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {valueBets.length > 0 ? (
              valueBets.map((bet) => (
                <ValueBetCard key={bet.id} bet={bet} />
              ))
            ) : (
              <div className="col-span-full bg-[#0A0A0A] border border-[#27272A] p-8 text-center text-[#A1A1AA]">
                No hay value bets disponibles en este momento
              </div>
            )}
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-[#0A0A0A] border border-[#27272A] p-4">
            <div className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-2">Ganadas</div>
            <div className="flex items-center gap-4">
              <span className="font-data text-4xl font-bold text-[#CCFF00]">{stats.won}</span>
              <div className="flex-1 h-2 bg-[#1E1E1E] rounded-full overflow-hidden">
                <div 
                  className="h-full bg-[#CCFF00]" 
                  style={{ width: `${(stats.won / Math.max(stats.total_predictions, 1)) * 100}%` }}
                />
              </div>
            </div>
          </div>
          <div className="bg-[#0A0A0A] border border-[#27272A] p-4">
            <div className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-2">Perdidas</div>
            <div className="flex items-center gap-4">
              <span className="font-data text-4xl font-bold text-[#FF2E2E]">{stats.lost}</span>
              <div className="flex-1 h-2 bg-[#1E1E1E] rounded-full overflow-hidden">
                <div 
                  className="h-full bg-[#FF2E2E]" 
                  style={{ width: `${(stats.lost / Math.max(stats.total_predictions, 1)) * 100}%` }}
                />
              </div>
            </div>
          </div>
          <div className="bg-[#0A0A0A] border border-[#27272A] p-4">
            <div className="text-xs text-[#A1A1AA] uppercase tracking-wider mb-2">Pendientes</div>
            <div className="flex items-center gap-4">
              <span className="font-data text-4xl font-bold text-[#00E5FF]">{stats.pending}</span>
              <div className="flex-1 h-2 bg-[#1E1E1E] rounded-full overflow-hidden">
                <div 
                  className="h-full bg-[#00E5FF]" 
                  style={{ width: `${(stats.pending / Math.max(stats.total_predictions, 1)) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
