/**
 * Text isolation — extract user-written segment (UX Spec 2.2).
 * Gmail: remove .gmail_quote, .gmail_signature; then heuristic for "-- ".
 * Generic: heuristic boundaries (On ... wrote:, >, --, etc.) or full field.
 */
(function () {
  function heuristicBoundary(text) {
    if (!text || !text.trim()) return { userText: '', method: 'full_field' };
    const lines = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
    let boundaryAt = null;
    for (let i = 0; i < lines.length; i++) {
      const stripped = lines[i].trim();
      if (stripped.startsWith('>')) {
        boundaryAt = i;
        break;
      }
      if (/^On\s+.+wrote\s*:$/i.test(stripped)) {
        boundaryAt = i;
        break;
      }
      if (stripped.indexOf('forwarded message') !== -1 && stripped.indexOf('----------') !== -1) {
        boundaryAt = i;
        break;
      }
      if (/^From:\s+/.test(stripped)) {
        boundaryAt = i;
        break;
      }
      if (stripped === '---' || stripped === '--' || /^--\s*$/.test(stripped)) {
        boundaryAt = i;
        break;
      }
      if (/^(Best regards|Sincerely|Thanks|Regards|Cheers),?\s*$/i.test(stripped)) {
        boundaryAt = i;
        break;
      }
    }
    if (boundaryAt !== null && boundaryAt > 0) {
      const userLines = lines.slice(0, boundaryAt);
      return { userText: userLines.join('\n').trim(), method: 'heuristic_boundary' };
    }
    const sigIdx = text.indexOf('\n-- \n');
    if (sigIdx > 0) return { userText: text.substring(0, sigIdx).trim(), method: 'heuristic_boundary' };
    if (text.indexOf('\n--\n') > 0) return { userText: text.substring(0, text.indexOf('\n--\n')).trim(), method: 'heuristic_boundary' };
    return { userText: text.trim(), method: 'full_field' };
  }

  /**
   * Extract user-written text from a field (textarea, input, or contenteditable).
   * On Gmail, removes .gmail_quote and .gmail_signature from a clone, then applies heuristic.
   * @param {Element} el - The field element
   * @param {boolean} isGmail - Whether we're on mail.google.com
   * @returns {{ userText: string, method: string }}
   */
  function extractUserTextFromElement(el, isGmail) {
    const tag = (el.tagName || '').toLowerCase();
    if (tag === 'textarea' || tag === 'input') {
      const full = (el.value || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      return heuristicBoundary(full);
    }
    if (el.contentEditable === 'true' || el.isContentEditable) {
      let full;
      if (isGmail) {
        const clone = el.cloneNode(true);
        clone.querySelectorAll('.gmail_quote, blockquote, .gmail_signature').forEach(function (n) { n.remove(); });
        full = (clone.textContent || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      } else {
        full = (el.innerText || el.textContent || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      }
      return heuristicBoundary(full);
    }
    return { userText: '', method: 'full_field' };
  }

  /**
   * Replace content with new text. For Gmail contenteditable, replace only the user portion
   * (before .gmail_quote / .gmail_signature) so signature and quote are preserved.
   */
  function replaceUserText(el, newText, isGmail) {
    const tag = (el.tagName || '').toLowerCase();
    if (tag === 'textarea' || tag === 'input') {
      el.value = newText;
      el.dispatchEvent(new Event('input', { bubbles: true }));
      return;
    }
    if (el.contentEditable === 'true' || el.isContentEditable) {
      if (!isGmail) {
        el.innerText = newText;
        el.dispatchEvent(new Event('input', { bubbles: true }));
        return;
      }
      const quote = el.querySelector('.gmail_quote');
      const sig = el.querySelector('.gmail_signature');
      const boundary = quote || sig;
      if (boundary) {
        const userNodes = [];
        let sibling = el.firstChild;
        while (sibling) {
          if (sibling === boundary) break;
          userNodes.push(sibling);
          sibling = sibling.nextSibling;
        }
        userNodes.forEach(function (n) { n.remove(); });
        const wrap = document.createElement('div');
        wrap.innerHTML = newText.split('\n').join('<br>');
        el.insertBefore(wrap, boundary);
      } else {
        el.innerText = newText;
      }
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }

  window.LomaTextIsolation = {
    extractUserTextFromElement,
    replaceUserText,
  };
})();
