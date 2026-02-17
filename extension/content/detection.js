/**
 * Vietnamese detection and language mix (Tech Spec 3.1).
 * Loma button appears only when containsVietnamese(text) is true.
 *
 * Improvements over v1:
 * - Romanized Vietnamese detection (no diacritics): common bigrams
 *   that are unambiguously Vietnamese even without diacritics.
 */
const VI_CHARS = /[ăắằẳẵặâấầẩẫậđêếềểễệôốồổỗộơớờởỡợưứừửữự]/i;
const VI_FUNCTION_WORDS = /\b(ơi|ạ|nhé|nha|đã|đang|sẽ|chưa|rồi|cái|của|cho|với|được|không|này|đó|thì|mà|là|và|hay|hoặc|nhưng|nếu|vì|để)\b/i;

// Romanized Vietnamese bigrams — unambiguously Vietnamese even without diacritics
const VI_ROMANIZED_BIGRAMS = /\b(anh oi|chi oi|em oi|xin chao|cam on|xin loi|duoc khong|chua duoc|khong duoc|nhu the|nhu vay|tai sao|the nao|lam sao|bao nhieu|thanh toan|hoa don|bao cao|de xuat|dong y|gioi thieu|hop tac|phan tich|danh gia|xin phep|gui anh|gui chi|nho anh|nho chi|vang a|cam on anh|cam on chi|mong anh|mong chi)\b/i;

// Single romanized words — need ≥3 to trigger (avoid false positives)
const VI_ROMANIZED_WORDS = /\b(khong|chua|duoc|nhung|hoac|vay|gui|xin|moi)\b/gi;

function containsVietnamese(text) {
  if (!text || text.length < 10) return false;
  // Check 1: Vietnamese diacritics
  const viCharMatches = (text.match(VI_CHARS) || []).length;
  if (viCharMatches >= 3) return true;
  // Check 2: Vietnamese function words with diacritics
  const viWordMatches = (text.match(new RegExp(VI_FUNCTION_WORDS.source, 'gi')) || []).length;
  if (viWordMatches >= 2) return true;
  // Check 3: Romanized Vietnamese bigrams (no diacritics)
  if (VI_ROMANIZED_BIGRAMS.test(text)) return true;
  // Check 4: Multiple romanized single words
  const romanizedMatches = (text.match(VI_ROMANIZED_WORDS) || []).length;
  if (romanizedMatches >= 3) return true;
  return false;
}

function computeLanguageMix(text) {
  const words = text.split(/\s+/).filter(w => w.length > 1);
  const total = words.length;
  if (total === 0) return { vi_ratio: 0, en_ratio: 0 };
  let viCount = 0;
  for (const word of words) {
    if (VI_CHARS.test(word) || VI_FUNCTION_WORDS.test(word)) viCount++;
  }
  const vi_ratio = Math.round((viCount / total) * 100) / 100;
  const en_ratio = Math.round(((total - viCount) / total) * 100) / 100;
  return { vi_ratio, en_ratio };
}

/**
 * Detect if Grammarly is present so we can offset the Loma button (UX Spec 3.2).
 */
function detectGrammarly(textField) {
  if (!textField) return false;
  const parent = textField.closest && textField.closest('[data-gramm]') || textField.parentElement;
  const grammarlyEl = document.querySelector && document.querySelector('grammarly-extension, grammarly-desktop-integration');
  const hasGrammAttr = textField.hasAttribute && (textField.hasAttribute('data-gramm') || textField.hasAttribute('data-gramm_editor'));
  const nearbyBtn = parent && parent.querySelector && parent.querySelector('[class*="grammarly"], grammarly-btn');
  return !!(grammarlyEl || hasGrammAttr || nearbyBtn);
}

function getPlatform() {
  const host = window.location.hostname;
  if (host.includes('mail.google.com')) return 'gmail';
  if (host.includes('app.slack.com')) return 'slack';
  if (host.includes('github.com')) return 'github';
  if (host.includes('chat.openai.com')) return 'chatgpt';
  if (host.includes('claude.ai')) return 'claude';
  if (host.includes('linkedin.com')) return 'linkedin';
  return 'generic';
}

const DOMAIN_OUTPUT_LANG_KEY = 'domain_output_lang';

/**
 * Output language for rewrite (Tech Spec v1.5, UX 2.6).
 * Calls cb('en' | 'vi_casual' | 'vi_formal' | 'vi_admin'). Reads per-domain preference from chrome.storage.local first.
 */
function getOutputLanguage(cb) {
  const host = (window.location.hostname || '').toLowerCase();
  if (typeof chrome !== 'undefined' && chrome.storage && chrome.storage.local) {
    chrome.storage.local.get([DOMAIN_OUTPUT_LANG_KEY], function (data) {
      const map = data[DOMAIN_OUTPUT_LANG_KEY] || {};
      const stored = map[host];
      if (stored) {
        cb(stored);
        return;
      }
      if (host.endsWith('.gov.vn')) {
        cb('vi_admin');
        return;
      }
      cb('en');
    });
  } else {
    cb(host.endsWith('.gov.vn') ? 'vi_admin' : 'en');
  }
}

/**
 * Store output language for current domain (UX 2.6 recovery path). Call when user picks [English] or [Tiếng Việt] in tone selector.
 */
function setOutputLanguageForDomain(outputLanguage) {
  const host = (window.location.hostname || '').toLowerCase();
  if (typeof chrome === 'undefined' || !chrome.storage || !chrome.storage.local) return;
  chrome.storage.local.get([DOMAIN_OUTPUT_LANG_KEY], function (data) {
    const map = data[DOMAIN_OUTPUT_LANG_KEY] || {};
    map[host] = outputLanguage;
    chrome.storage.local.set({ [DOMAIN_OUTPUT_LANG_KEY]: map });
  });
}
