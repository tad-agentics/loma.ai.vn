import { useState } from "react";

const tokens = {
  colors: {
    background: { value: "#F5F0E8", name: "Cream Canvas", usage: "Primary background, page surface" },
    backgroundAlt: { value: "#EDE8DD", name: "Warm Stone", usage: "Cards, code blocks, elevated surfaces" },
    backgroundDark: { value: "#2C2825", name: "Espresso", usage: "Dark mode background, inverted sections" },
    text: { value: "#2C2825", name: "Charcoal", usage: "Primary body text, headings" },
    textSecondary: { value: "#6B6560", name: "Warm Gray", usage: "Secondary text, meta info, timestamps" },
    textMuted: { value: "#9C9590", name: "Stone", usage: "Disabled states, placeholder text" },
    textOnDark: { value: "#F5F0E8", name: "Cream on Dark", usage: "Text on dark backgrounds" },
    brand: { value: "#0D9488", name: "Loma Teal", usage: "Primary actions, brand accent, links" },
    brandHover: { value: "#0F766E", name: "Deep Teal", usage: "Hover states on brand elements" },
    brandSubtle: { value: "#CCFBF1", name: "Teal Mist", usage: "Badge backgrounds, light accent fills" },
    border: { value: "#D8D2C8", name: "Linen", usage: "Dividers, card borders, horizontal rules" },
    borderSubtle: { value: "#E8E2D8", name: "Pale Linen", usage: "Subtle separators, inner borders" },
    success: { value: "#10B981", name: "Mint", usage: "Success states, confirmation" },
    warning: { value: "#D97706", name: "Amber", usage: "Warning states, attention" },
    error: { value: "#DC2626", name: "Vermillion", usage: "Error states, destructive actions" },
  },
  typography: {
    display: { family: "'Newsreader', 'Georgia', serif", weight: 700, usage: "H1 headlines, hero text" },
    heading: { family: "'Newsreader', 'Georgia', serif", weight: 600, usage: "H2-H4, section headers" },
    body: { family: "'Source Serif 4', 'Georgia', serif", weight: 400, usage: "Body text, paragraphs" },
    mono: { family: "'JetBrains Mono', 'SF Mono', monospace", weight: 400, usage: "Code blocks, data, technical" },
    ui: { family: "'Be Vietnam Pro', 'Helvetica Neue', sans-serif", weight: 500, usage: "Buttons, labels, UI chrome — Vietnamese-optimized" },
  },
  scale: [
    { name: "xs", size: "0.75rem", px: "12px", leading: "1.5", usage: "Captions, footnotes" },
    { name: "sm", size: "0.875rem", px: "14px", leading: "1.5", usage: "Secondary text, meta" },
    { name: "base", size: "1rem", px: "16px", leading: "1.7", usage: "Body text" },
    { name: "lg", size: "1.125rem", px: "18px", leading: "1.7", usage: "Lead paragraphs" },
    { name: "xl", size: "1.25rem", px: "20px", leading: "1.5", usage: "H4, small headings" },
    { name: "2xl", size: "1.5rem", px: "24px", leading: "1.4", usage: "H3" },
    { name: "3xl", size: "1.875rem", px: "30px", leading: "1.3", usage: "H2" },
    { name: "4xl", size: "2.25rem", px: "36px", leading: "1.2", usage: "H1" },
    { name: "5xl", size: "3rem", px: "48px", leading: "1.1", usage: "Display, hero" },
  ],
  spacing: [
    { name: "2xs", value: "4px", rem: "0.25rem" },
    { name: "xs", value: "8px", rem: "0.5rem" },
    { name: "sm", value: "12px", rem: "0.75rem" },
    { name: "md", value: "16px", rem: "1rem" },
    { name: "lg", value: "24px", rem: "1.5rem" },
    { name: "xl", value: "32px", rem: "2rem" },
    { name: "2xl", value: "48px", rem: "3rem" },
    { name: "3xl", value: "64px", rem: "4rem" },
    { name: "4xl", value: "96px", rem: "6rem" },
  ],
  radius: [
    { name: "none", value: "0" },
    { name: "sm", value: "4px" },
    { name: "md", value: "8px" },
    { name: "lg", value: "12px" },
    { name: "full", value: "9999px" },
  ],
  shadows: [
    { name: "sm", value: "0 1px 3px rgba(44,40,37,0.06)", usage: "Subtle elevation" },
    { name: "md", value: "0 4px 12px rgba(44,40,37,0.08)", usage: "Cards, dropdowns" },
    { name: "lg", value: "0 8px 24px rgba(44,40,37,0.12)", usage: "Modals, floating panels" },
  ],
};

const sections = ["Overview", "Colors", "Typography", "Spacing", "Components"];

function Swatch({ color, name, value, usage }) {
  const [copied, setCopied] = useState(false);
  const isDark = value === "#2C2825";
  return (
    <div
      style={{ cursor: "pointer" }}
      onClick={() => { navigator.clipboard?.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 1200); }}
    >
      <div style={{
        width: "100%", height: 64, borderRadius: 8, backgroundColor: value,
        border: `1px solid ${tokens.colors.border.value}`,
        display: "flex", alignItems: "center", justifyContent: "center",
        transition: "transform 0.15s ease",
      }}>
        {copied && <span style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, color: isDark ? "#F5F0E8" : "#2C2825", letterSpacing: "0.05em", textTransform: "uppercase" }}>Copied</span>}
      </div>
      <div style={{ marginTop: 8 }}>
        <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: 600, color: tokens.colors.text.value }}>{name}</div>
        <div style={{ fontFamily: tokens.typography.mono.family, fontSize: 11, color: tokens.colors.textSecondary.value, marginTop: 2 }}>{value}</div>
        <div style={{ fontFamily: tokens.typography.body.family, fontSize: 12, color: tokens.colors.textMuted.value, marginTop: 2 }}>{usage}</div>
      </div>
    </div>
  );
}

function IntentBadge({ emoji, viLabel, enLabel, bg, textColor }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 6, padding: "4px 12px",
      borderRadius: 9999, backgroundColor: bg, fontFamily: tokens.typography.ui.family,
      fontSize: 13, color: textColor, fontWeight: 500,
    }}>
      <span>{emoji}</span>
      <span>{viLabel}</span>
      <span style={{ opacity: 0.5 }}>·</span>
      <span style={{ opacity: 0.7 }}>{enLabel}</span>
    </span>
  );
}

export default function DesignSystem() {
  const [activeSection, setActiveSection] = useState("Overview");

  const navStyle = (s) => ({
    fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: activeSection === s ? 600 : 400,
    color: activeSection === s ? tokens.colors.brand.value : tokens.colors.textSecondary.value,
    cursor: "pointer", padding: "6px 0",
    borderBottom: activeSection === s ? `2px solid ${tokens.colors.brand.value}` : "2px solid transparent",
    transition: "all 0.15s ease", letterSpacing: "0.01em",
  });

  return (
    <div style={{ minHeight: "100vh", backgroundColor: tokens.colors.background.value, color: tokens.colors.text.value }}>
      <link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,600;6..72,700&family=Source+Serif+4:opsz,wght@8..60,400;8..60,600&family=Be+Vietnam+Pro:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />

      {/* Header */}
      <div style={{ padding: "48px 48px 0", maxWidth: 960, margin: "0 auto" }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginBottom: 8 }}>
          <h1 style={{ fontFamily: tokens.typography.display.family, fontSize: 42, fontWeight: 700, margin: 0, letterSpacing: "-0.02em", lineHeight: 1.1, color: tokens.colors.text.value }}>
            Loma
          </h1>
          <span style={{ fontFamily: tokens.typography.ui.family, fontSize: 12, fontWeight: 500, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase" }}>
            Design System v1.1
          </span>
        </div>
        <p style={{ fontFamily: tokens.typography.body.family, fontSize: 17, color: tokens.colors.textSecondary.value, margin: "12px 0 32px", lineHeight: 1.6, maxWidth: 560 }}>
          Editorial warmth. Serif-led typography. Vietnamese-optimized UI font. Cream canvas. Built for a product that speaks Vietnamese and writes English.
        </p>

        {/* Nav */}
        <div style={{ display: "flex", gap: 24, borderBottom: `1px solid ${tokens.colors.border.value}`, paddingBottom: 0 }}>
          {sections.map(s => (
            <div key={s} style={navStyle(s)} onClick={() => setActiveSection(s)}>{s}</div>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ padding: "40px 48px 80px", maxWidth: 960, margin: "0 auto" }}>

        {activeSection === "Overview" && (
          <div>
            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 24px", letterSpacing: "-0.01em" }}>Design Principles</h2>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 48 }}>
              {[
                { title: "Editorial, Not Corporate", body: "Loma's aesthetic draws from literary publishing — warm paper tones, serif typography, generous leading. The interface should feel like reading a well-typeset document, not using enterprise software." },
                { title: "Vietnamese First, English Output", body: "Every label, button, and message the user sees is in Vietnamese by default. The only English in the UI is the rewrite output itself. The design must feel native to Vietnamese professionals, not translated." },
                { title: "One Surface, Full Attention", body: "The result card is the entire product. No sidebar, no toolbar, no ambient widgets. When Loma speaks, it has the user's complete attention. The card earns this with warmth and clarity." },
                { title: "Quiet Confidence", body: "No exclamation marks in UI copy. No celebration animations. No gamification. The product exudes the same confident professionalism it produces in the user's English. Calm, direct, trustworthy." },
              ].map((p, i) => (
                <div key={i} style={{ padding: 24, backgroundColor: tokens.colors.backgroundAlt.value, borderRadius: 12, border: `1px solid ${tokens.colors.borderSubtle.value}` }}>
                  <h3 style={{ fontFamily: tokens.typography.heading.family, fontSize: 18, fontWeight: 600, margin: "0 0 8px", color: tokens.colors.text.value }}>{p.title}</h3>
                  <p style={{ fontFamily: tokens.typography.body.family, fontSize: 14, color: tokens.colors.textSecondary.value, margin: 0, lineHeight: 1.65 }}>{p.body}</p>
                </div>
              ))}
            </div>

            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 16px" }}>Aesthetic Direction</h2>
            <div style={{ padding: 32, backgroundColor: tokens.colors.backgroundAlt.value, borderRadius: 12, border: `1px solid ${tokens.colors.borderSubtle.value}`, marginBottom: 48 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 32 }}>
                <div>
                  <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>Tone</div>
                  <div style={{ fontFamily: tokens.typography.body.family, fontSize: 15, color: tokens.colors.text.value, lineHeight: 1.6 }}>Warm editorial minimalism. Literary, not techy. Think Monocle magazine, not Material Design.</div>
                </div>
                <div>
                  <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>Canvas</div>
                  <div style={{ fontFamily: tokens.typography.body.family, fontSize: 15, color: tokens.colors.text.value, lineHeight: 1.6 }}>Cream paper, not white screens. Every surface has warmth. Borders are linen-colored, not gray. Shadows are brown-tinted.</div>
                </div>
                <div>
                  <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 8 }}>Motion</div>
                  <div style={{ fontFamily: tokens.typography.body.family, fontSize: 15, color: tokens.colors.text.value, lineHeight: 1.6 }}>Restrained. 150-200ms ease-out transitions. No bouncing, no spring physics. Content fades in and slides up gently.</div>
                </div>
              </div>
            </div>

            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 16px" }}>Font Stack</h2>
            <div style={{ display: "grid", gap: 16, marginBottom: 48 }}>
              {Object.entries(tokens.typography).map(([key, t]) => (
                <div key={key} style={{ display: "flex", alignItems: "baseline", gap: 16, padding: "16px 0", borderBottom: `1px solid ${tokens.colors.borderSubtle.value}` }}>
                  <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", width: 72, flexShrink: 0 }}>{key}</div>
                  <div style={{ fontFamily: t.family, fontSize: key === "display" ? 28 : key === "mono" ? 15 : 20, fontWeight: t.weight, color: tokens.colors.text.value, flex: 1 }}>
                    {key === "display" ? "Newsreader 700" : key === "heading" ? "Newsreader 600" : key === "body" ? "Source Serif 4" : key === "mono" ? "JetBrains Mono 400" : "Be Vietnam Pro 500"}
                  </div>
                  <div style={{ fontFamily: tokens.typography.body.family, fontSize: 13, color: tokens.colors.textMuted.value, flexShrink: 0 }}>{t.usage}</div>
                </div>
              ))}
            </div>

            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 16px" }}>Vietnamese Diacritic Test</h2>
            <p style={{ fontFamily: tokens.typography.body.family, fontSize: 14, color: tokens.colors.textSecondary.value, margin: "0 0 16px", lineHeight: 1.6 }}>
              Stacked diacritics (ặ ệ ộ ử) and the stroke-d (đ) are the hardest characters. Every font in the stack must render these without clipping or misalignment.
            </p>
            <div style={{ display: "grid", gap: 0, marginBottom: 48 }}>
              {Object.entries(tokens.typography).map(([key, t]) => (
                <div key={key + "-vi"} style={{ display: "flex", alignItems: "baseline", gap: 16, padding: "14px 0", borderBottom: `1px solid ${tokens.colors.borderSubtle.value}` }}>
                  <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", width: 72, flexShrink: 0 }}>{key}</div>
                  <div style={{ fontFamily: t.family, fontSize: key === "display" ? 26 : key === "mono" ? 15 : 18, fontWeight: t.weight, color: tokens.colors.text.value, flex: 1, lineHeight: 1.6 }}>
                    Đặng Thị Ngọc Huyền — ăắằẳẵặ âấầẩẫậ đ êếềểễệ ôốồổỗộ ơớờởỡợ ưứừửữự
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === "Colors" && (
          <div>
            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 8px" }}>Color Palette</h2>
            <p style={{ fontFamily: tokens.typography.body.family, fontSize: 15, color: tokens.colors.textSecondary.value, margin: "0 0 32px", lineHeight: 1.6 }}>
              Warm neutrals inspired by aged paper and natural materials. A single teal accent for brand and interactive elements. Click any swatch to copy its hex value.
            </p>

            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 12 }}>Surfaces</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
              {["background", "backgroundAlt", "backgroundDark", "border"].map(k => (
                <Swatch key={k} color={k} {...tokens.colors[k]} />
              ))}
            </div>

            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 12 }}>Text</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
              {["text", "textSecondary", "textMuted", "textOnDark"].map(k => (
                <Swatch key={k} color={k} {...tokens.colors[k]} />
              ))}
            </div>

            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 12 }}>Brand</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
              {["brand", "brandHover", "brandSubtle"].map(k => (
                <Swatch key={k} color={k} {...tokens.colors[k]} />
              ))}
            </div>

            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 12 }}>Semantic</div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 32 }}>
              {["success", "warning", "error"].map(k => (
                <Swatch key={k} color={k} {...tokens.colors[k]} />
              ))}
            </div>

            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 12 }}>Intent Badge Colors</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 16 }}>
              <IntentBadge emoji="💰" viLabel="Nhắc thanh toán" enLabel="Payment" bg="#D1FAE5" textColor="#065F46" />
              <IntentBadge emoji="📋" viLabel="Yêu cầu" enLabel="Request" bg="#DBEAFE" textColor="#1E40AF" />
              <IntentBadge emoji="🔄" viLabel="Theo dõi" enLabel="Follow up" bg="#FEF3C7" textColor="#92400E" />
              <IntentBadge emoji="🚫" viLabel="Từ chối" enLabel="Decline" bg="#FEE2E2" textColor="#991B1B" />
              <IntentBadge emoji="🤝" viLabel="Giới thiệu" enLabel="Outreach" bg="#E0E7FF" textColor="#3730A3" />
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
              <IntentBadge emoji="💬" viLabel="Góp ý" enLabel="Feedback" bg="#FCE7F3" textColor="#9D174D" />
              <IntentBadge emoji="⚡" viLabel="Không đồng ý" enLabel="Disagree" bg="#FFF7ED" textColor="#9A3412" />
              <IntentBadge emoji="🔺" viLabel="Chuyển cấp trên" enLabel="Escalate" bg="#FEF2F2" textColor="#7F1D1D" />
              <IntentBadge emoji="🙏" viLabel="Xin lỗi" enLabel="Apologize" bg="#F0FDF4" textColor="#166534" />
              <IntentBadge emoji="🤖" viLabel="Prompt AI" enLabel="AI prompt" bg="#F5F3FF" textColor="#5B21B6" />
            </div>
          </div>
        )}

        {activeSection === "Typography" && (
          <div>
            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 8px" }}>Type Scale</h2>
            <p style={{ fontFamily: tokens.typography.body.family, fontSize: 15, color: tokens.colors.textSecondary.value, margin: "0 0 32px", lineHeight: 1.6 }}>
              A nine-step scale from 12px to 48px. Headings use Newsreader (serif, editorial). Body uses Source Serif 4 (optimized for screen reading). UI elements use Be Vietnam Pro (designed by Vietnamese typographers — perfect diacritic spacing for ặ, ệ, ộ, ử).
            </p>

            <div style={{ display: "grid", gap: 0, marginBottom: 48 }}>
              {tokens.scale.map((s, i) => (
                <div key={s.name} style={{ display: "flex", alignItems: "baseline", gap: 16, padding: "16px 0", borderBottom: `1px solid ${tokens.colors.borderSubtle.value}` }}>
                  <div style={{ fontFamily: tokens.typography.mono.family, fontSize: 12, color: tokens.colors.textMuted.value, width: 40, flexShrink: 0 }}>{s.name}</div>
                  <div style={{ fontFamily: tokens.typography.mono.family, fontSize: 12, color: tokens.colors.textSecondary.value, width: 72, flexShrink: 0 }}>{s.size}</div>
                  <div style={{
                    fontFamily: i >= 6 ? tokens.typography.heading.family : tokens.typography.body.family,
                    fontSize: s.size, fontWeight: i >= 6 ? 600 : 400,
                    color: tokens.colors.text.value, flex: 1, lineHeight: s.leading,
                  }}>
                    {i >= 7 ? "Viết tiếng Việt" : i >= 5 ? "Your ideas deserve better English" : "The quick brown fox jumps over the lazy dog"}
                  </div>
                  <div style={{ fontFamily: tokens.typography.body.family, fontSize: 12, color: tokens.colors.textMuted.value, flexShrink: 0, width: 120, textAlign: "right" }}>{s.usage}</div>
                </div>
              ))}
            </div>

            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 16px" }}>Specimen</h2>
            <div style={{ padding: 32, backgroundColor: tokens.colors.backgroundAlt.value, borderRadius: 12, border: `1px solid ${tokens.colors.borderSubtle.value}`, maxWidth: 640 }}>
              <h1 style={{ fontFamily: tokens.typography.display.family, fontSize: "2.25rem", fontWeight: 700, margin: "0 0 8px", letterSpacing: "-0.02em", lineHeight: 1.2 }}>Loma</h1>
              <p style={{ fontFamily: tokens.typography.body.family, fontSize: 17, fontWeight: 600, color: tokens.colors.text.value, margin: "0 0 20px", lineHeight: 1.4 }}>Write in Vietnamese. Sound like a native English speaker.</p>
              <div style={{ height: 1, backgroundColor: tokens.colors.border.value, margin: "0 0 24px" }} />
              <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: "1.5rem", fontWeight: 600, margin: "0 0 12px", lineHeight: 1.3 }}>What Loma Does</h2>
              <p style={{ fontFamily: tokens.typography.body.family, fontSize: "1rem", color: tokens.colors.text.value, margin: "0 0 16px", lineHeight: 1.7 }}>
                Loma is a Chrome extension that transforms Vietnamese thoughts into professional English — inside any text field, in under 2 seconds, with one tap.
              </p>
              <p style={{ fontFamily: tokens.typography.body.family, fontSize: "1rem", color: tokens.colors.text.value, margin: "0 0 20px", lineHeight: 1.7 }}>
                Not a grammar checker. Not a translator. A <strong>thinking-to-English bridge</strong> that understands what you're trying to accomplish and writes accordingly.
              </p>
              <div style={{ padding: "16px 20px", backgroundColor: tokens.colors.background.value, borderRadius: 8, fontFamily: tokens.typography.mono.family, fontSize: 13.5, lineHeight: 1.7, color: tokens.colors.text.value }}>
                <div style={{ color: tokens.colors.textSecondary.value, marginBottom: 12 }}>You type: <span style={{ color: tokens.colors.text.value }}>"anh Minh ơi, cái invoice tháng 1 chưa thanh toán"</span></div>
                <div style={{ color: tokens.colors.textSecondary.value }}>Loma: <span style={{ color: tokens.colors.text.value }}>"Hi Minh, following up on VinAI's January invoice — now 2 weeks overdue."</span></div>
              </div>
            </div>
          </div>
        )}

        {activeSection === "Spacing" && (
          <div>
            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 8px" }}>Spacing Scale</h2>
            <p style={{ fontFamily: tokens.typography.body.family, fontSize: 15, color: tokens.colors.textSecondary.value, margin: "0 0 32px", lineHeight: 1.6 }}>
              Base-8 spacing system. Generous whitespace is central to the editorial aesthetic — err on the side of more space, not less.
            </p>

            <div style={{ display: "grid", gap: 0, marginBottom: 48 }}>
              {tokens.spacing.map(s => (
                <div key={s.name} style={{ display: "flex", alignItems: "center", gap: 16, padding: "12px 0", borderBottom: `1px solid ${tokens.colors.borderSubtle.value}` }}>
                  <div style={{ fontFamily: tokens.typography.mono.family, fontSize: 12, color: tokens.colors.textMuted.value, width: 40 }}>{s.name}</div>
                  <div style={{ fontFamily: tokens.typography.mono.family, fontSize: 12, color: tokens.colors.textSecondary.value, width: 56 }}>{s.value}</div>
                  <div style={{ width: s.value, height: 16, backgroundColor: tokens.colors.brand.value, borderRadius: 3, opacity: 0.6, transition: "width 0.2s ease" }} />
                </div>
              ))}
            </div>

            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 16px" }}>Border Radius</h2>
            <div style={{ display: "flex", gap: 24, marginBottom: 48 }}>
              {tokens.radius.map(r => (
                <div key={r.name} style={{ textAlign: "center" }}>
                  <div style={{ width: 56, height: 56, backgroundColor: tokens.colors.backgroundAlt.value, border: `2px solid ${tokens.colors.brand.value}`, borderRadius: r.value, margin: "0 auto 8px" }} />
                  <div style={{ fontFamily: tokens.typography.mono.family, fontSize: 11, color: tokens.colors.textSecondary.value }}>{r.name}</div>
                  <div style={{ fontFamily: tokens.typography.mono.family, fontSize: 10, color: tokens.colors.textMuted.value }}>{r.value}</div>
                </div>
              ))}
            </div>

            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 16px" }}>Shadows</h2>
            <div style={{ display: "flex", gap: 24 }}>
              {tokens.shadows.map(s => (
                <div key={s.name} style={{ width: 120, height: 80, backgroundColor: tokens.colors.background.value, borderRadius: 12, boxShadow: s.value, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                  <div style={{ fontFamily: tokens.typography.mono.family, fontSize: 12, color: tokens.colors.textSecondary.value }}>{s.name}</div>
                  <div style={{ fontFamily: tokens.typography.body.family, fontSize: 11, color: tokens.colors.textMuted.value, marginTop: 4 }}>{s.usage}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeSection === "Components" && (
          <div>
            <h2 style={{ fontFamily: tokens.typography.heading.family, fontSize: 28, fontWeight: 600, margin: "0 0 8px" }}>Core Components</h2>
            <p style={{ fontFamily: tokens.typography.body.family, fontSize: 15, color: tokens.colors.textSecondary.value, margin: "0 0 32px", lineHeight: 1.6 }}>
              The essential building blocks of Loma's interface. All components use Vietnamese labels by default.
            </p>

            {/* Buttons */}
            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 16 }}>Buttons</div>
            <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 32, flexWrap: "wrap" }}>
              <button style={{ fontFamily: tokens.typography.ui.family, fontSize: 14, fontWeight: 600, padding: "10px 20px", borderRadius: 8, border: "none", backgroundColor: tokens.colors.brand.value, color: "#fff", cursor: "pointer", letterSpacing: "0.01em" }}>✓ Dùng</button>
              <button style={{ fontFamily: tokens.typography.ui.family, fontSize: 14, fontWeight: 500, padding: "10px 20px", borderRadius: 8, border: `1.5px solid ${tokens.colors.border.value}`, backgroundColor: "transparent", color: tokens.colors.text.value, cursor: "pointer" }}>📋 Sao chép</button>
              <button style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: 500, padding: "8px 16px", borderRadius: 8, border: "none", backgroundColor: "transparent", color: tokens.colors.brand.value, cursor: "pointer", textDecoration: "underline", textUnderlineOffset: 3 }}>↻ Đổi giọng</button>
              <button style={{ fontFamily: tokens.typography.ui.family, fontSize: 14, fontWeight: 600, padding: "10px 20px", borderRadius: 8, border: "none", backgroundColor: tokens.colors.brand.value, color: "#fff", cursor: "pointer", opacity: 0.5 }}>Disabled</button>
            </div>

            {/* Tone pills */}
            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 16 }}>Tone Selector</div>
            <div style={{ display: "flex", gap: 8, marginBottom: 32 }}>
              {["Trực tiếp hơn", "Nhẹ nhàng hơn", "Ngắn gọn hơn", "Trang trọng hơn"].map((t, i) => (
                <span key={t} style={{
                  fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: 500,
                  padding: "6px 14px", borderRadius: 9999,
                  backgroundColor: i === 0 ? tokens.colors.brand.value : tokens.colors.backgroundAlt.value,
                  color: i === 0 ? "#fff" : tokens.colors.text.value,
                  border: i === 0 ? "none" : `1px solid ${tokens.colors.border.value}`,
                  cursor: "pointer",
                }}>{t}</span>
              ))}
            </div>

            {/* Result Card */}
            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 16 }}>Result Card</div>
            <div style={{
              width: 420, backgroundColor: "#fff", borderRadius: 12, border: `1px solid ${tokens.colors.border.value}`,
              boxShadow: tokens.shadows[2].value, overflow: "hidden", marginBottom: 32,
            }}>
              <div style={{ padding: "16px 20px 12px", borderBottom: `1px solid ${tokens.colors.borderSubtle.value}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <IntentBadge emoji="🎯" viLabel="Nhắc thanh toán" enLabel="Payment follow-up" bg="#D1FAE5" textColor="#065F46" />
                <span style={{ fontFamily: tokens.typography.ui.family, fontSize: 16, color: tokens.colors.textMuted.value, cursor: "pointer", lineHeight: 1 }}>✕</span>
              </div>
              <div style={{ padding: "12px 20px 4px" }}>
                <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, color: tokens.colors.brand.value, cursor: "pointer", marginBottom: 12 }}>▸ Xem bản gốc</div>
                <p style={{ fontFamily: tokens.typography.body.family, fontSize: 14, color: tokens.colors.text.value, margin: "0 0 12px", lineHeight: 1.7 }}>
                  Hi Minh, following up on VinAI's January invoice for $5,000 — now 2 weeks overdue. Could you confirm the expected payment date by Friday?
                </p>
              </div>
              <div style={{ padding: "0 20px 12px", borderBottom: `1px solid ${tokens.colors.borderSubtle.value}` }}>
                <span style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, color: tokens.colors.textSecondary.value }}>✂️ Ngắn hơn 52%</span>
              </div>
              <div style={{ padding: "12px 20px 16px", display: "flex", gap: 8 }}>
                <button style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: 600, padding: "8px 16px", borderRadius: 8, border: "none", backgroundColor: tokens.colors.brand.value, color: "#fff", cursor: "pointer", flex: 1 }}>✓ Dùng</button>
                <button style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: 500, padding: "8px 16px", borderRadius: 8, border: `1.5px solid ${tokens.colors.border.value}`, backgroundColor: "transparent", color: tokens.colors.text.value, cursor: "pointer", flex: 1 }}>📋 Sao chép</button>
                <button style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: 500, padding: "8px 16px", borderRadius: 8, border: "none", backgroundColor: "transparent", color: tokens.colors.brand.value, cursor: "pointer" }}>↻ Đổi giọng</button>
              </div>
            </div>

            {/* Undo Toast */}
            <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 16 }}>Undo Toast</div>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 12, padding: "10px 20px",
              backgroundColor: tokens.colors.backgroundDark.value, borderRadius: 8,
              boxShadow: tokens.shadows[1].value, marginBottom: 32,
            }}>
              <span style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, color: tokens.colors.textOnDark.value }}>✓ Đã thay văn bản</span>
              <span style={{ fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: 600, color: tokens.colors.brandSubtle.value, cursor: "pointer", textDecoration: "underline", textUnderlineOffset: 3 }}>Hoàn tác</span>
            </div>

            {/* Quick Pick */}
            <div style={{ display: "block" }}>
              <div style={{ fontFamily: tokens.typography.ui.family, fontSize: 11, fontWeight: 600, color: tokens.colors.textMuted.value, letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 16 }}>Quick Pick Card</div>
              <div style={{
                width: 420, backgroundColor: "#fff", borderRadius: 12, border: `1px solid ${tokens.colors.border.value}`,
                boxShadow: tokens.shadows[2].value, padding: "20px",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                  <span style={{ fontFamily: tokens.typography.heading.family, fontSize: 16, fontWeight: 600, color: tokens.colors.text.value }}>Bạn muốn làm gì?</span>
                  <span style={{ fontFamily: tokens.typography.ui.family, fontSize: 16, color: tokens.colors.textMuted.value, cursor: "pointer" }}>✕</span>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                  {[
                    { emoji: "💰", label: "Nhắc thanh toán" },
                    { emoji: "🔄", label: "Theo dõi" },
                    { emoji: "🚫", label: "Từ chối" },
                    { emoji: "···", label: "Khác..." },
                  ].map((item, i) => (
                    <div key={i} style={{
                      padding: "10px 14px", borderRadius: 8,
                      border: `1.5px solid ${tokens.colors.border.value}`,
                      fontFamily: tokens.typography.ui.family, fontSize: 13, fontWeight: 500,
                      color: tokens.colors.text.value, cursor: "pointer",
                      display: "flex", alignItems: "center", gap: 8,
                      backgroundColor: i === 3 ? tokens.colors.backgroundAlt.value : "transparent",
                    }}>
                      <span>{item.emoji}</span>
                      <span>{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
