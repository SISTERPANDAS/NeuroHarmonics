# NeuroHarmonics Fullstack Integration

This project integrates a Flask backend (API, authentication) with a React dashboard frontend, served as static files by Flask for a seamless user experience.

## How it Works
- User logs in via Flask (Python backend)
- On successful login, Flask redirects to /dashboard
- /dashboard serves the React app (built static files)
- React fetches user data and analytics from Flask API endpoints

## Setup Steps
1. Build the React app (from /client):
   - `npm install`
   - `npm run build`
2. Copy the build output (client/build or client/dist) to Flask's static directory (e.g., /static/dashboard or /static/app)
3. Update Flask's /dashboard route to serve the React index.html
4. Ensure all API endpoints are accessible at /api/*
5. Test login and dashboard flow

## Development
- For local development, run React and Flask separately for hot reload
- For production, serve React build from Flask

---

## Optional Node/Express API

A parallel Node.js/Express backend has been scaffolded under `node-backend/` for
clients using React (Vite) and MongoDB Atlas. It connects to the same
`neuroharmonics` database and uses Mongoose with schemas targeting the
existing collections (`users`, `admin`, `community_message`, `contact_message`,
`rfeedback`). See `node-backend/README.md` for setup instructions.

Replace this file with project-specific details as you customize further.