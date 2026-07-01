import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { LoginPage } from './pages/LoginPage'
import { DashboardPage } from './pages/DashboardPage'
import { ItemsPage } from './pages/ItemsPage'
import { ItemFormPage } from './pages/ItemFormPage'
import { ItemDetailPage } from './pages/ItemDetailPage'
import { StockInPage } from './pages/inventory/StockInPage'
import { StockOutPage } from './pages/inventory/StockOutPage'
import { TransferPage } from './pages/inventory/TransferPage'
import { PurchaseOrdersPage } from './pages/orders/PurchaseOrdersPage'
import { POFormPage } from './pages/POFormPage'
import { DeliveryOrdersPage } from './pages/orders/DeliveryOrdersPage'
import { DOFormPage } from './pages/DOFormPage'
import { RepairsPage } from './pages/repairs/RepairsPage'
import { RepairFormPage } from './pages/RepairFormPage'
import { ProjectsPage } from './pages/projects/ProjectsPage'
import { ProjectFormPage } from './pages/ProjectFormPage'
import { SerialsPage } from './pages/tracking/SerialsPage'
import { BatchesPage } from './pages/tracking/BatchesPage'
import { LocationsPage } from './pages/settings/LocationsPage'
import { UsersPage } from './pages/settings/UsersPage'
import { SettingsPage } from './pages/settings/SettingsPage'
import { NotFoundPage } from './pages/NotFoundPage'
import { useAuthStore } from './stores/authStore'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <AppLayout />
            </PrivateRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="items" element={<ItemsPage />} />
          <Route path="items/new" element={<ItemFormPage />} />
          <Route path="items/:id" element={<ItemDetailPage />} />
          <Route path="items/:id/edit" element={<ItemFormPage />} />
          <Route path="inventory/stock-in" element={<StockInPage />} />
          <Route path="inventory/stock-out" element={<StockOutPage />} />
          <Route path="inventory/transfer" element={<TransferPage />} />
          <Route path="orders/purchase" element={<PurchaseOrdersPage />} />
          <Route path="orders/purchase/new" element={<POFormPage />} />
          <Route path="orders/delivery" element={<DeliveryOrdersPage />} />
          <Route path="orders/delivery/new" element={<DOFormPage />} />
          <Route path="repairs" element={<RepairsPage />} />
          <Route path="repairs/new" element={<RepairFormPage />} />
          <Route path="projects" element={<ProjectsPage />} />
          <Route path="projects/new" element={<ProjectFormPage />} />
          <Route path="tracking/serials" element={<SerialsPage />} />
          <Route path="tracking/batches" element={<BatchesPage />} />
          <Route path="settings/locations" element={<LocationsPage />} />
          <Route path="settings/users" element={<UsersPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
