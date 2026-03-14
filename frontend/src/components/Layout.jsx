import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../App";
import {
  House,
  SoccerBall,
  TrendUp,
  ListChecks,
  Scales,
  ClockCounterClockwise,
  Gear,
  SignOut,
  List,
  X,
  TelegramLogo,
  Bell
} from "@phosphor-icons/react";

const navItems = [
  { to: "/", icon: House, label: "Dashboard" },
  { to: "/matches", icon: SoccerBall, label: "Partidos" },
  { to: "/value-bets", icon: TrendUp, label: "Value Bets" },
  { to: "/parlays", icon: ListChecks, label: "Combinadas" },
  { to: "/odds", icon: Scales, label: "Comparador" },
  { to: "/history", icon: ClockCounterClockwise, label: "Historial" },
  { to: "/settings", icon: Gear, label: "Configuración" },
];

export const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-[#050505] flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed lg:static inset-y-0 left-0 z-50 w-64 bg-[#080808] border-r border-[#27272A] transform transition-transform duration-200 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-4 border-b border-[#27272A]">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <TrendUp size={28} weight="bold" className="text-[#CCFF00]" />
                <span className="font-heading text-xl font-black uppercase tracking-tight text-white">
                  SB<span className="text-[#CCFF00]">AI</span>
                </span>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="lg:hidden text-[#A1A1AA] hover:text-white"
              >
                <X size={24} />
              </button>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setSidebarOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-2.5 text-sm transition-colors border-l-2 ${
                    isActive
                      ? "text-[#CCFF00] bg-[#CCFF00]/5 border-[#CCFF00]"
                      : "text-[#A1A1AA] hover:text-[#CCFF00] hover:bg-[#CCFF00]/5 border-transparent hover:border-[#CCFF00]"
                  }`
                }
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <item.icon size={20} weight="regular" />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            ))}
          </nav>

          {/* User section */}
          <div className="p-4 border-t border-[#27272A]">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-[#1E1E1E] border border-[#27272A] flex items-center justify-center">
                <span className="font-heading font-bold text-[#CCFF00]">
                  {user?.name?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-white truncate">{user?.name}</div>
                <div className="text-xs text-[#A1A1AA] truncate">{user?.email}</div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 w-full px-3 py-2 text-sm text-[#A1A1AA] hover:text-[#FF2E2E] hover:bg-[#FF2E2E]/5 transition-colors"
              data-testid="logout-button"
            >
              <SignOut size={18} />
              <span>Cerrar sesión</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen">
        {/* Header */}
        <header className="sticky top-0 z-30 bg-[#050505]/95 backdrop-blur-sm border-b border-[#27272A]">
          <div className="flex items-center justify-between px-4 h-14">
            <button
              onClick={() => setSidebarOpen(true)}
              className="lg:hidden text-[#A1A1AA] hover:text-white"
              data-testid="mobile-menu-button"
            >
              <List size={24} />
            </button>
            
            <div className="flex items-center gap-4 ml-auto">
              {user?.telegram_chat_id && (
                <div className="flex items-center gap-2 text-xs text-[#A1A1AA]">
                  <TelegramLogo size={16} className="text-[#00E5FF]" />
                  <span>Conectado</span>
                </div>
              )}
              <button className="relative text-[#A1A1AA] hover:text-white transition-colors">
                <Bell size={20} />
                <span className="absolute -top-1 -right-1 w-2 h-2 bg-[#CCFF00] rounded-full" />
              </button>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 md:p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
};
