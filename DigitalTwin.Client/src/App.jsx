import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './pages/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import CommandCenter from './pages/CommandCenter';
import HealthIntelligence from './pages/HealthIntelligence';
import AutomationHub from './pages/AutomationHub';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Core Layout Shell */}
        <Route element={<Layout />}>
          {/* Guest Auth Gates */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Secure Workspace Views */}
          <Route path="/" element={<Dashboard />} />
          <Route path="/command" element={<CommandCenter />} />
          <Route path="/health" element={<HealthIntelligence />} />
          <Route path="/automate" element={<AutomationHub />} />
          <Route path="/settings" element={<Settings />} />

          {/* Wildcard Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
