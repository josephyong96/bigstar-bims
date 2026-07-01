export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface Location {
  id: number;
  name: string;
  address: string;
  type: string;
  is_active: boolean;
  created_at: string;
}

export interface Project {
  id: number;
  project_code: string;
  name: string;
  description: string;
  location_id: number;
  location?: Location;
  status: string;
  start_date: string;
  end_date: string;
  created_by: number;
  created_at: string;
}

export interface ItemCategory {
  id: number;
  name: string;
  description: string;
  created_at: string;
}

export interface Item {
  id: number;
  item_code: string;
  name: string;
  description: string;
  category_id: number;
  category?: ItemCategory;
  unit: string;
  barcode: string;
  min_stock_level: number;
  current_stock: number;
  status: string;
  created_at: string;
}

export interface BatchNumber {
  id: number;
  batch_code: string;
  item_id: number;
  item?: Item;
  purchase_order_id: number;
  quantity: number;
  unit_cost: number;
  manufacture_date: string;
  expiry_date: string;
  status: string;
  created_at: string;
}

export interface SerialNumber {
  id: number;
  serial_code: string;
  batch_id: number;
  batch?: BatchNumber;
  item_id: number;
  item?: Item;
  status: string;
  current_location_id: number;
  current_location?: Location;
  created_at: string;
}

export interface PurchaseOrder {
  id: number;
  po_code: string;
  project_id: number;
  project?: Project;
  supplier_name: string;
  status: string;
  total_amount: number;
  order_date: string;
  expected_date: string;
  created_by: number;
  created_at: string;
  items?: POItem[];
}

export interface POItem {
  id: number;
  purchase_order_id: number;
  item_id: number;
  item?: Item;
  quantity: number;
  unit_cost: number;
  total_cost: number;
}

export interface DeliveryOrder {
  id: number;
  do_code: string;
  project_id: number;
  project?: Project;
  receiver_name: string;
  status: string;
  delivery_date: string;
  created_by: number;
  created_at: string;
  items?: DOItem[];
}

export interface DOItem {
  id: number;
  delivery_order_id: number;
  item_id: number;
  item?: Item;
  serial_number_id: number;
  serial_number?: SerialNumber;
  quantity: number;
}

export interface RepairRecord {
  id: number;
  repair_code: string;
  serial_number_id: number;
  serial_number?: SerialNumber;
  item_id: number;
  item?: Item;
  issue_description: string;
  repair_status: string;
  repair_cost: number;
  repaired_by: string;
  created_at: string;
  completed_at: string;
}

export interface StockMovement {
  id: number;
  movement_type: string;
  item_id: number;
  item?: Item;
  serial_number_id: number;
  serial_number?: SerialNumber;
  from_location_id: number;
  from_location?: Location;
  to_location_id: number;
  to_location?: Location;
  quantity: number;
  reference_id: number;
  reference_type: string;
  notes: string;
  created_by: number;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
