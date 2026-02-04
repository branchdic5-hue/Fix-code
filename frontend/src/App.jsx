import React from 'react';
import { Link, Route, Routes } from 'react-router-dom';
import CaseDashboard from './pages/CaseDashboard.jsx';
import CdrUpload from './pages/CdrUpload.jsx';
import EyeconSearch from './pages/EyeconSearch.jsx';
import Login from './pages/Login.jsx';
import Reports from './pages/Reports.jsx';

const App = () => (
  <div className="app">
    <header>
      <h1>Multi-Operator CDR Analysis</h1>
      <nav>
        <Link to="/">Login</Link>
        <Link to="/cases">Cases</Link>
        <Link to="/upload">Upload</Link>
        <Link to="/reports">Reports</Link>
        <Link to="/eyecon">Eyecon</Link>
      </nav>
    </header>
    <main>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/cases" element={<CaseDashboard />} />
        <Route path="/upload" element={<CdrUpload />} />
        <Route path="/reports" element={<Reports />} />
        <Route path="/eyecon" element={<EyeconSearch />} />
      </Routes>
    </main>
  </div>
);

export default App;
