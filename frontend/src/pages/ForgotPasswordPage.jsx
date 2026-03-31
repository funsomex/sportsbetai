import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { TrendUp, ArrowLeft, EnvelopeSimple, LockKey, CheckCircle } from "@phosphor-icons/react";
import { toast } from "sonner";
import axios from "axios";

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ForgotPasswordPage() {
  const [step, setStep] = useState(1); // 1: email, 2: code, 3: new password
  const [email, setEmail] = useState("");
  const [code, setCode] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [debugCode, setDebugCode] = useState(""); // Para desarrollo
  const navigate = useNavigate();

  const handleRequestCode = async (e) => {
    e.preventDefault();
    if (!email) {
      toast.error("Por favor ingresa tu email");
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/api/auth/forgot-password`, { email });
      toast.success(response.data.message);
      // Guardar el código de debug si existe (solo desarrollo)
      if (response.data.debug_code) {
        setDebugCode(response.data.debug_code);
      }
      setStep(2);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al enviar el código");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!code || !newPassword || !confirmPassword) {
      toast.error("Por favor completa todos los campos");
      return;
    }
    if (newPassword !== confirmPassword) {
      toast.error("Las contraseñas no coinciden");
      return;
    }
    if (newPassword.length < 6) {
      toast.error("La contraseña debe tener al menos 6 caracteres");
      return;
    }
    setLoading(true);
    try {
      await axios.post(`${API_URL}/api/auth/reset-password`, {
        email,
        reset_code: code,
        new_password: newPassword
      });
      toast.success("Contraseña actualizada correctamente");
      setStep(3);
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error al cambiar la contraseña");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#050505] flex items-center justify-center p-8">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex items-center gap-3 mb-12 justify-center">
          <TrendUp size={40} weight="bold" className="text-[#CCFF00]" />
          <span className="font-heading text-3xl font-black uppercase tracking-tight text-white">
            SportsBet<span className="text-[#CCFF00]">AI</span>
          </span>
        </div>

        <div className="bg-[#0A0A0A] border border-[#27272A] p-8">
          {/* Step 1: Request Code */}
          {step === 1 && (
            <>
              <div className="flex items-center gap-3 mb-6">
                <EnvelopeSimple size={32} className="text-[#CCFF00]" />
                <div>
                  <h2 className="font-heading text-2xl font-bold uppercase tracking-wide text-white">
                    Recuperar Contraseña
                  </h2>
                  <p className="text-[#A1A1AA] text-sm">
                    Te enviaremos un código por Telegram
                  </p>
                </div>
              </div>

              <form onSubmit={handleRequestCode} className="space-y-6">
                <div>
                  <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                    Email de tu cuenta
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors"
                    placeholder="tu@email.com"
                    data-testid="forgot-email-input"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-[#CCFF00] text-black font-bold uppercase tracking-wider h-12 hover:bg-[#B3E600] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  data-testid="forgot-submit-button"
                >
                  {loading ? "Enviando..." : "Enviar Código"}
                </button>
              </form>
            </>
          )}

          {/* Step 2: Enter Code and New Password */}
          {step === 2 && (
            <>
              <div className="flex items-center gap-3 mb-6">
                <LockKey size={32} className="text-[#CCFF00]" />
                <div>
                  <h2 className="font-heading text-2xl font-bold uppercase tracking-wide text-white">
                    Nueva Contraseña
                  </h2>
                  <p className="text-[#A1A1AA] text-sm">
                    Ingresa el código y tu nueva contraseña
                  </p>
                </div>
              </div>

              {/* Debug info - solo para desarrollo */}
              {debugCode && (
                <div className="bg-[#1A1A1A] border border-[#CCFF00]/30 p-4 mb-6">
                  <p className="text-xs text-[#A1A1AA] mb-1">Código de desarrollo:</p>
                  <p className="text-[#CCFF00] font-mono text-2xl tracking-widest">{debugCode}</p>
                </div>
              )}

              <form onSubmit={handleResetPassword} className="space-y-6">
                <div>
                  <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                    Código de verificación
                  </label>
                  <input
                    type="text"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors text-center font-mono text-xl tracking-[0.5em]"
                    placeholder="000000"
                    maxLength={6}
                    data-testid="reset-code-input"
                  />
                </div>

                <div>
                  <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                    Nueva Contraseña
                  </label>
                  <input
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors"
                    placeholder="••••••••"
                    data-testid="new-password-input"
                  />
                </div>

                <div>
                  <label className="block text-xs uppercase tracking-wider text-[#A1A1AA] mb-2">
                    Confirmar Contraseña
                  </label>
                  <input
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    className="w-full bg-[#050505] border border-[#27272A] text-white px-4 h-12 focus:border-[#CCFF00] focus:ring-1 focus:ring-[#CCFF00] outline-none transition-colors"
                    placeholder="••••••••"
                    data-testid="confirm-password-input"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full bg-[#CCFF00] text-black font-bold uppercase tracking-wider h-12 hover:bg-[#B3E600] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  data-testid="reset-submit-button"
                >
                  {loading ? "Guardando..." : "Cambiar Contraseña"}
                </button>
              </form>

              <button
                onClick={() => setStep(1)}
                className="mt-4 w-full text-[#A1A1AA] hover:text-white text-sm flex items-center justify-center gap-2"
              >
                <ArrowLeft size={16} />
                Volver a solicitar código
              </button>
            </>
          )}

          {/* Step 3: Success */}
          {step === 3 && (
            <div className="text-center py-8">
              <CheckCircle size={64} weight="fill" className="text-[#CCFF00] mx-auto mb-6" />
              <h2 className="font-heading text-2xl font-bold uppercase tracking-wide text-white mb-2">
                ¡Listo!
              </h2>
              <p className="text-[#A1A1AA] mb-8">
                Tu contraseña ha sido actualizada correctamente
              </p>
              <button
                onClick={() => navigate("/login")}
                className="w-full bg-[#CCFF00] text-black font-bold uppercase tracking-wider h-12 hover:bg-[#B3E600] transition-colors"
                data-testid="go-to-login-button"
              >
                Ir a Iniciar Sesión
              </button>
            </div>
          )}

          {step !== 3 && (
            <p className="mt-6 text-center text-[#A1A1AA] text-sm">
              <Link to="/login" className="text-[#CCFF00] hover:underline flex items-center justify-center gap-2">
                <ArrowLeft size={16} />
                Volver al inicio de sesión
              </Link>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
