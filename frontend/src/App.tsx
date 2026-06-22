import { BrowserRouter, Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Navbar from "./components/Navbar";
import { AuthProvider } from "./context/AuthContext";
import HistoryPage from "./pages/HistoryPage";
import LoginPage from "./pages/LoginPage";
import QueryPage from "./pages/QueryPage";
import RegisterPage from "./pages/RegisterPage";
import ConnectionsPage from "./pages/ConnectionsPage";
import UploadPage from "./pages/UploadPage";

function AppShell() {
  return (
    <div className="flex h-screen w-full bg-slate-50">
      <Navbar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<ProtectedRoute><QueryPage /></ProtectedRoute>} />
          <Route path="/upload" element={<ProtectedRoute><UploadPage /></ProtectedRoute>} />
          <Route path="/connections" element={<ProtectedRoute><ConnectionsPage /></ProtectedRoute>} />
          <Route path="/history" element={<ProtectedRoute><HistoryPage /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/*" element={<AppShell />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
