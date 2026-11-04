#!/usr/bin/env bash
# setup.sh – One-command dev setup for TicketSite
set -e

echo "==> Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "==> Installing dependencies..."
pip install -r requirements.txt

echo "==> Copying .env.example to .env (edit it before running the server)..."
[ -f ticketsite/.env ] || cp .env.example ticketsite/.env

echo "==> Running migrations (seeds FAQs, error codes & sample events)..."
cd ticketsite
python manage.py migrate

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit ticketsite/.env with your API keys"
echo "  2. python ticketsite/manage.py createsuperuser"
echo "  3. python ticketsite/manage.py runserver"
echo "  4. Open http://127.0.0.1:8000"

