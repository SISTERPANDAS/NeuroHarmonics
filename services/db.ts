import { Pool } from "pg";

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false,
  },
});

// Test connection on startup
pool.on("connect", () => {
  console.log("✓ PostgreSQL connection pool initialized");
});

pool.on("error", (err) => {
  console.error("✗ PostgreSQL pool error:", err);
});

export default pool;
