import { ClerkProvider } from "@clerk/react";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";
import "./styles.css";

createRoot(document.getElementById("root")!).render(<StrictMode><ClerkProvider afterSignOutUrl="/">
<App />
</ClerkProvider></StrictMode>);