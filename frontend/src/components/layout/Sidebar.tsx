import { Link, useLocation } from 'react-router-dom'
import {
  LayoutDashboard, Package, ArrowDownLeft, ArrowUpRight, ArrowLeftRight,
  ShoppingCart, Truck, Wrench, FolderKanban, Barcode, Settings,
  LogOut, ChevronDown, ChevronRight, MapPin, Users,
} from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '../../stores/authStore'
import { cn } from '../../lib/utils'

interface NavItem {
  label: string
  icon: React.ReactNode
  path?: string
  children?: { label: string; path: string }[]
}

const navItems: NavItem[] = [
  { label: 'Dashboard', icon: <LayoutDashboard size={20} />, path: '/' },
  { label: 'Items', icon: <Package size={20} />, path: '/items' },
  {
    label: 'Inventory',
    icon: <ArrowLeftRight size={20} />,
    children: [
      { label: 'Stock In', path: '/inventory/stock-in' },
      { label: 'Stock Out', path: '/inventory/stock-out' },
      { label: 'Transfer', path: '/inventory/transfer' },
    ],
  },
  {
    label: 'Orders',
    icon: <ShoppingCart size={20} />,
    children: [
      { label: 'Purchase Orders', path: '/orders/purchase' },
      { label: 'Delivery Orders', path: '/orders/delivery' },
    ],
  },
  { label: 'Repairs', icon: <Wrench size={20} />, path: '/repairs' },
  { label: 'Projects', icon: <FolderKanban size={20} />, path: '/projects' },
  {
    label: 'Tracking',
    icon: <Barcode size={20} />,
    children: [
      { label: 'Serial Numbers', path: '/tracking/serials' },
      { label: 'Batch Numbers', path: '/tracking/batches' },
    ],
  },
  {
    label: 'Settings',
    icon: <Settings size={20} />,
    children: [
      { label: 'Locations', path: '/settings/locations' },
      { label: 'Users', path: '/settings/users' },
      { label: 'General', path: '/settings' },
    ],
  },
]

function NavSection({ item }: { item: NavItem }) {
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(() =>
    item.children?.some((c) => location.pathname.startsWith(c.path)) ?? false
  )

  if (item.children) {
    const isActive = item.children.some((c) => location.pathname.startsWith(c.path))
    return (
      <div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={cn(
            'flex w-full items-center justify-between rounded-lg px-3 py-2 text-sm font-medium transition-colors',
            isActive
              ? 'bg-primary text-primary-foreground'
              : 'text-gray-700 hover:bg-gray-100'
          )}
        >
          <span className="flex items-center gap-3">
            {item.icon}
            {item.label}
          </span>
          {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        </button>
        {isOpen && (
          <div className="ml-4 mt-1 space-y-1">
            {item.children.map((child) => (
              <Link
                key={child.path}
                to={child.path}
                className={cn(
                  'block rounded-lg px-3 py-2 text-sm transition-colors',
                  location.pathname === child.path
                    ? 'bg-primary/10 text-primary font-medium'
                    : 'text-gray-600 hover:bg-gray-100'
                )}
              >
                {child.label}
              </Link>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <Link
      to={item.path!}
      className={cn(
        'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
        location.pathname === item.path
          ? 'bg-primary text-primary-foreground'
          : 'text-gray-700 hover:bg-gray-100'
      )}
    >
      {item.icon}
      {item.label}
    </Link>
  )
}

export function Sidebar() {
  const logout = useAuthStore((s) => s.logout)
  const user = useAuthStore((s) => s.user)

  return (
    <aside className="flex w-64 flex-col border-r bg-white">
      <div className="flex items-center gap-2 border-b px-4 py-4">
        <Package className="text-primary" size={28} />
        <div>
          <h1 className="text-lg font-bold leading-tight">BIMS</h1>
          <p className="text-xs text-muted-foreground">Bigstar Inventory</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 overflow-auto p-3">
        {navItems.map((item) => (
          <NavSection key={item.label} item={item} />
        ))}
      </nav>

      <div className="border-t p-3">
        <div className="mb-2 px-3 py-2">
          <p className="text-xs font-medium text-gray-500">Logged in as</p>
          <p className="text-sm font-medium">{user?.username || 'Unknown'}</p>
          <p className="text-xs text-gray-400 capitalize">{user?.role || ''}</p>
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-red-600 transition-colors hover:bg-red-50"
        >
          <LogOut size={20} />
          Logout
        </button>
      </div>
    </aside>
  )
}
