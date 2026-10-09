# Bhadawar Hotel & Bhadawar Foods website

This is a mobile-friendly browser website, not an installable app.

## Open the website

Install the backend packages with `pip install -r backend/requirements.txt`, then run `server.py` to use the local API and upload flow at `http://127.0.0.1:4175`. The customer site is `index.html`; customer wallet sign-in is `account.html`; Admin, Kitchen, and Delivery staff access is `team.html`.

## Production build and Vercel API

- Install the pinned frontend toolchain with `pnpm install`, then generate the production site with `pnpm build`. Vite builds the five HTML pages into `dist/`, minifies JavaScript and CSS, and copies the local restaurant images.
- `vercel.json` builds the static site from `dist/` and configures the Python serverless functions under the root `api/` directory. The primary production endpoints (`/api/orders`, `/api/food-stories`, `/api/leaderboard`, `/api/preview-config`) have explicit function files; nested API paths use the catch-all function. Deploy from the repository root, not by deploying `dist/` alone, or Vercel will publish only static files and `/api/*` will return 404.
- The proxy functions require the Vercel environment variable `BHADAWAR_API_ORIGIN`, set to the HTTPS origin of the separately hosted backend (for example, your own `https://api...` host; enter the origin only, with no `/api` suffix). If the function is present but this value is missing, the API deliberately returns a JSON `503`; a `404` means the API function was not part of the active deployment or the Vercel project's root directory is wrong.
- The backend is now a FastAPI application with separate auth, order, booking, payment, and community handler modules. Vercel serves the static site and proxies `/api/*`; it does not host the durable application database. Configure the backend service with `HOST=0.0.0.0`, `PORT` from its platform, `BHADAWAR_API_ONLY=true`, `BHADAWAR_ENV=production`, and unique staff credentials. Do not use a temporary Quick Tunnel as the production API origin.
- Production mode requires a managed PostgreSQL `DATABASE_URL` and shared Redis `REDIS_URL`. SQLAlchemy models define the PostgreSQL schema, and Alembic applies schema migrations at backend startup. Existing handler queries use a small SQLAlchemy compatibility adapter during the transition, so the schema/migrations are ORM-backed while handler query conversion remains incremental. SQLite remains the local development default. The PostgreSQL database starts with an empty application dataset; provision/import any menu, order, booking, and wallet data separately before switching customers to it.
- Redis stores expiring customer/staff sessions and OTP challenge state, and applies cross-instance OTP rate limits atomically. In development, those states stay in process memory. Production startup checks both persistent services and fails early if either is unavailable.
- After the backend is live, add `BHADAWAR_API_ORIGIN` in the Vercel project settings and redeploy. Without it, the Vercel `/api/*` route deliberately returns `503` instead of accepting orders that cannot be saved.
- Delivery checkouts now require a customer map pin; the server measures the restaurant distance and applies the 10 km limit and ₹35/₹50 delivery bands itself. It recomputes menu prices, tax, first-order delivery, and wallet redemption from backend data. Corporate bulk pricing remains checked by the corporate order API.
- For production, keep the backend on an always-on service and use its HTTPS origin. Do not set `BHADAWAR_ENV=production` until PostgreSQL and Redis URLs are configured in that backend's private environment. Never put database URLs, provider credentials, or real staff passwords in Git or frontend settings.

### Local staff preview accounts

Staff sign-in uses an in-memory local preview session. These defaults are only for the server bound to `127.0.0.1`; override them with environment variables before sharing a preview:

| Role | Default username | Default password |
| --- | --- | --- |
| Admin | `admin` | `BhadawarAdminDemo!` |
| Kitchen | `kitchen` | `BhadawarKitchenDemo!` |
| Delivery | `delivery` | `BhadawarDeliveryDemo!` |

Set `BHADAWAR_ADMIN_USER` / `BHADAWAR_ADMIN_PASSWORD`, `BHADAWAR_KITCHEN_USER` / `BHADAWAR_KITCHEN_PASSWORD`, and `BHADAWAR_DELIVERY_USER` / `BHADAWAR_DELIVERY_PASSWORD` to override these accounts. This is demo access control, not production identity security.

To add individual rider preview logins, set `BHADAWAR_RIDER_CREDENTIALS` in `.env` to semicolon-separated `username=password` pairs (for example, `rider-a=...;rider-b=...`). Each rider marks themselves available in the Delivery portal. Ready orders are assigned to an available rider with the fewest active deliveries; a rider's unpicked orders return to the pool when they go unavailable. Availability renews while the rider portal is open and expires after two minutes without a heartbeat.

### Customer SMS OTP sign-in

- Customer account creation and sign-in use MSG91's server-side OTP send and verify APIs. Set `MSG91_AUTH_KEY` and `MSG91_OTP_TEMPLATE_ID` in the backend server's environment (or private `.env`), then restart `server.py`. Never put the auth key in browser JavaScript.
- In MSG91, create and approve an OTP template with the `##OTP##` placeholder, and complete the required Indian sender ID/DLT setup before sending. See MSG91's [OTP setup guide](https://msg91.com/help/sendotp/step-by-step-process-to-configure-otp) and [OTP API documentation](https://docs.msg91.com/otp).
- Until both server values are configured, the OTP endpoints return `503` and do not fall back to a demo code. The implementation here has not sent a real SMS; first live send will use the MSG91 account configured by the site owner.

### Customer email verification

- Signed-in customers can verify the optional email saved in their profile with a 6-digit Resend code. Codes expire after 10 minutes and requests/attempts are rate-limited. Changing the saved email clears its previous verification.
- Set `RESEND_API_KEY` and `RESEND_FROM_EMAIL` on the backend. Verify the sending domain and sender in Resend first. Never expose the Resend key in browser code. The email code is optional; phone OTP remains the account sign-in check.
- The actual send cannot be confirmed until those private settings and a verified sending domain are configured.

### Customer location and rider directions

- Customers choose when to share current location from the delivery-address panel; the browser will ask permission. Delivery checkouts require a valid map pin, and the backend checks that it is within the delivery area.
- Ready orders are assigned to a rider marked available. Only that rider's assigned orders are returned to the delivery portal; the card includes a Google Maps two-wheeler directions link to the customer's pinned destination and uses the rider device's current location as the start point when available.
- This link-based map flow does not need a Google Maps API key or a billing-enabled Maps Platform project. Production location sharing requires an HTTPS site and the customer’s permission.

### Table and party booking deposits

Table reservations collect ₹50 per guest; party bookings collect ₹50 per person for 10–11 guests and ₹30 per person for 12 or more. Both use server-verified Razorpay checkout and are confirmed only after payment is captured. For local Razorpay setup, generate API keys in the Dashboard while Test Mode is selected, then paste the Test Key ID and Test Key Secret into the matching entries in `.env`. Keep `BHADAWAR_ENABLE_LIVE_PAYMENTS=false`; live keys are blocked unless that setting is explicitly enabled. Set `RAZORPAY_WEBHOOK_SECRET` when a webhook endpoint is configured. `.env` is excluded from version control and blocked by the local static server. After saving credentials, restart `server.py` and confirm `/api/payment-config` reports `test` before making a test booking. Razorpay's test checkout simulates payment and does not debit real money. After payment is verified, party bookings appear in the admin settlement area; staff enters the final bill and the site applies the advance once. Any excess advance is shown for manual refund follow-up.

## Menu and brand assets

- The website includes 136 vegetarian dishes and prices transcribed from the owner-supplied 10-page Bhadawar Hotel menu PDF.
- The logo, palette, pattern, and food photos in `assets/` are crops from that supplied menu artwork.
- The Zomato and Swiggy outlet listings were used to confirm the Bhadawar Hotel and Bhadawar Foods names and the Agra listing details. Their displayed prices vary from the supplied printed menu, so the website uses the printed-menu prices. Confirm current menu prices, terms, address, and opening hours before launch.
- Public listings: [Bhadawar Hotel on Zomato](https://www.zomato.com/agra/bhadawar-hotel-mantola/menu), [Bhadawar Hotel on Swiggy](https://www.swiggy.com/city/agra/bhadawar-hotel-daresi-civil-lines-rest84613), [Bhadawar Foods on Swiggy](https://www.swiggy.com/city/agra/bhadawar-foods-gajanan-nagar-civil-lines-rest175478).

## Preview behavior

- Menu search, categories, cart, checkout, dine-in reservations, wallet history, order stages, and staff panels are local-preview features.
- The dine-in booking deposit is ₹50 per guest and is credited toward the final bill. The sample website offer is ₹100 off a dine-in bill of ₹999 or more; the admin panel can change or hide it.
- Staff dashboard data is stored in the local SQLite database. Customer-only preview data may also use this browser's local storage. MSG91 OTP sends only when the backend key and approved template are configured; standard food-order payment selections remain demonstrations.
- Sample tax, delivery fees, and offer terms should be confirmed before launch. Public platform ratings are a snapshot and should be refreshed before launch.

## Production work still needed

The repository now contains the production database, session-storage, and FastAPI deployment paths, but the service accounts still need to be provisioned and configured by the owner before production traffic is moved. Customer OTP requires the owner's MSG91 credentials, approved DLT sender/template, and production backend environment setup. Live order updates and automatic Razorpay refunds are not implemented. Party advances still require owner verification of the payment setup, webhook configuration, external hosting, and production review. Confirm all restaurant details before accepting real orders or deposits.
