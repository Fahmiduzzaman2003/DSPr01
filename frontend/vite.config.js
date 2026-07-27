import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    // In dev the API runs on 8000; requests to /api are proxied so the browser
    // sees a single origin and CORS never comes into play.
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
});
