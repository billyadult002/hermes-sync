import { lazy, Suspense } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import StateView from './components/StateView'

const Control = lazy(() => import('./pages/Control'))
const Chat = lazy(() => import('./pages/Chat'))
const Legal = lazy(() => import('./pages/Legal'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const KPI = lazy(() => import('./pages/KPI'))
const Strategy = lazy(() => import('./pages/Strategy'))
const Tasks = lazy(() => import('./pages/Tasks'))
const Workspace = lazy(() => import('./pages/Workspace'))

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Suspense fallback={<StateView type="loading" message="Loading..." />}>
          <Routes>
            <Route path="/" element={<Chat />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/kpi" element={<KPI />} />
            <Route path="/strategy" element={<Strategy />} />
            <Route path="/control" element={<Control />} />
            <Route path="/legal" element={<Legal />} />
            <Route path="/workspace/:id" element={<Workspace />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </Layout>
    </BrowserRouter>
  )
}
