import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../App";
import { Eye, EyeSlash, TrendUp } from "@phosphor-icons/react";
import { toast } from "sonner";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error("Por favor completa todos los campos");
      return;
    }
    setLoading(true);
    try {
      await login(email, password);
      toast.success("Bienvenido de vuelta");
      navigate("/");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al iniciar sesión");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: `url('https://images.unsplash.com/photo-1709078477781-3f885189ecbf?crop=entropy&cs=srgb&fm=jpg&ixid=M3w4NjA1ODh8MHwxfHNlYXJjaHw0fHxzb2NjZXIlMjBzdGFkaXVtJTIwbmlnaHQlMjBtYXRjaCUyMGF0bW9zcGhlcmUlMjBkYXJrfGVufDB8fHx8MTc3MzUxODIxMnww&ixlib=rb-4.1.0&q=85')`,
            filter: 'brightness(0.4)'
          }}
        />
        <div className="absolute inset-0 bg-gradient-to-r from-[#050505] to-transparent" />
        <div className="relative z-10 flex flex-col justify-center p-12">
          <div className="flex items-center gap-3 mb-8">
            <TrendUp size={48} weight="bold" className="text-[#CCFF00]" />
            <span className="font-heading text-4xl font-black uppercase tracking-tight text-white">
              SportsBet<span className="text-[#CCFF00]">AI</span>
            </span>
          </div>
          <h1 className="font-heading text-5xl font-black uppercase tracking-tight text-white mb-4">
            Predicciones<br />
            <span className="text-[#CCFF00]">Inteligentes</span>
          </h1>
          <p className="text-[#A1A1AA] text-lg max-w-md">
            Sistema predictivo con IA para detectar value bets y maximizar tu ROI en apuestas deportivas.
          </p>
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-3 mb-12 justify-center">
            <TrendUp size={40} weight="bold" className="text-[#CCFF00]" />
            <span className="font-heading text-3xl font-black uppercase tracking-tight text-white">
              SportsBet<span className="text-[#CCFF00]">AI</span>
            </span>
          </div>

          <div className="bg-[#0A0A0A] border border-[#27272A] p-8">
            <h2 className="font-heading text-2xl font-bold uppercase tracking-wide text-white mb-2">
              Iniciar Sesión
            </h2>
            <p className="text-[#A1A1AA] text-sm mb-8">
              Accede a tu cuenta para ver predicciones
            </p>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors"
                  placeholder="tu@email.com"
                  data-testid="login-email-input"
                />
              </div>

              <div>
                <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                  Contraseña
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 pr-12 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors"
                    placeholder="••••••••"
                    data-testid="login-password-input"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-[#A1A1AA] hover:text-white transition-colors"
                  >
                    {showPassword ? <EyeSlash size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#CCFF00] text-black font-bold uppercase tracking-wider h-12 hover:bg-[#B3E600] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="login-submit-button"
              >
                {loading ? "Cargando..." : "Entrar"}
              </button>
            </form>

            <p className="mt-6 text-center text-[#A1A1AA] text-sm">
              ¿No tienes cuenta?{" "}
              <Link to="/register" className="text-[#CCFF00] hover:underline" data-testid="register-link">
                Regístrate
              </Link>
            </p>
            <p className="mt-3 text-center text-[#A1A1AA] text-sm">
              <Link to="/forgot-password" className="text-[#71717A] hover:text-[#CCFF00] hover:underline transition-colors" data-testid="forgot-password-link">
                ¿Olvidaste tu contraseña?
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
