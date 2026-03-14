import React, { useState } from "react";
import { Layout } from "../components/Layout";
import { api, useAuth } from "../App";
import { toast } from "sonner";
import {
  Gear,
  TelegramLogo,
  User,
  Bell,
  CheckCircle,
  Info,
  ArrowsClockwise
} from "@phosphor-icons/react";

export default function SettingsPage() {
  const { user, updateUser } = useAuth();
  const [telegramChatId, setTelegramChatId] = useState(user?.telegram_chat_id || "");
  const [savingTelegram, setSavingTelegram] = useState(false);
  const [testingTelegram, setTestingTelegram] = useState(false);

  const saveTelegram = async () => {
    if (!telegramChatId) {
      toast.error("Ingresa tu Chat ID de Telegram");
      return;
    }
    setSavingTelegram(true);
    try {
      await api.post("/telegram/setup", { chat_id: telegramChatId });
      updateUser({ telegram_chat_id: telegramChatId });
      toast.success("Telegram configurado correctamente");
    } catch (error) {
      toast.error("Error guardando configuración");
    } finally {
      setSavingTelegram(false);
    }
  };

  const testTelegram = async () => {
    if (!user?.telegram_chat_id && !telegramChatId) {
      toast.error("Primero configura tu Chat ID");
      return;
    }
    setTestingTelegram(true);
    try {
      await api.post("/telegram/test");
      toast.success("Mensaje de prueba enviado a Telegram");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error enviando mensaje de prueba");
    } finally {
      setTestingTelegram(false);
    }
  };

  return (
    <Layout>
      <div className="space-y-6" data-testid="settings-page">
        {/* Header */}
        <div>
          <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight text-white flex items-center gap-3">
            <Gear size={36} className="text-[#A1A1AA]" />
            Configuración
          </h1>
          <p className="text-[#A1A1AA] text-sm mt-1">
            Administra tu cuenta y preferencias
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Profile Section */}
          <div className="bg-[#0A0A0A] border border-[#27272A]">
            <div className="px-4 py-3 border-b border-[#27272A] flex items-center gap-2 bg-[#0F0F0F]">
              <User size={18} className="text-[#A1A1AA]" />
              <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white">
                Perfil
              </h2>
            </div>
            <div className="p-4 space-y-4">
              <div>
                <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                  Nombre
                </label>
                <input
                  type="text"
                  value={user?.name || ""}
                  disabled
                  className="w-full bg-[#050505] border border-[#27272A] text-[#A1A1AA] px-4 h-10 cursor-not-allowed"
                />
              </div>
              <div>
                <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={user?.email || ""}
                  disabled
                  className="w-full bg-[#050505] border border-[#27272A] text-[#A1A1AA] px-4 h-10 cursor-not-allowed"
                />
              </div>
              <div>
                <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                  Miembro desde
                </label>
                <input
                  type="text"
                  value={user?.created_at ? new Date(user.created_at).toLocaleDateString("es-ES", {
                    day: "numeric",
                    month: "long",
                    year: "numeric"
                  }) : ""}
                  disabled
                  className="w-full bg-[#050505] border border-[#27272A] text-[#A1A1AA] px-4 h-10 cursor-not-allowed"
                />
              </div>
            </div>
          </div>

          {/* Telegram Section */}
          <div className="bg-[#0A0A0A] border border-[#27272A]">
            <div className="px-4 py-3 border-b border-[#27272A] flex items-center gap-2 bg-[#0F0F0F]">
              <TelegramLogo size={18} className="text-[#00E5FF]" />
              <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white">
                Telegram Alerts
              </h2>
              {user?.telegram_chat_id && (
                <span className="ml-auto flex items-center gap-1 text-xs text-[#CCFF00]">
                  <CheckCircle size={14} />
                  Conectado
                </span>
              )}
            </div>
            <div className="p-4 space-y-4">
              {/* Instructions */}
              <div className="bg-[#00E5FF]/5 border border-[#00E5FF]/20 p-3">
                <div className="flex gap-2">
                  <Info size={18} className="text-[#00E5FF] flex-shrink-0 mt-0.5" />
                  <div className="text-xs text-[#A1A1AA]">
                    <p className="font-medium text-[#00E5FF] mb-1">¿Cómo obtener tu Chat ID?</p>
                    <ol className="list-decimal list-inside space-y-1">
                      <li>Busca nuestro bot en Telegram: <span className="text-white">@SportsBetAI_Bot</span></li>
                      <li>Envía el comando <span className="text-white">/start</span></li>
                      <li>El bot te responderá con tu Chat ID</li>
                      <li>Copia y pega el ID aquí</li>
                    </ol>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                  Chat ID
                </label>
                <input
                  type="text"
                  value={telegramChatId}
                  onChange={(e) => setTelegramChatId(e.target.value)}
                  placeholder="123456789"
                  className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-10 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none font-data"
                  data-testid="telegram-chat-id-input"
                />
              </div>

              <div className="flex gap-3">
                <button
                  onClick={saveTelegram}
                  disabled={savingTelegram}
                  className="flex-1 bg-[#CCFF00] text-black font-bold uppercase tracking-wider h-10 hover:bg-[#B3E600] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                  data-testid="save-telegram-button"
                >
                  {savingTelegram ? (
                    <ArrowsClockwise size={18} className="animate-spin" />
                  ) : (
                    <CheckCircle size={18} />
                  )}
                  Guardar
                </button>
                <button
                  onClick={testTelegram}
                  disabled={testingTelegram}
                  className="flex-1 bg-[#1E1E1E] text-white font-bold uppercase tracking-wider h-10 hover:bg-[#2A2A2A] border border-[#27272A] transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                  data-testid="test-telegram-button"
                >
                  {testingTelegram ? (
                    <ArrowsClockwise size={18} className="animate-spin" />
                  ) : (
                    <TelegramLogo size={18} />
                  )}
                  Probar
                </button>
              </div>
            </div>
          </div>

          {/* Notifications Section */}
          <div className="bg-[#0A0A0A] border border-[#27272A]">
            <div className="px-4 py-3 border-b border-[#27272A] flex items-center gap-2 bg-[#0F0F0F]">
              <Bell size={18} className="text-[#A1A1AA]" />
              <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white">
                Notificaciones
              </h2>
            </div>
            <div className="p-4 space-y-4">
              <div className="flex items-center justify-between py-2">
                <div>
                  <div className="text-sm text-white">Value Bets</div>
                  <div className="text-xs text-[#52525B]">Alertas cuando se detecte un value bet</div>
                </div>
                <button className="w-12 h-6 bg-[#CCFF00] rounded-full relative">
                  <span className="absolute right-1 top-1 w-4 h-4 bg-black rounded-full" />
                </button>
              </div>
              <div className="flex items-center justify-between py-2">
                <div>
                  <div className="text-sm text-white">Partidos en vivo</div>
                  <div className="text-xs text-[#52525B]">Notificaciones de partidos en curso</div>
                </div>
                <button className="w-12 h-6 bg-[#27272A] rounded-full relative">
                  <span className="absolute left-1 top-1 w-4 h-4 bg-[#52525B] rounded-full" />
                </button>
              </div>
              <div className="flex items-center justify-between py-2">
                <div>
                  <div className="text-sm text-white">Resultados</div>
                  <div className="text-xs text-[#52525B]">Resultado de tus predicciones</div>
                </div>
                <button className="w-12 h-6 bg-[#CCFF00] rounded-full relative">
                  <span className="absolute right-1 top-1 w-4 h-4 bg-black rounded-full" />
                </button>
              </div>
            </div>
          </div>

          {/* About Section */}
          <div className="bg-[#0A0A0A] border border-[#27272A]">
            <div className="px-4 py-3 border-b border-[#27272A] flex items-center gap-2 bg-[#0F0F0F]">
              <Info size={18} className="text-[#A1A1AA]" />
              <h2 className="font-heading text-sm font-bold uppercase tracking-wider text-white">
                Acerca de
              </h2>
            </div>
            <div className="p-4 space-y-3">
              <div className="flex justify-between items-center py-2 border-b border-[#27272A]/50">
                <span className="text-sm text-[#A1A1AA]">Versión</span>
                <span className="font-data text-sm text-white">1.0.0</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-[#27272A]/50">
                <span className="text-sm text-[#A1A1AA]">Deportes</span>
                <span className="font-data text-sm text-white">7</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-[#27272A]/50">
                <span className="text-sm text-[#A1A1AA]">Casas de apuestas</span>
                <span className="font-data text-sm text-white">5</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-[#A1A1AA]">Modelo IA</span>
                <span className="font-data text-sm text-[#CCFF00]">GPT-5.2</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
