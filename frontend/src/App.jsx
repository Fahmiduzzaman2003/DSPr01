import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import ClassificationApp from "./pages/ClassificationApp.jsx";
import Home from "./pages/Home.jsx";
import RegressionApp from "./pages/RegressionApp.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/regression" element={<RegressionApp />} />
        <Route path="/classification" element={<ClassificationApp />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
