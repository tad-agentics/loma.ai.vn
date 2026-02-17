/**
 * FTUX welcome page (UX Spec 5.1).
 * Google Sign-in via Supabase Auth using chrome.identity.launchWebAuthFlow.
 */
(function () {
  const isVi = typeof chrome !== 'undefined' && chrome.i18n && chrome.i18n.getUILanguage && chrome.i18n.getUILanguage().startsWith('vi');
  const t = function (key) {
    if (typeof chrome !== 'undefined' && chrome.i18n) return chrome.i18n.getMessage(key) || key;
    return key;
  };

  // i18n text
  document.getElementById('screen1').textContent = t('ftux_screen1');
  document.getElementById('screen2').textContent = t('ftux_screen2');
  document.getElementById('screen3').textContent = t('ftux_screen3');

  // CTA: close tab
  const cta = document.getElementById('cta');
  cta.textContent = isVi ? 'Bắt đầu dùng Loma' : 'Get started with Loma';
  cta.addEventListener('click', function (e) {
    e.preventDefault();
    if (typeof chrome !== 'undefined' && chrome.tabs) chrome.tabs.getCurrent((tab) => { if (tab && tab.id) chrome.tabs.remove(tab.id); });
    else window.close();
  });

  // Skip link: close tab without signing in
  const skipLink = document.getElementById('skip-link');
  if (skipLink) {
    skipLink.addEventListener('click', function (e) {
      e.preventDefault();
      if (typeof chrome !== 'undefined' && chrome.tabs) chrome.tabs.getCurrent((tab) => { if (tab && tab.id) chrome.tabs.remove(tab.id); });
      else window.close();
    });
  }

  // Google Sign-in
  const signinBtn = document.getElementById('google-signin-btn');
  const signedInEl = document.getElementById('signed-in');
  const userEmailEl = document.getElementById('user-email');

  /**
   * Get Supabase config from storage or use defaults.
   * In production, these should be set via the popup settings or env config.
   */
  function getSupabaseConfig(callback) {
    chrome.storage.local.get(['loma_supabase_url', 'loma_supabase_anon_key'], function (data) {
      callback({
        url: data.loma_supabase_url || '',
        anonKey: data.loma_supabase_anon_key || '',
      });
    });
  }

  /**
   * Google Sign-in via Supabase OAuth using chrome.identity.launchWebAuthFlow.
   *
   * Flow:
   * 1. Open Supabase OAuth URL in a popup via chrome.identity
   * 2. Supabase redirects to Google, user signs in
   * 3. Google redirects back to Supabase with auth code
   * 4. Supabase redirects to our redirect URL with access_token in hash
   * 5. We extract the token and store it
   */
  function signInWithGoogle() {
    getSupabaseConfig(function (config) {
      if (!config.url) {
        // Fallback: show a message that config is needed
        alert(isVi
          ? 'Cần cấu hình Supabase URL trong cài đặt extension. Liên hệ support@loma.app.'
          : 'Supabase URL not configured. Contact support@loma.app.');
        return;
      }

      const redirectUrl = chrome.identity.getRedirectURL();
      const supabaseAuthUrl = config.url + '/auth/v1/authorize'
        + '?provider=google'
        + '&redirect_to=' + encodeURIComponent(redirectUrl)
        + '&scopes=email%20profile';

      chrome.identity.launchWebAuthFlow(
        { url: supabaseAuthUrl, interactive: true },
        function (callbackUrl) {
          if (chrome.runtime.lastError || !callbackUrl) {
            console.error('Auth failed:', chrome.runtime.lastError);
            return;
          }

          // Extract tokens from the callback URL hash
          // Format: ...#access_token=...&refresh_token=...&token_type=bearer&...
          const hashParams = new URLSearchParams(
            callbackUrl.includes('#') ? callbackUrl.split('#')[1] : ''
          );
          const accessToken = hashParams.get('access_token');
          const refreshToken = hashParams.get('refresh_token');

          if (!accessToken) {
            console.error('No access token in callback URL');
            return;
          }

          // Decode JWT to extract user info (basic, no verification needed client-side)
          const payload = parseJwt(accessToken);
          const email = payload.email || '';
          const userId = payload.sub || '';

          // Store auth in extension storage
          chrome.runtime.sendMessage({
            type: 'SET_AUTH',
            token: accessToken,
            userId: userId,
            email: email,
          }, function () {
            // Also store refresh token for session persistence
            chrome.storage.local.set({
              loma_refresh_token: refreshToken || '',
            });

            // Update UI
            showSignedIn(email);
          });
        }
      );
    });
  }

  function parseJwt(token) {
    try {
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64).split('').map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join('')
      );
      return JSON.parse(jsonPayload);
    } catch (e) {
      return {};
    }
  }

  function showSignedIn(email) {
    if (signinBtn) signinBtn.style.display = 'none';
    if (skipLink) skipLink.style.display = 'none';
    if (signedInEl) {
      signedInEl.style.display = 'block';
      if (userEmailEl) userEmailEl.textContent = email;
    }
  }

  // Check if already signed in
  if (typeof chrome !== 'undefined' && chrome.runtime && chrome.runtime.sendMessage) {
    chrome.runtime.sendMessage({ type: 'GET_AUTH' }, function (response) {
      if (response && response.token && response.email) {
        showSignedIn(response.email);
      }
    });
  }

  // Attach click handler
  if (signinBtn) {
    signinBtn.addEventListener('click', signInWithGoogle);
  }
})();
