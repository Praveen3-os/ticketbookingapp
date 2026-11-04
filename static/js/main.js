/* ── Chat Widget JS ── */
(function () {
  'use strict';

  const toggle   = document.getElementById('chat-toggle');
  const chatBox  = document.getElementById('chat-box');
  const closeBtn = document.getElementById('chat-close');
  const messages = document.getElementById('chat-messages');
  const input    = document.getElementById('chat-input');
  const sendBtn  = document.getElementById('chat-send');

  if (!toggle) return;   // widget not on page

  // ── Open / close ───────────────────────────────────────────────────────
  toggle.addEventListener('click', () => {
    chatBox.classList.toggle('open');
    if (chatBox.classList.contains('open') && messages.children.length === 0) {
      appendBot(
        "👋 Hi! I'm TicketBot. Ask me anything about bookings, payments, error codes or events.",
        null
      );
    }
    if (chatBox.classList.contains('open')) input.focus();
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => chatBox.classList.remove('open'));
  }

  // ── Send message ────────────────────────────────────────────────────────
  function send() {
    const text = input.value.trim();
    if (!text) return;
    appendUser(text);
    input.value = '';
    showTyping();

    fetch('/assistant/chat/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ message: text }),
    })
      .then(r => r.json())
      .then(data => {
        removeTyping();
        if (data.error) {
          appendBot('⚠️ ' + data.error, null);
        } else {
          appendBot(data.reply, data.message_id, data.ticket_ref);
        }
      })
      .catch(() => {
        removeTyping();
        appendBot('⚠️ Sorry, something went wrong. Please try again.', null);
      });
  }

  sendBtn.addEventListener('click', send);
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  });

  // ── Append helpers ──────────────────────────────────────────────────────
  function appendUser(text) {
    const div = document.createElement('div');
    div.className = 'msg msg-user';
    div.textContent = text;
    messages.appendChild(div);
    scroll();
  }

  function appendBot(text, messageId, ticketRef) {
    const div = document.createElement('div');
    div.className = 'msg msg-bot';

    // Simple markdown-ish: **bold**
    const html = text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
    div.innerHTML = html;

    if (ticketRef) {
      const ref = document.createElement('div');
      ref.className = 'ticket-ref';
      ref.textContent = '🎫 Reference: ' + ticketRef;
      div.appendChild(ref);
    }

    if (messageId) {
      const fbRow = document.createElement('div');
      fbRow.className = 'feedback-row';
      fbRow.innerHTML = `
        <button class="fb-btn" data-mid="${messageId}" data-rating="up">👍</button>
        <button class="fb-btn" data-mid="${messageId}" data-rating="down">👎</button>
      `;
      fbRow.querySelectorAll('.fb-btn').forEach(btn => {
        btn.addEventListener('click', () => submitFeedback(btn.dataset.mid, btn.dataset.rating, btn));
      });
      div.appendChild(fbRow);
    }

    messages.appendChild(div);
    scroll();
  }

  let typingEl = null;
  function showTyping() {
    typingEl = document.createElement('div');
    typingEl.className = 'msg-typing';
    typingEl.textContent = 'TicketBot is typing…';
    messages.appendChild(typingEl);
    scroll();
  }
  function removeTyping() {
    if (typingEl) { typingEl.remove(); typingEl = null; }
  }

  function scroll() {
    messages.scrollTop = messages.scrollHeight;
  }

  // ── Feedback ────────────────────────────────────────────────────────────
  function submitFeedback(messageId, rating, btn) {
    fetch('/assistant/feedback/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ message_id: messageId, rating: rating }),
    }).catch(() => {});
    btn.parentElement.innerHTML = rating === 'up'
      ? '<span style="font-size:.8rem;color:#86efac">Thanks for the feedback! 🙌</span>'
      : '<span style="font-size:.8rem;color:#fca5a5">Thanks! We\'ll improve. 🙏</span>';
  }

  // ── Utility ─────────────────────────────────────────────────────────────
  function getCookie(name) {
    let v = null;
    document.cookie.split(';').forEach(c => {
      const [k, val] = c.trim().split('=');
      if (k === name) v = decodeURIComponent(val);
    });
    return v;
  }

  // ── FAQ accordion ────────────────────────────────────────────────────────
  document.querySelectorAll('.faq-question').forEach(btn => {
    btn.addEventListener('click', () => {
      const isOpen = btn.getAttribute('aria-expanded') === 'true';
      // close all
      document.querySelectorAll('.faq-question').forEach(b => {
        b.setAttribute('aria-expanded', 'false');
        b.nextElementSibling.classList.remove('open');
      });
      if (!isOpen) {
        btn.setAttribute('aria-expanded', 'true');
        btn.nextElementSibling.classList.add('open');
      }
    });
  });

  // ── Mobile nav ──────────────────────────────────────────────────────────
  const navToggle = document.getElementById('nav-toggle');
  const navLinks  = document.getElementById('nav-links');
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => navLinks.classList.toggle('open'));
  }

})();

