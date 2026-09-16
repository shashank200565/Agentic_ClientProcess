import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      "/analyze": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
      "/reports": "http://127.0.0.1:8000",
      "/sessions": "http://127.0.0.1:8000",
    },
  },
});
