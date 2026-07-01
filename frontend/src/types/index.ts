export interface Item {
  id: string
  sku: string
  name: string
  description: string | null
  category_id: string | null
  brand: string | null
  model: string | null
  unit: string
  unit_cost: number | null
  reorder_level: number
  inventory_type: 'serialized' | 'batch_tracked' | 'standard'
  barcode: string | null
  status: 'active' | 'inactive'
  total_quantity: number
  created_at: string
  updated_at: string | null
}

export interface Category {
  id: string
  code: string
  name: string
  description: string | null
}

export interface Location {
  id: string
  code: string
  name: string
  type: 'warehouse' | 'office' | 'project_site' | 'supplier' | 'virtual'
  address: string | null
  status: 'active' | 'inactive'
}

export interface Project {
  id: string
  project_code: string
  name: string
  description: string | null
  client_name: string | null
  start_date: string | null
  end_date: string | null
  status: 'active' | 'completed' | 'on_hold' | 'cancelled'
  created_by: string | null
  created_at: string
}

export interface Stock {
  id: string
  item_id: string
  location_id: string
  project_id: string | null
  quantity: number
  reserved_quantity: number
  unit_cost: number | null
  item_name?: string
  item_sku?: string
  location_name?: string
  location_code?: string
  project_code?: string
}

export interface StockMovement {
  id: string
  movement_type: 'stock_in' | 'stock_out' | 'transfer' | 'adjustment'
  item_id: string
  from_location_id: string | null
  to_location_id: string | null
  quantity: number
  reference_no: string | null
  reference_type: string | null
  notes: string | null
  created_by: string | null
  created_at: string
}

export interface PurchaseOrder {
  id: string
  po_number: string
  supplier_name: string
  status: 'pending' | 'partial' | 'received' | 'cancelled'
  total_amount: number
  notes: string | null
  created_by: string | null
  created_at: string
  po_items: POItem[]
}

export interface POItem {
  id: string
  po_id: string
  item_id: string
  quantity: number
  unit_price: number
  received_qty: number
  item_name?: string
  item_sku?: string
}

export interface DeliveryOrder {
  id: string
  do_number: string
  project_id: string
  status: 'pending' | 'dispatched' | 'in_transit' | 'delivered' | 'cancelled' | 'returned'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  delivery_date: string | null
  notes: string | null
  created_by: string | null
  created_at: string
}

export interface RepairTicket {
  id: string
  ticket_number: string
  item_id: string
  serial_id: string | null
  issue_description: string
  status: 'open' | 'in_progress' | 'on_hold' | 'resolved' | 'closed' | 'cancelled'
  priority: 'low' | 'medium' | 'high' | 'urgent'
  reported_by: string
  assigned_to: string | null
  resolution_notes: string | null
  created_at: string
  resolved_at: string | null
}

export interface SerialNumber {
  id: string
  serial_number: string
  item_id: string
  status: 'in_stock' | 'allocated' | 'in_use' | 'under_repair' | 'disposed' | 'reserved'
  location_id: string | null
  project_id: string | null
  po_id: string | null
  created_at: string
}

export interface BatchNumber {
  id: string
  item_id: string
  batch_number: string
  location_id: string | null
  quantity: number
  expiry_date: string | null
  manufacture_date: string | null
  supplier_batch: string | null
  status: 'active' | 'inactive' | 'expired'
}

export interface User {
  id: string
  username: string
  email: string
  full_name: string | null
  role: string
  is_active: boolean
  last_login: string | null
  created_at: string
}

export interface DashboardSummary {
  total_items: number
  total_stock: number
  low_stock_count: number
  pending_purchase_orders: number
  open_repair_tickets: number
  active_projects: number
}
