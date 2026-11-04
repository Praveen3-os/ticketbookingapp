# CineTix 🎬 – Tamil Movie Ticket Booking Platform

> **Live Website:** [http://127.0.0.1:8000](http://127.0.0.1:8000)  
> **GitHub Repository:** `https://github.com/yourusername/cinetix-tamil-movies`

A full-stack Django movie ticket booking platform for original **Tamil cinema (Kollywood)** in Chennai, built as a **Software Development Final Assessment** submission. It includes an integrated AI assistant (**CineBot**), SQL-backed bookings & support tickets, MongoDB chat logging, Chennai weather integration, custom error pages, and request logging.

---

## 🎬 Real Tamil Cinema Features

- **10 Original Tamil Movies:**
  - *Leo* (லியோ) – Thalapathy Vijay, Lokesh Kanagaraj
  - *Jailer* (ஜெயிலர்) – Superstar Rajinikanth, Nelson Dilipkumar
  - *Ponniyin Selvan 3* (பொன்னியின் செல்வன் 3) – Mani Ratnam epic
  - *Vidaamuyarchi* (விடாமுயற்சி) – Ajith Kumar
  - *Amaran* (அமரன்) – Sivakarthikeyan, Sai Pallavi
  - *GOAT* (கோட்) – Vijay, Venkat Prabhu
  - *Kanguva* (காங்குவா) – Suriya
  - *Vettaiyan* (வேட்டையன்) – Rajinikanth, Amitabh Bachchan, Fahadh Faasil
  - *Demonte Colony 2* (டிமான்ட் காலனி 2) – Arulnithi
  - *Love Today 2* (லவ் டுடே 2) – Pradeep Ranganathan
- **Top Chennai Theaters:** Rohini Silver Screens (Koyambedu), SPI Sathyam Cinemas (Royapettah), AGS Cinemas (T. Nagar), Kamala Cinemas (Vadapalani), Kasi Theatre, PVR SKLS Galaxy Mall, INOX National, etc.
- **Showtimes:** Morning (10:00 AM / FDFS), Matinee (01:30 PM), First Show (04:30 PM), Second Show (07:30 PM), Night Show (10:30 PM).

---

## 📋 Assessment Requirements Checklist

| Requirement | Status | CineTix Implementation |
|---|---|---|
| Responsive site, ≥ 3 pages | ✅ | 10 pages: Home, Now Showing, Movie Detail & Showtimes, Seat Selection, Booking Detail, My Bookings, FAQ, Error Codes, About, Contact |
| Chat widget on **every** page | ✅ | CineBot floating assistant in `base.html` |
| ≥ 10 FAQs in SQL database | ✅ | 14 Tamil movie & booking FAQs seeded in SQL (`apps.faqs`) |
| ≥ 8 error codes | ✅ | 400, 401, 403, 404, 429, 500, 503 + **SEAT-001** (Site-specific "Seat Already Booked") |
| Custom 404 & 500 with "Ask assistant" | ✅ | `templates/errors/404.html` & `500.html` |
| AI answers FAQs & error codes | ✅ | Fuzzy match + Movie database + OpenAI GPT-3.5-turbo fallback |
| AI creates support ticket when unable to answer | ✅ | Automatically generates `SUP-XXXXXXXX` ticket in SQL |
| Support tickets in SQL | ✅ | `SupportTicket` model in `apps.tickets` |
| Chat logs & feedback in MongoDB | ✅ | `chat_logs` & `feedback` collections in MongoDB (`MONGO_URI`) |
| API keys in env variables | ✅ | Managed via `.env` and `django-environ` |
| Request logging & Health check | ✅ | `RequestLoggingMiddleware` (SQL table + file) & `GET /health/` |
| Third-party API with timeout & fallback | ✅ | OpenWeatherMap API for Chennai on Home page (5 s timeout + fallback) |
| README with proposed improvement | ✅ | Included below |

---

## 💡 Proposed Improvement

**Interactive Visual Seat Map Selection (SVG / Canvas Grid):**  
Currently, users select seat quantity and the system allocates available seats with concurrency checks (`select_for_update`). Adding an interactive graphical seat layout (Screen, Box, Balcony, First Class, Corner seats) with real-time seat locking via WebSockets (Django Channels) would prevent race conditions during high-demand FDFS bookings for superstar releases.

---

## 🚀 Running the Project

```bash
cd /Users/praveen.a/.gemini/antigravity/scratch/ticketbooking
python3 manage.py runserver 8000
```

Open **http://127.0.0.1:8000** in your browser.  
Admin Login: `admin` / `admin123` at `/admin/`.
