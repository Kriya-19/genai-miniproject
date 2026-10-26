# DiagnoSure frontend (React 18 + Vite, JavaScript)
Frontend only. Runs on fictional mock data by default.

    npm install
    npm run dev      # http://localhost:5173
    npm run build

## Configuration (`.env`, see `.env.example`)
- `VITE_USE_MOCKS=true` mock services; set `false` to call the API.
- `VITE_API_BASE_URL=http://localhost:8000/api`

## Architecture
Pages never call `fetch`. Each feature has a module in `src/services/` exposing identical methods in mock and API mode (`pick(mock, real)` in `apiClient.js`). Mock data lives in `src/mocks/data.js`. In API mode failures show an error with Retry; mock data is never used as a fallback. See `API_CONTRACTS.md`.
Diagnosis is a structured case form (no chatbot). Video uses a demo adapter in `videoService.js` (no real WebRTC). Clinic map is a placeholder until a provider is configured.
