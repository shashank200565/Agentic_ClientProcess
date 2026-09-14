import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { AutomationBlueprintPage } from "./pages/AutomationBlueprintPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { DashboardPage } from "./pages/DashboardPage";
import { RedesignProposalPage } from "./pages/RedesignProposalPage";
import { ReportPage } from "./pages/ReportPage";
import { RedesignedFlowPage } from "./pages/RedesignedFlowPage";
import { ResumeSessionPage } from "./pages/ResumeSessionPage";
import { StepReviewPage } from "./pages/StepReviewPage";
import { UploadPage } from "./pages/UploadPage";

export function App() {
  return <BrowserRouter><Routes><Route element={<AppShell />}>
    <Route path="/" element={<UploadPage />} />
    <Route path="/review/:workflowId" element={<StepReviewPage />} />
    <Route path="/automation/:workflowId/:stepId" element={<AutomationBlueprintPage />} />
    <Route path="/redesign/:workflowId/:stepId" element={<RedesignProposalPage />} />
    <Route path="/report/:workflowId" element={<ReportPage />} />
    <Route path="/redesigned-flow/:workflowId" element={<RedesignedFlowPage />} />
    <Route path="/dashboard" element={<DashboardPage />} />
    <Route path="/resume" element={<ResumeSessionPage />} />
  </Route></Routes></BrowserRouter>;
}
