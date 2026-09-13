import { BrowserRouter, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { AutomationBlueprintPage } from "./pages/AutomationBlueprintPage";
import { PlaceholderPage } from "./pages/PlaceholderPage";
import { RedesignProposalPage } from "./pages/RedesignProposalPage";
import { ReportPage } from "./pages/ReportPage";
import { StepReviewPage } from "./pages/StepReviewPage";
import { UploadPage } from "./pages/UploadPage";

export function App() {
  return <BrowserRouter><Routes><Route element={<AppShell />}>
    <Route path="/" element={<UploadPage />} />
    <Route path="/review/:workflowId" element={<StepReviewPage />} />
    <Route path="/automation/:workflowId/:stepId" element={<AutomationBlueprintPage />} />
    <Route path="/redesign/:workflowId/:stepId" element={<RedesignProposalPage />} />
    <Route path="/report/:workflowId" element={<ReportPage />} />
    <Route path="/dashboard" element={<PlaceholderPage eyebrow="04 / Portfolio view" title="See the exception pattern across the book of work." description="This portfolio view will map complexity and exception concentration across all analyzed workflows." dependency="Analyzed workflow aggregation endpoint" />} />
    <Route path="/resume" element={<PlaceholderPage eyebrow="04 / Resume session" title="Pick up exactly where the work paused." description="This control will list the latest incomplete workflow and return the user to its last completed stage." dependency="WorkflowSession persistence and API support" />} />
  </Route></Routes></BrowserRouter>;
}
