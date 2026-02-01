import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import './index.css';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import BusinessSettings from './pages/BusinessSettings';
import KnowledgeBase from './pages/KnowledgeBase';
import Services from './pages/Services';
import BookingRules from './pages/BookingRules';
import CallLogs from './pages/CallLogs';
import Layout from './components/Layout';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  return token ? <>{children}</> : <Navigate to="/login" />;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="settings" element={<BusinessSettings />} />
          <Route path="knowledge-base" element={<KnowledgeBase />} />
          <Route path="services" element={<Services />} />
          <Route path="booking-rules" element={<BookingRules />} />
          <Route path="call-logs" element={<CallLogs />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
