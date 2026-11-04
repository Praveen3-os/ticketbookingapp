/* ── CineBot Chat Widget JS with Instant Payment ── */
(function () {
  'use strict';

  const toggle   = document.getElementById('chat-toggle');
  const chatBox  = document.getElementById('chat-box');
  const closeBtn = document.getElementById('chat-close');
  const messages = document.getElementById('chat-messages');
  const input    = document.getElementById('chat-input');
  const sendBtn  = document.getElementById('chat-send');

  if (!toggle) return;

  // ── Open / close ───────────────────────────────────────────────────────
  toggle.addEventListener('click', () => {
    chatBox.classList.toggle('open');
    if (chatBox.classList.contains('open') && messages.children.length === 0) {
      appendBot(
        "👋 Vanakkam! I'm **CineBot**, your Tamil movie assistant.\n\n" +
        "You can ask me about **movies, show timings, Coimbatore theaters, error codes**, or even **book tickets and pay directly inside this chat!**",
        null,
        null,
        true // offer payment action
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
          appendBot(data.reply, data.message_id, data.ticket_ref, data.show_payment_action);
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

  function appendBot(text, messageId, ticketRef, showPaymentAction) {
    const div = document.createElement('div');
    div.className = 'msg msg-bot';

    const html = text
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br>');
    div.innerHTML = html;

    if (ticketRef) {
      const ref = document.createElement('div');
      ref.className = 'ticket-ref';
      ref.innerHTML = '🎫 <strong>Support Ticket:</strong> ' + ticketRef;
      div.appendChild(ref);
    }

    // In-Chat Payment Action Card
    if (showPaymentAction) {
      const payBox = document.createElement('div');
      payBox.style.cssText = 'margin-top:10px;padding:10px;background:#1e293b;border:1px solid #475569;border-radius:8px;font-size:0.82rem;';
      payBox.innerHTML = `
        <div style="font-weight:700;color:#6366f1;margin-bottom:6px">⚡ Instant Book & Pay in Chat</div>
        <div style="margin-bottom:6px">
          <label style="font-size:0.75rem;color:#94a3b8">Movie:</label>
          <select id="chatMovieSelect" style="width:100%;padding:4px;background:#0f172a;color:#fff;border:1px solid #334155;border-radius:4px;font-size:0.8rem">
            <option value="1">Leo (10:00 AM FDFS @ Broadway Cinemas Coimbatore)</option>
            <option value="2">Jailer (07:30 PM @ KG Cinemas Coimbatore)</option>
            <option value="5">Amaran (04:30 PM @ The Cinema Brookefields)</option>
            <option value="6">GOAT (01:30 PM @ INOX Prozone Mall)</option>
          </select>
        </div>
        <div style="display:flex;gap:6px;margin-bottom:8px">
          <div style="flex:1">
            <label style="font-size:0.75rem;color:#94a3b8">Seats:</label>
            <select id="chatSeatsSelect" style="width:100%;padding:4px;background:#0f172a;color:#fff;border:1px solid #334155;border-radius:4px;font-size:0.8rem">
              <option value="1">1 Seat (₹150)</option>
              <option value="2" selected>2 Seats (₹300)</option>
              <option value="3">3 Seats (₹450)</option>
              <option value="4">4 Seats (₹600)</option>
            </select>
          </div>
          <div style="flex:1">
            <label style="font-size:0.75rem;color:#94a3b8">Pay Via:</label>
            <select id="chatPayMethod" style="width:100%;padding:4px;background:#0f172a;color:#fff;border:1px solid #334155;border-radius:4px;font-size:0.8rem">
              <option value="Google Pay (UPI)">GPay UPI</option>
              <option value="PhonePe (UPI)">PhonePe</option>
              <option value="Paytm (UPI)">Paytm</option>
              <option value="Credit / Debit Card">Card</option>
            </select>
          </div>
        </div>
        <button id="chatPayBtn" style="width:100%;background:#22c55e;color:#fff;border:none;border-radius:6px;padding:6px;font-weight:700;cursor:pointer;font-size:0.85rem">
          💳 Pay ₹300 & Confirm Booking
        </button>
      `;

      const movieSelect = payBox.querySelector('#chatMovieSelect');
      const seatsSelect = payBox.querySelector('#chatSeatsSelect');
      const payMethodSelect = payBox.querySelector('#chatPayMethod');
      const payBtn = payBox.querySelector('#chatPayBtn');

      seatsSelect.addEventListener('change', () => {
        const count = parseInt(seatsSelect.value);
        payBtn.textContent = `💳 Pay ₹${count * 150} & Confirm Booking`;
      });

      payBtn.addEventListener('click', () => {
        payBtn.disabled = true;
        payBtn.textContent = '⏳ Processing payment...';

        fetch('/assistant/instant_pay/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: JSON.stringify({
            movie_id: movieSelect.value,
            seats: seatsSelect.value,
            payment_method: payMethodSelect.value,
          }),
        })
          .then(r => r.json())
          .then(res => {
            if (res.status === 'success') {
              payBox.innerHTML = `
                <div style="background:#064e3b;border:1px solid #059669;padding:8px;border-radius:6px;color:#a7f3d0">
                  <div style="font-weight:700;font-size:0.88rem">✅ Payment Successful!</div>
                  <div style="margin-top:4px">🎬 <strong>${res.movie_title}</strong></div>
                  <div>🏛️ ${res.theater} • ⏰ ${res.timing}</div>
                  <div>🎟️ Seats: <strong>${res.seats}</strong></div>
                  <div>💰 Paid: <strong>₹${res.total}</strong> via ${res.payment_method}</div>
                  <div style="margin-top:4px;font-size:0.75rem;color:#6ee7b7">Ref: <strong>${res.booking_ref}</strong> | Txn: ${res.payment_id}</div>
                </div>
              `;
            } else {
              payBox.innerHTML = `<span style="color:#f87171">Payment failed: ${res.error || 'Please try again'}</span>`;
            }
            scroll();
          })
          .catch(() => {
            payBox.innerHTML = '<span style="color:#f87171">Network error. Please try again.</span>';
          });
      });

      div.appendChild(payBox);
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
    typingEl.textContent = 'CineBot is typing…';
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
