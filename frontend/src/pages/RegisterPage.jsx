import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../App";
import { Eye, EyeSlash, TrendUp } from "@phosphor-icons/react";
import { toast } from "sonner";

export default function RegisterPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name || !email || !password || !confirmPassword) {
      toast.error("Por favor completa todos los campos");
      return;
    }
    if (password !== confirmPassword) {
      toast.error("Las contraseñas no coinciden");
      return;
    }
    if (password.length < 6) {
      toast.error("La contraseña debe tener al menos 6 caracteres");
      return;
    }
    setLoading(true);
    try {
      await register(name, email, password);
      toast.success("Cuenta creada exitosamente");
      navigate("/");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al registrarse");
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
            backgroundImage: `url('https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=2980&auto=format&fit=crop')`,
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
            Únete al<br />
            <span className="text-[#CCFF00]">Futuro</span>
          </h1>
          <p className="text-[#A1A1AA] text-lg max-w-md">
            Analiza más de 7 deportes, detecta value bets y recibe alertas en tiempo real vía Telegram.
          </p>
          <div className="mt-8 flex gap-6">
            <div className="text-center">
              <div className="font-data text-3xl font-bold text-[#CCFF00]">7+</div>
              <div className="text-[#A1A1AA] text-xs uppercase tracking-wider">Deportes</div>
            </div>
            <div className="text-center">
              <div className="font-data text-3xl font-bold text-[#00E5FF]">5</div>
              <div className="text-[#A1A1AA] text-xs uppercase tracking-wider">Casas</div>
            </div>
            <div className="text-center">
              <div className="font-data text-3xl font-bold text-white">AI</div>
              <div className="text-[#A1A1AA] text-xs uppercase tracking-wider">Powered</div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Register form */}
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
              Crear Cuenta
            </h2>
            <p className="text-[#A1A1AA] text-sm mb-8">
              Regístrate para acceder a predicciones con IA
            </p>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                  Nombre
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors"
                  placeholder="Tu nombre"
                  data-testid="register-name-input"
                />
              </div>

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
                  data-testid="register-email-input"
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
                    data-testid="register-password-input"
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

              <div>
                <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                  Confirmar Contraseña
                </label>
                <input
                  type={showPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors"
                  placeholder="••••••••"
                  data-testid="register-confirm-password-input"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#CCFF00] text-black font-bold uppercase tracking-wider h-12 hover:bg-[#B3E600] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                data-testid="register-submit-button"
              >
                {loading ? "Creando cuenta..." : "Crear Cuenta"}
              </button>
            </form>

            <p className="mt-6 text-center text-[#A1A1AA] text-sm">
              ¿Ya tienes cuenta?{" "}
              <Link to="/login" className="text-[#CCFF00] hover:underline" data-testid="login-link">
                Inicia sesión
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
