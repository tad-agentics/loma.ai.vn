import { useState, useEffect, useRef } from "react";

/* ─── DESIGN TOKENS ─── */
const T = {
  bg: "#F5F0E8", bgAlt: "#EDE8DD", bgDark: "#2C2825", white: "#FFFFFF",
  text: "#2C2825", textSec: "#6B6560", textMuted: "#9C9590", textOnDark: "#F5F0E8",
  brand: "#0D9488", brandHover: "#0F766E", brandSubtle: "#CCFBF1", brandSubtleText: "#065F46",
  border: "#D8D2C8", borderSub: "#E8E2D8",
  success: "#10B981", warning: "#D97706", error: "#DC2626",
  errorSubtle: "#FEE2E2", errorText: "#991B1B",
  warningSubtle: "#FEF3C7", warningText: "#92400E",
  shadow: { sm: "0 1px 3px rgba(44,40,37,0.06)", md: "0 4px 12px rgba(44,40,37,0.08)", lg: "0 8px 24px rgba(44,40,37,0.12)" },
  font: {
    display: "'Newsreader', Georgia, serif",
    heading: "'Newsreader', Georgia, serif",
    body: "'Source Serif 4', Georgia, serif",
    ui: "'Be Vietnam Pro', 'Helvetica Neue', sans-serif",
    mono: "'JetBrains Mono', 'SF Mono', monospace",
  },
};

/* ─── HELPERS ─── */
const intentColors = {
  ask_payment: { emoji: "💰", vi: "Nhắc thanh toán", en: "Payment", bg: "#D1FAE5", text: "#065F46" },
  follow_up: { emoji: "🔄", vi: "Theo dõi", en: "Follow up", bg: "#FEF3C7", text: "#92400E" },
  request_senior: { emoji: "📋", vi: "Yêu cầu cấp trên", en: "Request", bg: "#DBEAFE", text: "#1E40AF" },
  say_no: { emoji: "🚫", vi: "Từ chối", en: "Decline", bg: "#FEE2E2", text: "#991B1B" },
  cold_outreach: { emoji: "🤝", vi: "Giới thiệu", en: "Outreach", bg: "#E0E7FF", text: "#3730A3" },
  give_feedback: { emoji: "💬", vi: "Góp ý", en: "Feedback", bg: "#FCE7F3", text: "#9D174D" },
  disagree: { emoji: "⚡", vi: "Không đồng ý", en: "Disagree", bg: "#FFF7ED", text: "#9A3412" },
  escalate: { emoji: "🔺", vi: "Chuyển cấp trên", en: "Escalate", bg: "#FEF2F2", text: "#7F1D1D" },
  apologize: { emoji: "🙏", vi: "Xin lỗi", en: "Apologize", bg: "#F0FDF4", text: "#166534" },
  ai_prompt: { emoji: "🤖", vi: "Prompt AI", en: "AI prompt", bg: "#F5F3FF", text: "#5B21B6" },
};

/* ─── SECTION NAV ─── */
const sections = [
  { id: "loma-button", label: "Loma Button" },
  { id: "result-card", label: "Result Card" },
  { id: "quick-pick", label: "Quick Pick" },
  { id: "toasts", label: "Toasts" },
  { id: "tooltip", label: "Tooltip" },
  { id: "errors", label: "Error States" },
  { id: "popup", label: "Popup" },
  { id: "ftux", label: "FTUX" },
];

/* ─── SHIMMER KEYFRAMES (injected once) ─── */
function ShimmerStyles() {
  return (
    <style>{`
      @keyframes loma-shimmer {
        0% { background-position: -400px 0; }
        100% { background-position: 400px 0; }
      }
      @keyframes loma-fade-up {
        0% { opacity: 0; transform: translateY(8px); }
        100% { opacity: 1; transform: translateY(0); }
      }
      @keyframes loma-pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
      }
      @keyframes loma-toast-timer {
        0% { width: 100%; }
        100% { width: 0%; }
      }
      @keyframes loma-spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      .loma-shimmer-bar {
        background: linear-gradient(90deg, ${T.bgAlt} 25%, ${T.bg} 50%, ${T.bgAlt} 75%);
        background-size: 800px 100%;
        animation: loma-shimmer 1.8s infinite ease-in-out;
        border-radius: 6px;
      }
    `}</style>
  );
}

/* ─── COMPONENTS ─── */

function SectionTitle({ children }) {
  return <h2 style={{ fontFamily: T.font.heading, fontSize: 26, fontWeight: 600, margin: "0 0 6px", letterSpacing: "-0.01em", color: T.text }}>{children}</h2>;
}
function SectionDesc({ children }) {
  return <p style={{ fontFamily: T.font.body, fontSize: 14, color: T.textSec, margin: "0 0 24px", lineHeight: 1.6 }}>{children}</p>;
}
function StateLabel({ children }) {
  return <div style={{ fontFamily: T.font.ui, fontSize: 11, fontWeight: 600, color: T.textMuted, letterSpacing: "0.07em", textTransform: "uppercase", marginBottom: 10 }}>{children}</div>;
}
function Divider() {
  return <div style={{ height: 1, backgroundColor: T.border, margin: "40px 0" }} />;
}

/* Loma Button */
function LomaButton({ state = "dormant" }) {
  const base = {
    fontFamily: T.font.ui, fontSize: 12, fontWeight: 600, border: "none", cursor: "pointer",
    display: "inline-flex", alignItems: "center", gap: 6, transition: "all 0.15s ease",
    borderRadius: 8, letterSpacing: "0.01em",
  };
  if (state === "dormant") return (
    <button style={{ ...base, padding: "6px 12px", backgroundColor: T.white, color: T.brand, boxShadow: T.shadow.sm, border: `1px solid ${T.borderSub}` }}>
      <span style={{ fontSize: 14 }}>✦</span> Loma
    </button>
  );
  if (state === "hover") return (
    <button style={{ ...base, padding: "6px 12px", backgroundColor: T.brand, color: "#fff", boxShadow: T.shadow.md }}>
      <span style={{ fontSize: 14 }}>✦</span> Viết lại
    </button>
  );
  if (state === "active") return (
    <button style={{ ...base, padding: "6px 12px", backgroundColor: T.brandHover, color: "#fff", boxShadow: T.shadow.sm, transform: "scale(0.97)" }}>
      <span style={{ fontSize: 14 }}>✦</span> Viết lại
    </button>
  );
  if (state === "loading") return (
    <button style={{ ...base, padding: "6px 12px", backgroundColor: T.brand, color: "#fff", boxShadow: T.shadow.sm, opacity: 0.85, cursor: "wait" }}>
      <span style={{ display: "inline-block", width: 12, height: 12, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "#fff", borderRadius: "50%", animation: "loma-spin 0.6s linear infinite" }} />
      Đang viết...
    </button>
  );
  if (state === "disabled") return (
    <button style={{ ...base, padding: "6px 12px", backgroundColor: T.bgAlt, color: T.textMuted, boxShadow: "none", border: `1px solid ${T.borderSub}`, cursor: "not-allowed" }}>
      <span style={{ fontSize: 14, opacity: 0.4 }}>✦</span> Loma
    </button>
  );
  return null;
}

/* Intent Badge */
function IntentBadge({ intent }) {
  const ic = intentColors[intent] || intentColors.ask_payment;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5, padding: "4px 10px",
      borderRadius: 9999, backgroundColor: ic.bg, fontFamily: T.font.ui,
      fontSize: 12, color: ic.text, fontWeight: 500,
    }}>
      <span>{ic.emoji}</span>
      <span>{ic.vi}</span>
      <span style={{ opacity: 0.4 }}>·</span>
      <span style={{ opacity: 0.65 }}>{ic.en}</span>
    </span>
  );
}

/* Result Card */
function ResultCard({ state = "populated" }) {
  const [showOriginal, setShowOriginal] = useState(false);
  const cardBase = {
    width: "100%", maxWidth: 400, backgroundColor: T.white, borderRadius: 12,
    border: `1px solid ${T.border}`, boxShadow: T.shadow.lg, overflow: "hidden",
  };

  if (state === "skeleton") return (
    <div style={cardBase}>
      <div style={{ padding: "14px 20px 10px", borderBottom: `1px solid ${T.borderSub}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div className="loma-shimmer-bar" style={{ width: 160, height: 22 }} />
        <div className="loma-shimmer-bar" style={{ width: 16, height: 16, borderRadius: 4 }} />
      </div>
      <div style={{ padding: "14px 20px 16px" }}>
        <div className="loma-shimmer-bar" style={{ width: "100%", height: 14, marginBottom: 10 }} />
        <div className="loma-shimmer-bar" style={{ width: "90%", height: 14, marginBottom: 10 }} />
        <div className="loma-shimmer-bar" style={{ width: "60%", height: 14, marginBottom: 16 }} />
        <div className="loma-shimmer-bar" style={{ width: 80, height: 12 }} />
      </div>
      <div style={{ padding: "10px 20px 14px", borderTop: `1px solid ${T.borderSub}`, display: "flex", gap: 8 }}>
        <div className="loma-shimmer-bar" style={{ flex: 1, height: 34 }} />
        <div className="loma-shimmer-bar" style={{ flex: 1, height: 34 }} />
        <div className="loma-shimmer-bar" style={{ width: 70, height: 34 }} />
      </div>
    </div>
  );

  if (state === "loading") return (
    <div style={cardBase}>
      <div style={{ padding: "14px 20px 10px", borderBottom: `1px solid ${T.borderSub}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <IntentBadge intent="ask_payment" />
        <span style={{ fontFamily: T.font.ui, fontSize: 16, color: T.textMuted, cursor: "pointer" }}>✕</span>
      </div>
      <div style={{ padding: "24px 20px", display: "flex", flexDirection: "column", alignItems: "center", gap: 12 }}>
        <span style={{ display: "inline-block", width: 20, height: 20, border: `2.5px solid ${T.borderSub}`, borderTopColor: T.brand, borderRadius: "50%", animation: "loma-spin 0.7s linear infinite" }} />
        <span style={{ fontFamily: T.font.ui, fontSize: 13, color: T.textSec }}>Đang viết lại cho bạn...</span>
      </div>
    </div>
  );

  if (state === "error") return (
    <div style={cardBase}>
      <div style={{ padding: "14px 20px 10px", borderBottom: `1px solid ${T.borderSub}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontFamily: T.font.ui, fontSize: 13, fontWeight: 600, color: T.error }}>Lỗi</span>
        <span style={{ fontFamily: T.font.ui, fontSize: 16, color: T.textMuted, cursor: "pointer" }}>✕</span>
      </div>
      <div style={{ padding: "16px 20px", display: "flex", gap: 10, alignItems: "flex-start" }}>
        <span style={{ fontSize: 16 }}>⚠️</span>
        <div>
          <p style={{ fontFamily: T.font.ui, fontSize: 13, color: T.text, margin: "0 0 4px", fontWeight: 500 }}>Không thể kết nối máy chủ</p>
          <p style={{ fontFamily: T.font.ui, fontSize: 12, color: T.textSec, margin: 0, lineHeight: 1.5 }}>Kiểm tra kết nối mạng rồi thử lại.</p>
        </div>
      </div>
      <div style={{ padding: "10px 20px 14px", borderTop: `1px solid ${T.borderSub}` }}>
        <button style={{ fontFamily: T.font.ui, fontSize: 13, fontWeight: 600, padding: "8px 16px", borderRadius: 8, border: "none", backgroundColor: T.brand, color: "#fff", cursor: "pointer", width: "100%" }}>↻ Thử lại</button>
      </div>
    </div>
  );

  /* populated (default) + original-expanded */
  return (
    <div style={{ ...cardBase, animation: "loma-fade-up 0.25s ease-out" }}>
      <div style={{ padding: "14px 20px 10px", borderBottom: `1px solid ${T.borderSub}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <IntentBadge intent="ask_payment" />
        <span style={{ fontFamily: T.font.ui, fontSize: 16, color: T.textMuted, cursor: "pointer" }}>✕</span>
      </div>
      <div style={{ padding: "10px 20px 4px" }}>
        <div onClick={() => setShowOriginal(!showOriginal)} style={{ fontFamily: T.font.ui, fontSize: 13, color: T.brand, cursor: "pointer", marginBottom: 10, userSelect: "none" }}>
          {showOriginal ? "▾" : "▸"} Xem bản gốc
        </div>
        {showOriginal && (
          <div style={{ padding: "10px 14px", backgroundColor: T.bgAlt, borderRadius: 8, marginBottom: 12, animation: "loma-fade-up 0.2s ease-out" }}>
            <p style={{ fontFamily: T.font.body, fontSize: 13, color: T.textSec, margin: 0, lineHeight: 1.65, fontStyle: "italic" }}>
              anh Minh ơi, cái invoice tháng 1 chưa thanh toán, 5000 USD quá hạn 2 tuần rồi
            </p>
          </div>
        )}
        <p style={{ fontFamily: T.font.body, fontSize: 14, color: T.text, margin: "0 0 12px", lineHeight: 1.7 }}>
          Hi Minh, following up on VinAI's January invoice for $5,000 — now 2 weeks overdue. Could you confirm the expected payment date by Friday?
        </p>
      </div>
      <div style={{ padding: "0 20px 10px", borderBottom: `1px solid ${T.borderSub}` }}>
        <span style={{ fontFamily: T.font.ui, fontSize: 12, color: T.textSec }}>✂️ Ngắn hơn 52%</span>
      </div>
      <div style={{ padding: "10px 20px 14px", display: "flex", gap: 8 }}>
        <button style={{ fontFamily: T.font.ui, fontSize: 13, fontWeight: 600, padding: "8px 16px", borderRadius: 8, border: "none", backgroundColor: T.brand, color: "#fff", cursor: "pointer", flex: 1 }}>✓ Dùng</button>
        <button style={{ fontFamily: T.font.ui, fontSize: 13, fontWeight: 500, padding: "8px 16px", borderRadius: 8, border: `1.5px solid ${T.border}`, backgroundColor: "transparent", color: T.text, cursor: "pointer", flex: 1 }}>📋 Sao chép</button>
        <button style={{ fontFamily: T.font.ui, fontSize: 13, fontWeight: 500, padding: "8px 14px", borderRadius: 8, border: "none", backgroundColor: "transparent", color: T.brand, cursor: "pointer" }}>↻ Đổi giọng</button>
      </div>
    </div>
  );
}

/* Quick Pick Card */
function QuickPickCard() {
  const [selected, setSelected] = useState(null);
  const intents = [
    { key: "ask_payment", emoji: "💰", label: "Nhắc thanh toán" },
    { key: "follow_up", emoji: "🔄", label: "Theo dõi" },
    { key: "say_no", emoji: "🚫", label: "Từ chối" },
    { key: "request_senior", emoji: "📋", label: "Yêu cầu cấp trên" },
    { key: "cold_outreach", emoji: "🤝", label: "Giới thiệu" },
    { key: "other", emoji: "···", label: "Khác..." },
  ];
  return (
    <div style={{
      width: "100%", maxWidth: 360, backgroundColor: T.white, borderRadius: 12,
      border: `1px solid ${T.border}`, boxShadow: T.shadow.lg, padding: 20,
      animation: "loma-fade-up 0.25s ease-out",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 14 }}>
        <span style={{ fontFamily: T.font.heading, fontSize: 15, fontWeight: 600, color: T.text }}>Bạn muốn làm gì?</span>
        <span style={{ fontFamily: T.font.ui, fontSize: 16, color: T.textMuted, cursor: "pointer" }}>✕</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
        {intents.map(item => (
          <div
            key={item.key}
            onClick={() => setSelected(item.key)}
            style={{
              padding: "10px 12px", borderRadius: 8, cursor: "pointer",
              border: selected === item.key ? `2px solid ${T.brand}` : `1.5px solid ${T.border}`,
              backgroundColor: selected === item.key ? T.brandSubtle : "transparent",
              fontFamily: T.font.ui, fontSize: 13, fontWeight: 500, color: T.text,
              display: "flex", alignItems: "center", gap: 7, transition: "all 0.12s ease",
            }}
          >
            <span>{item.emoji}</span><span>{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* Toasts */
function UndoToast({ active }) {
  return (
    <div style={{
      display: "inline-flex", alignItems: "center", gap: 12, padding: "10px 20px",
      backgroundColor: T.bgDark, borderRadius: 10, boxShadow: T.shadow.md,
      position: "relative", overflow: "hidden", minWidth: 260,
    }}>
      <span style={{ fontFamily: T.font.ui, fontSize: 13, color: T.textOnDark }}>✓ Đã thay văn bản</span>
      <span style={{ fontFamily: T.font.ui, fontSize: 13, fontWeight: 600, color: T.brandSubtle, cursor: "pointer", textDecoration: "underline", textUnderlineOffset: 3 }}>Hoàn tác</span>
      {active && <div style={{
        position: "absolute", bottom: 0, left: 0, height: 3, backgroundColor: T.brand,
        animation: "loma-toast-timer 5s linear forwards", borderRadius: "0 0 10px 10px",
      }} />}
    </div>
  );
}

function CopyToast() {
  return (
    <div style={{
      display: "inline-flex", alignItems: "center", gap: 8, padding: "10px 20px",
      backgroundColor: T.bgDark, borderRadius: 10, boxShadow: T.shadow.md,
    }}>
      <span style={{ fontFamily: T.font.ui, fontSize: 13, color: T.textOnDark }}>📋 Đã sao chép</span>
    </div>
  );
}

/* Tooltip */
function TooltipDemo() {
  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      <LomaButton state="dormant" />
      <div style={{
        position: "absolute", bottom: "calc(100% + 10px)", left: "50%", transform: "translateX(-50%)",
        backgroundColor: T.bgDark, borderRadius: 8, padding: "10px 14px", boxShadow: T.shadow.md,
        whiteSpace: "nowrap", animation: "loma-fade-up 0.2s ease-out", minWidth: 180,
      }}>
        <p style={{ fontFamily: T.font.ui, fontSize: 12, fontWeight: 500, color: T.textOnDark, margin: "0 0 2px" }}>Nhấn để viết lại bằng tiếng Anh</p>
        <p style={{ fontFamily: T.font.ui, fontSize: 11, color: T.textMuted, margin: 0 }}>Phím tắt: Ctrl+Shift+L</p>
        <div style={{
          position: "absolute", top: "100%", left: "50%", transform: "translateX(-50%)",
          width: 0, height: 0, borderLeft: "6px solid transparent",
          borderRight: "6px solid transparent", borderTop: `6px solid ${T.bgDark}`,
        }} />
      </div>
    </div>
  );
}

/* Error states */
function ErrorBanner({ type }) {
  const configs = {
    offline: { icon: "📡", title: "Không có kết nối mạng", desc: "Loma cần Internet để viết lại. Kiểm tra Wi-Fi rồi thử lại.", bg: T.warningSubtle, border: T.warning, text: T.warningText },
    rate_limit: { icon: "⏳", title: "Hết lượt viết miễn phí hôm nay", desc: "Mua thêm gói 20 lượt với giá 49K VND hoặc quay lại ngày mai.", bg: T.warningSubtle, border: T.warning, text: T.warningText, cta: "Mua thêm lượt" },
    server: { icon: "⚠️", title: "Máy chủ đang bận", desc: "Thử lại sau vài giây. Nếu lỗi tiếp tục, liên hệ hỗ trợ.", bg: T.errorSubtle, border: T.error, text: T.errorText },
    balance: { icon: "💳", title: "Hết lượt viết lại", desc: "Tài khoản PAYG: 0 lượt còn lại.", bg: T.warningSubtle, border: T.warning, text: T.warningText, cta: "Nạp thêm" },
  };
  const c = configs[type];
  return (
    <div style={{
      padding: "14px 16px", borderRadius: 10, backgroundColor: c.bg,
      borderLeft: `4px solid ${c.border}`, maxWidth: 380,
    }}>
      <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
        <span style={{ fontSize: 16, lineHeight: 1 }}>{c.icon}</span>
        <div>
          <p style={{ fontFamily: T.font.ui, fontSize: 13, fontWeight: 600, color: c.text, margin: "0 0 3px" }}>{c.title}</p>
          <p style={{ fontFamily: T.font.ui, fontSize: 12, color: c.text, margin: 0, lineHeight: 1.5, opacity: 0.85 }}>{c.desc}</p>
          {c.cta && (
            <button style={{
              fontFamily: T.font.ui, fontSize: 12, fontWeight: 600, marginTop: 10,
              padding: "6px 14px", borderRadius: 6, border: "none",
              backgroundColor: c.border, color: "#fff", cursor: "pointer",
            }}>{c.cta}</button>
          )}
        </div>
      </div>
    </div>
  );
}

/* Extension Popup */
function PopupPreview() {
  return (
    <div style={{
      width: 320, backgroundColor: T.bg, borderRadius: 12, border: `1px solid ${T.border}`,
      boxShadow: T.shadow.lg, overflow: "hidden",
    }}>
      {/* Header */}
      <div style={{ padding: "16px 20px 12px", borderBottom: `1px solid ${T.borderSub}` }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
            <span style={{ fontFamily: T.font.display, fontSize: 22, fontWeight: 700, color: T.text }}>Loma</span>
            <span style={{
              fontFamily: T.font.ui, fontSize: 10, fontWeight: 600, color: T.brand,
              padding: "2px 8px", borderRadius: 9999, backgroundColor: T.brandSubtle,
            }}>PAYG</span>
          </div>
          <span style={{ fontFamily: T.font.ui, fontSize: 16, color: T.textMuted, cursor: "pointer" }}>⚙️</span>
        </div>
      </div>

      {/* Balance */}
      <div style={{ padding: "14px 20px", borderBottom: `1px solid ${T.borderSub}` }}>
        <div style={{ fontFamily: T.font.ui, fontSize: 11, fontWeight: 600, color: T.textMuted, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 6 }}>Lượt còn lại</div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
          <span style={{ fontFamily: T.font.display, fontSize: 32, fontWeight: 700, color: T.text }}>34</span>
          <span style={{ fontFamily: T.font.ui, fontSize: 13, color: T.textSec }}>lượt viết lại</span>
        </div>
        <button style={{
          fontFamily: T.font.ui, fontSize: 12, fontWeight: 600, marginTop: 10,
          padding: "7px 14px", borderRadius: 8, border: "none",
          backgroundColor: T.brand, color: "#fff", cursor: "pointer",
        }}>+ Mua thêm lượt</button>
      </div>

      {/* Stats */}
      <div style={{ padding: "14px 20px", borderBottom: `1px solid ${T.borderSub}` }}>
        <div style={{ fontFamily: T.font.ui, fontSize: 11, fontWeight: 600, color: T.textMuted, letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 10 }}>Thống kê</div>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div>
            <div style={{ fontFamily: T.font.display, fontSize: 20, fontWeight: 700, color: T.text }}>7</div>
            <div style={{ fontFamily: T.font.ui, fontSize: 11, color: T.textSec }}>Hôm nay</div>
          </div>
          <div>
            <div style={{ fontFamily: T.font.display, fontSize: 20, fontWeight: 700, color: T.text }}>143</div>
            <div style={{ fontFamily: T.font.ui, fontSize: 11, color: T.textSec }}>Tháng này</div>
          </div>
        </div>
      </div>

      {/* Site toggle */}
      <div style={{ padding: "12px 20px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontFamily: T.font.ui, fontSize: 13, fontWeight: 500, color: T.text }}>mail.google.com</div>
          <div style={{ fontFamily: T.font.ui, fontSize: 11, color: T.textSec }}>Loma đang bật trên trang này</div>
        </div>
        <div style={{
          width: 40, height: 22, borderRadius: 11, backgroundColor: T.brand,
          position: "relative", cursor: "pointer",
        }}>
          <div style={{
            width: 18, height: 18, borderRadius: 9, backgroundColor: "#fff",
            position: "absolute", top: 2, right: 2, boxShadow: T.shadow.sm,
          }} />
        </div>
      </div>
    </div>
  );
}

/* FTUX Onboarding */
function FTUXPreview() {
  const [step, setStep] = useState(0);
  const steps = [
    {
      title: "Chào mừng bạn đến với Loma",
      desc: "Viết tiếng Việt. Loma chuyển sang tiếng Anh chuyên nghiệp.",
      demo: null,
    },
    {
      title: "Thử viết lại ngay",
      desc: "Đây là email mẫu. Nhấn nút Loma để xem kết quả.",
      demo: "compose",
    },
    {
      title: "Loma hiểu bạn muốn gì",
      desc: "Tự động phát hiện: nhắc thanh toán, từ chối, theo dõi, và 7 tình huống khác.",
      demo: "intents",
    },
  ];
  const s = steps[step];

  return (
    <div style={{
      width: "100%", maxWidth: 520, backgroundColor: T.white, borderRadius: 12,
      border: `1px solid ${T.border}`, boxShadow: T.shadow.lg, overflow: "hidden",
    }}>
      {/* Progress */}
      <div style={{ display: "flex", gap: 4, padding: "16px 24px 0" }}>
        {steps.map((_, i) => (
          <div key={i} style={{
            flex: 1, height: 3, borderRadius: 2,
            backgroundColor: i <= step ? T.brand : T.borderSub,
            transition: "background-color 0.2s ease",
          }} />
        ))}
      </div>

      <div style={{ padding: "20px 24px 24px" }}>
        <h3 style={{ fontFamily: T.font.heading, fontSize: 20, fontWeight: 600, color: T.text, margin: "0 0 6px" }}>{s.title}</h3>
        <p style={{ fontFamily: T.font.body, fontSize: 14, color: T.textSec, margin: "0 0 20px", lineHeight: 1.6 }}>{s.desc}</p>

        {/* Demo area */}
        {s.demo === "compose" && (
          <div style={{ backgroundColor: T.bg, borderRadius: 10, border: `1px solid ${T.borderSub}`, padding: 16, marginBottom: 16 }}>
            <div style={{ fontFamily: T.font.ui, fontSize: 11, color: T.textMuted, marginBottom: 8, fontWeight: 500 }}>To: minh@vinai.io</div>
            <div style={{ fontFamily: T.font.body, fontSize: 13, color: T.text, lineHeight: 1.7, marginBottom: 12, minHeight: 50 }}>
              Anh Minh ơi, cái invoice tháng trước chưa thanh toán, 5000 USD quá hạn 2 tuần rồi anh
            </div>
            <div style={{ display: "flex", justifyContent: "flex-end" }}>
              <LomaButton state="hover" />
            </div>
          </div>
        )}

        {s.demo === "intents" && (
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 16 }}>
            {Object.keys(intentColors).slice(0, 6).map(k => <IntentBadge key={k} intent={k} />)}
          </div>
        )}

        {/* Navigation */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <button
            onClick={() => setStep(Math.max(0, step - 1))}
            disabled={step === 0}
            style={{
              fontFamily: T.font.ui, fontSize: 13, fontWeight: 500, padding: "8px 16px",
              borderRadius: 8, border: "none", backgroundColor: "transparent",
              color: step === 0 ? T.textMuted : T.brand, cursor: step === 0 ? "default" : "pointer",
            }}
          >{step > 0 ? "← Quay lại" : ""}</button>
          <button
            onClick={() => setStep(Math.min(steps.length - 1, step + 1))}
            style={{
              fontFamily: T.font.ui, fontSize: 13, fontWeight: 600, padding: "8px 20px",
              borderRadius: 8, border: "none", backgroundColor: T.brand, color: "#fff", cursor: "pointer",
            }}
          >{step === steps.length - 1 ? "Bắt đầu dùng Loma →" : "Tiếp tục →"}</button>
        </div>
      </div>
    </div>
  );
}

/* ─── MAIN APP ─── */
export default function ComponentPlayground() {
  const [active, setActive] = useState("loma-button");
  const [toastKey, setToastKey] = useState(0);

  return (
    <div style={{ minHeight: "100vh", backgroundColor: T.bg, color: T.text, display: "flex" }}>
      <ShimmerStyles />
      <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Be+Vietnam+Pro:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* Sidebar */}
      <div style={{
        width: 200, flexShrink: 0, padding: "32px 20px", borderRight: `1px solid ${T.border}`,
        position: "sticky", top: 0, height: "100vh", overflowY: "auto",
      }}>
        <div style={{ fontFamily: T.font.display, fontSize: 20, fontWeight: 700, color: T.text, marginBottom: 4 }}>Loma</div>
        <div style={{ fontFamily: T.font.ui, fontSize: 10, fontWeight: 600, color: T.textMuted, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 24 }}>Components v1.0</div>
        {sections.map(s => (
          <div
            key={s.id}
            onClick={() => setActive(s.id)}
            style={{
              fontFamily: T.font.ui, fontSize: 13, fontWeight: active === s.id ? 600 : 400,
              color: active === s.id ? T.brand : T.textSec,
              padding: "7px 10px", borderRadius: 6, cursor: "pointer", marginBottom: 2,
              backgroundColor: active === s.id ? T.brandSubtle : "transparent",
              transition: "all 0.12s ease",
            }}
          >{s.label}</div>
        ))}
      </div>

      {/* Main */}
      <div style={{ flex: 1, padding: "40px 48px 80px", maxWidth: 720 }}>

        {active === "loma-button" && (
          <div>
            <SectionTitle>Loma Button</SectionTitle>
            <SectionDesc>The trigger element injected into text fields via Shadow DOM. Appears when Vietnamese is detected (≥10 chars, ≥3 diacritics or ≥2 function words).</SectionDesc>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 24, marginBottom: 32 }}>
              {["dormant", "hover", "active", "loading", "disabled"].map(state => (
                <div key={state}>
                  <StateLabel>{state}</StateLabel>
                  <LomaButton state={state} />
                </div>
              ))}
            </div>

            <Divider />
            <StateLabel>In Context — Gmail Compose</StateLabel>
            <div style={{ backgroundColor: T.white, borderRadius: 10, border: `1px solid ${T.border}`, padding: 20, maxWidth: 460 }}>
              <div style={{ fontFamily: T.font.ui, fontSize: 12, color: T.textMuted, marginBottom: 4 }}>To: minh@vinai.io</div>
              <div style={{ fontFamily: T.font.ui, fontSize: 12, color: T.textMuted, marginBottom: 12 }}>Subject: Invoice tháng 1</div>
              <div style={{ fontFamily: T.font.body, fontSize: 14, color: T.text, lineHeight: 1.7, marginBottom: 16, minHeight: 60 }}>
                Anh Minh ơi, cái invoice tháng 1 chưa thanh toán, 5000 USD quá hạn 2 tuần rồi anh. Em cần anh confirm lại ngày thanh toán giúp em nhé.
              </div>
              <div style={{ display: "flex", justifyContent: "flex-end" }}>
                <LomaButton state="dormant" />
              </div>
            </div>

            <Divider />
            <StateLabel>Specs</StateLabel>
            <div style={{ fontFamily: T.font.mono, fontSize: 12, color: T.textSec, lineHeight: 1.8, backgroundColor: T.bgAlt, padding: 16, borderRadius: 8 }}>
              Element: &lt;loma-button&gt; (Shadow DOM)<br />
              Position: bottom-right of text field, 8px inset<br />
              Min field height to show: 38px<br />
              Min text length: 10 characters<br />
              Z-index: 2147483640<br />
              Transition: all 150ms ease-out<br />
              Keyboard shortcut: Ctrl+Shift+L (Cmd+Shift+L on Mac)
            </div>
          </div>
        )}

        {active === "result-card" && (
          <div>
            <SectionTitle>Result Card</SectionTitle>
            <SectionDesc>The core product surface. Shows after the user taps the Loma button. All states must feel intentional and calm.</SectionDesc>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 32 }}>
              <div>
                <StateLabel>Skeleton (Initial Load)</StateLabel>
                <ResultCard state="skeleton" />
              </div>
              <div>
                <StateLabel>Loading (Intent Detected)</StateLabel>
                <ResultCard state="loading" />
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 32 }}>
              <div>
                <StateLabel>Populated (Click "Xem bản gốc" to expand)</StateLabel>
                <ResultCard state="populated" />
              </div>
              <div>
                <StateLabel>Error</StateLabel>
                <ResultCard state="error" />
              </div>
            </div>

            <Divider />
            <StateLabel>Specs</StateLabel>
            <div style={{ fontFamily: T.font.mono, fontSize: 12, color: T.textSec, lineHeight: 1.8, backgroundColor: T.bgAlt, padding: 16, borderRadius: 8 }}>
              Element: &lt;loma-card&gt; (Shadow DOM)<br />
              Max width: 440px<br />
              Position: below Loma button, right-aligned<br />
              Entry animation: fade-up 250ms ease-out<br />
              Dismiss: ✕ button, click outside, or Escape key<br />
              Auto-dismiss: never (user must act)<br />
              Shadow: lg (0 8px 24px rgba(44,40,37,0.12))
            </div>
          </div>
        )}

        {active === "quick-pick" && (
          <div>
            <SectionTitle>Quick Pick</SectionTitle>
            <SectionDesc>Appears when intent confidence is below threshold. 2×2 grid of top intent suggestions in Vietnamese. One tap selects. Click to try.</SectionDesc>
            <QuickPickCard />

            <Divider />
            <StateLabel>All Intent Badges</StateLabel>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {Object.keys(intentColors).map(k => <IntentBadge key={k} intent={k} />)}
            </div>

            <Divider />
            <StateLabel>Tone Selector (Post-Rewrite)</StateLabel>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
              {[
                { label: "Trực tiếp hơn", active: true },
                { label: "Nhẹ nhàng hơn", active: false },
                { label: "Ngắn gọn hơn", active: false },
                { label: "Trang trọng hơn", active: false },
              ].map(t => (
                <span key={t.label} style={{
                  fontFamily: T.font.ui, fontSize: 13, fontWeight: 500,
                  padding: "6px 14px", borderRadius: 9999, cursor: "pointer",
                  backgroundColor: t.active ? T.brand : T.bgAlt,
                  color: t.active ? "#fff" : T.text,
                  border: t.active ? "none" : `1px solid ${T.border}`,
                }}>{t.label}</span>
              ))}
            </div>
          </div>
        )}

        {active === "toasts" && (
          <div>
            <SectionTitle>Toasts</SectionTitle>
            <SectionDesc>Transient feedback after user actions. Dark background for contrast against cream canvas. Undo toast has a 5-second timer bar.</SectionDesc>

            <div style={{ display: "flex", flexDirection: "column", gap: 20, marginBottom: 32 }}>
              <div>
                <StateLabel>Undo Toast (with 5s timer — click to restart)</StateLabel>
                <div onClick={() => setToastKey(k => k + 1)} style={{ cursor: "pointer" }}>
                  <UndoToast key={toastKey} active={true} />
                </div>
              </div>
              <div>
                <StateLabel>Copy Confirmation</StateLabel>
                <CopyToast />
              </div>
              <div>
                <StateLabel>Undo Toast (static / timer expired)</StateLabel>
                <UndoToast active={false} />
              </div>
            </div>

            <Divider />
            <StateLabel>Specs</StateLabel>
            <div style={{ fontFamily: T.font.mono, fontSize: 12, color: T.textSec, lineHeight: 1.8, backgroundColor: T.bgAlt, padding: 16, borderRadius: 8 }}>
              Element: &lt;loma-toast&gt; (Shadow DOM)<br />
              Position: bottom-center of viewport, 24px from bottom<br />
              Background: Espresso (#2C2825)<br />
              Entry: fade-up 200ms<br />
              Undo timer: 5 seconds, teal progress bar<br />
              Copy toast: auto-dismiss after 2 seconds<br />
              Max one toast visible at a time
            </div>
          </div>
        )}

        {active === "tooltip" && (
          <div>
            <SectionTitle>Tooltip</SectionTitle>
            <SectionDesc>First-time hint shown on hover for new users. Appears above the Loma button. Dismissed after first use or manual close.</SectionDesc>

            <div style={{ paddingTop: 60, paddingBottom: 40 }}>
              <TooltipDemo />
            </div>

            <Divider />
            <StateLabel>Specs</StateLabel>
            <div style={{ fontFamily: T.font.mono, fontSize: 12, color: T.textSec, lineHeight: 1.8, backgroundColor: T.bgAlt, padding: 16, borderRadius: 8 }}>
              Trigger: hover on Loma button (first 3 sessions only)<br />
              Position: above button, centered, with caret<br />
              Background: Espresso (#2C2825)<br />
              Dismiss: click anywhere, or after first rewrite<br />
              Storage: chrome.storage.local tooltip_shown = true<br />
              Entry: fade-up 200ms
            </div>
          </div>
        )}

        {active === "errors" && (
          <div>
            <SectionTitle>Error States</SectionTitle>
            <SectionDesc>All error messages in Vietnamese. Left-border accent for severity. Warning (amber) for recoverable, error (red) for failures.</SectionDesc>

            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <div><StateLabel>Offline</StateLabel><ErrorBanner type="offline" /></div>
              <div><StateLabel>Free Tier Exhausted</StateLabel><ErrorBanner type="rate_limit" /></div>
              <div><StateLabel>PAYG Balance Empty</StateLabel><ErrorBanner type="balance" /></div>
              <div><StateLabel>Server Error</StateLabel><ErrorBanner type="server" /></div>
            </div>

            <Divider />
            <StateLabel>Error in Result Card</StateLabel>
            <ResultCard state="error" />
          </div>
        )}

        {active === "popup" && (
          <div>
            <SectionTitle>Extension Popup</SectionTitle>
            <SectionDesc>320px wide. Opens via extension icon. Shows account tier, balance, usage stats, and per-site toggle. All Vietnamese.</SectionDesc>
            <PopupPreview />

            <Divider />
            <StateLabel>Specs</StateLabel>
            <div style={{ fontFamily: T.font.mono, fontSize: 12, color: T.textSec, lineHeight: 1.8, backgroundColor: T.bgAlt, padding: 16, borderRadius: 8 }}>
              Width: 320px (Chrome popup constraint)<br />
              Background: Cream Canvas (#F5F0E8)<br />
              Framework: React + Be Vietnam Pro<br />
              Data source: chrome.storage.local + API /user/status<br />
              Phase 2 addition: Rewrite history list below stats
            </div>
          </div>
        )}

        {active === "ftux" && (
          <div>
            <SectionTitle>First-Time User Experience</SectionTitle>
            <SectionDesc>Opens as a new tab after install. 3 steps: welcome → live demo → intent overview. Click "Tiếp tục" to step through.</SectionDesc>
            <FTUXPreview />

            <Divider />
            <StateLabel>Specs</StateLabel>
            <div style={{ fontFamily: T.font.mono, fontSize: 12, color: T.textSec, lineHeight: 1.8, backgroundColor: T.bgAlt, padding: 16, borderRadius: 8 }}>
              Trigger: chrome.runtime.onInstalled → chrome.tabs.create<br />
              URL: chrome-extension://[id]/ftux.html<br />
              Steps: 3 (welcome → demo → intents)<br />
              Demo: fake Gmail compose with pre-filled Vietnamese text<br />
              Exit: "Bắt đầu dùng Loma →" closes tab<br />
              Analytics: loma_ftux_started, loma_ftux_completed, loma_ftux_step_[n]
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
