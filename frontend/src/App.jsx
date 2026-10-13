import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import UploadBudget from './pages/UploadBudget.jsx'
import UpliftCurves from './pages/UpliftCurves.jsx'
import AllocationMatrix from './pages/AllocationMatrix.jsx'
import './App.css'

const links = [
  { to: '/upload', label: 'Upload & Budget' },
  { to: '/uplift', label: 'Uplift Curves' },
  { to: '/allocation', label: 'Allocation Matrix' },
]

export default function App() {
  return (
    <div className="app">
      <header className="navbar">
        <span className="brand">EconoCausal</span>
        <nav>
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) => (isActive ? 'active' : '')}
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </header>
      <main className="content">
        <Routes>
          <Route path="/" element={<Navigate to="/upload" replace />} />
          <Route path="/upload" element={<UploadBudget />} />
          <Route path="/uplift" element={<UpliftCurves />} />
          <Route path="/allocation" element={<AllocationMatrix />} />
          <Route path="*" element={<p>Page not found.</p>} />
        </Routes>
      </main>
    </div>
  )
}