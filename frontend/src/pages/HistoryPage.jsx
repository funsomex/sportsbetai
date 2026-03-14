import React, { useState, useEffect } from "react";
import { Layout } from "../components/Layout";
import { api } from "../App";
import { toast } from "sonner";
import {
  ClockCounterClockwise,
  CheckCircle,
  XCircle,
  Clock,
  TrendUp,
  TrendDown,
  Funnel
} from "@phosphor-icons/react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer
} from "recharts";

export default function HistoryPage() {
  const [predictions, setPredictions] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [predsRes, statsRes] = await Promise.all([
        api.get("/predictions"),
        api.get("/stats")
      ]);
      setPredictions(predsRes.data.predictions || []);
      setStats(statsRes.data);
    } catch (error) {
      toast.error("Error cargando historial");
    } finally {
      setLoading(false);
    }
  };

  const filteredPredictions = predictions.filter(p => {
    if (filter === "all") return true;
    return p.result === filter;
  });

  // Generate mock chart data based on predictions count
  const chartData = [
    { name: "Sem 1", profit: -50 },
    { name: "Sem 2", profit: 120 },
    { name: "Sem 3", profit: 80 },
    { name: "Sem 4", profit: 250 },
    { name: "Sem 5", profit: 180 },
    { name: "Sem 6", profit: stats?.total_profit || 350 },
  ];

  const StatBox = ({ label, value, icon: Icon, color = "default" }) => (
    <div className="bg-[#0A0A0A] border border-[#27272A] p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] uppercase tracking-wider text-[#A1A1AA]">{label}</span>
        <Icon 
          size={18} 
          className={color === "profit" ? "text-[#CCFF00]" : color === "loss" ? "text-[#FF2E2E]" : "text-[#A1A1AA]"} 
        />
      </div>
      <div className={`font-data text-2xl font-bold ${
        color === "profit" ? "text-[#CCFF00]" : color === "loss" ? "text-[#FF2E2E]" : "text-white"
      }`}>
        {value}
      </div>
    </div>
  );

  return (
    <Layout>
      <div className="space-y-6" data-testid="history-page">
        {/* Header */}
        <div>
          <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight text-white flex items-center gap-3">
            <ClockCounterClockwise size={36} className="text-[#00E5FF]" />
            Historial
          </h1>
          <p className="text-[#A1A1AA] text-sm mt-1">
            Revisa tu rendimiento y predicciones pasadas
          </p>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="w-8 h-8 border-2 border-[#CCFF00] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <>
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatBox
                label="Total Predicciones"
                value={stats?.total_predictions || 0}
                icon={ClockCounterClockwise}
              />
              <StatBox
                label="Win Rate"
                value={`${stats?.win_rate || 0}%`}
                icon={stats?.win_rate >= 50 ? TrendUp : TrendDown}
                color={stats?.win_rate >= 50 ? "profit" : "loss"}
              />
              <StatBox
                label="ROI"
                value={`${stats?.roi || 0}%`}
                icon={stats?.roi >= 0 ? TrendUp : TrendDown}
                color={stats?.roi >= 0 ? "profit" : "loss"}
              />
              <StatBox
                label="Profit Total"
                value={`$${stats?.total_profit || 0}`}
                icon={stats?.total_profit >= 0 ? TrendUp : TrendDown}
                color={stats?.total_profit >= 0 ? "profit" : "loss"}
              />
            </div>

            {/* Chart */}
            <div className="bg-[#0A0A0A] border border-[#27272A]">
              <div className="px-4 py-3 border-b border-[#27272A]">
                <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white">
                  Evolución del Profit
                </h2>
              </div>
              <div className="p-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData}>
                    <defs>
                      <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
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
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: '#A1A1AA', fontSize: 10 }}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#0A0A0A',
                        border: '1px solid #27272A',
                        borderRadius: 0,
                        color: '#EDEDED'
                      }}
                      formatter={(value) => [`$${value}`, 'Profit']}
                    />
                    <Area
                      type="monotone"
                      dataKey="profit"
                      stroke="#CCFF00"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorProfit)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Predictions List */}
            <div className="bg-[#0A0A0A] border border-[#27272A]">
              <div className="px-4 py-3 border-b border-[#27272A] flex items-center justify-between">
                <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white">
                  Predicciones
                </h2>
                <div className="flex items-center gap-2">
                  <Funnel size={14} className="text-[#A1A1AA]" />
                  <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="bg-[#050505] border border-[#27272A] text-white px-3 py-1 text-xs focus:border-[#CCFF00] outline-none"
                    data-testid="filter-select"
                  >
                    <option value="all">Todos</option>
                    <option value="won">Ganados</option>
                    <option value="lost">Perdidos</option>
                    <option value="pending">Pendientes</option>
                  </select>
                </div>
              </div>

              {filteredPredictions.length > 0 ? (
                <div className="divide-y divide-[#27272A]/50">
                  {filteredPredictions.map((pred) => (
                    <div key={pred.id} className="px-4 py-3 flex items-center justify-between hover:bg-[#0F0F0F]">
                      <div className="flex items-center gap-3">
                        {pred.result === "won" && <CheckCircle size={20} className="text-[#CCFF00]" />}
                        {pred.result === "lost" && <XCircle size={20} className="text-[#FF2E2E]" />}
                        {pred.result === "pending" && <Clock size={20} className="text-[#A1A1AA]" />}
                        <div>
                          <div className="text-sm text-white">{pred.selection}</div>
                          <div className="text-xs text-[#52525B]">{pred.prediction_type}</div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-data font-bold text-white">@{pred.odds}</div>
                        <div className={`text-xs ${
                          pred.profit > 0 ? "text-[#CCFF00]" : 
                          pred.profit < 0 ? "text-[#FF2E2E]" : 
                          "text-[#A1A1AA]"
                        }`}>
                          {pred.profit !== null ? (pred.profit >= 0 ? `+$${pred.profit}` : `-$${Math.abs(pred.profit)}`) : "Pendiente"}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center text-[#A1A1AA]">
                  <ClockCounterClockwise size={48} className="mx-auto mb-4 text-[#27272A]" />
                  <p>No hay predicciones registradas</p>
                  <p className="text-xs text-[#52525B] mt-1">Tus apuestas aparecerán aquí</p>
                </div>
              )}
            </div>

            {/* Breakdown */}
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-[#0A0A0A] border border-[#27272A] p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-[#CCFF00]/10 flex items-center justify-center">
                  <CheckCircle size={24} className="text-[#CCFF00]" />
                </div>
                <div>
                  <div className="text-xs text-[#A1A1AA] uppercase">Ganadas</div>
                  <div className="font-data text-2xl font-bold text-[#CCFF00]">{stats?.won || 0}</div>
                </div>
              </div>
              <div className="bg-[#0A0A0A] border border-[#27272A] p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-[#FF2E2E]/10 flex items-center justify-center">
                  <XCircle size={24} className="text-[#FF2E2E]" />
                </div>
                <div>
                  <div className="text-xs text-[#A1A1AA] uppercase">Perdidas</div>
                  <div className="font-data text-2xl font-bold text-[#FF2E2E]">{stats?.lost || 0}</div>
                </div>
              </div>
              <div className="bg-[#0A0A0A] border border-[#27272A] p-4 flex items-center gap-4">
                <div className="w-12 h-12 bg-[#00E5FF]/10 flex items-center justify-center">
                  <Clock size={24} className="text-[#00E5FF]" />
                </div>
                <div>
                  <div className="text-xs text-[#A1A1AA] uppercase">Pendientes</div>
                  <div className="font-data text-2xl font-bold text-[#00E5FF]">{stats?.pending || 0}</div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}
