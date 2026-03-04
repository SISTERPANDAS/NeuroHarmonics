# NeuroHarmonics Express Backend

This folder contains the Node.js/Express backend for the NeuroHarmonics full‑stack application. It uses MongoDB Atlas as the database and Mongoose for ODM.

## Setup

1. **Install dependencies**
   ```bash
   cd node-backend
   npm install
   ```

2. **Environment variables**
   - Copy `.env` and fill in your Atlas connection string using a
  user that exists in your cluster and has access to the `neuroharmonics`
  database. An authentication error (`bad auth`) means the username/password
  pair in the URI is wrong or does not have privileges.

  - Example:
    ```env
    MONGO_URI=mongodb+srv://myUser:mySecurePassword@cluster0.phmuefa.mongodb.net/neuroharmonics?retryWrites=true&w=majority
    PORT=5000
    ```


3. **Start server**
   ```bash
   npm run dev
   # or npm start for production
   ```

The server exposes REST endpoints under `/api` that map to your existing collections (users, admin, community_message, contact_message, rfeedback).

## Structure

```
node-backend/
├── src/
│   ├── config/db.js      # Mongoose connection
│   ├── controllers/      # business logic
│   ├── models/           # mongoose schemas (explicit collection names)
│   ├── routes/           # express routers
│   └── index.js          # entry point
├── .env                 # environment variables (ignored by git)
└── package.json
```

## Notes

- Schemas use `collection` option to match imported collections exactly; no new collections are created.
- All CRUD handlers use async/await and basic error handling.
- Add additional routes/controllers as needed.
