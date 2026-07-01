import { Link, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  Package,
  FolderKanban,
  ClipboardList,
  Truck,
  Wrench,
  Warehouse,
  Barcode,
  Settings,
  LogOut,
} from "lucide-react";
import { useAuthStore } from "../../stores/authStore";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/items", icon: Package, label: "Items" },
  { to: "/projects", icon: FolderKanban, label: "Projects" },
  { to: "/orders/purchase", icon: ClipboardList, label: "Purchase Orders" },
  { to: "/orders/delivery", icon: Truck, label: "Delivery Orders" },
  { to: "/repairs", icon: Wrench, label: "Repairs" },
  { to: "/inventory/stock-in", icon: Warehouse, label: "Stock In" },
  { to: "/inventory/stock-out", icon: Warehouse, label: "Stock Out" },
  { to: "/tracking/batches", icon: Barcode, label: "Batches" },
  { to: "/tracking/serials", icon: Barcode, label: "Serials" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export function Sidebar() {
  const location = useLocation();
  const logout = useAuthStore((s) => s.logout);

  return (
    <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-blue-900">BIMS</h1>
        <p className="text-xs text-gray-500">Big Star Inventory</p>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.to;
          return (
            <Link
              key={item.to}
              to={item.to}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-blue-50 text-blue-700"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <Icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-2 border-t border-gray-200">
        <button
          onClick={logout}
          className="flex items-center gap-3 px-3 py-2 w-full rounded-lg text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  );
}
