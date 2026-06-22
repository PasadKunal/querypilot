import { BrowserRouter, Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar";
import HistoryPage from "./pages/HistoryPage";
import QueryPage from "./pages/QueryPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-slate-50">
        <Navbar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<QueryPage />} />
            <Route path="/history" element={<HistoryPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
