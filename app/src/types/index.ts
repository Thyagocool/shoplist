// Auth
export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

export interface AuthResponse {
  user: UserResponse;
  tokens: TokenResponse;
}

export interface UserResponse {
  id: string;
  name: string;
  email: string;
}

// Category
export interface CategoryResponse {
  id: string;
  name: string;
}

// Item
export interface ItemResponse {
  id: string;
  name: string;
  category_id: string;
  category_name: string;
  default_unit: string;
  default_quantity: number;
  min_stock: number;
  max_stock: number;
  active: boolean;
}

// Store
export interface StoreResponse {
  id: string;
  name: string;
}

// Stock
export interface StockItemResponse {
  pre_registered_item_id: string;
  item_name: string;
  category_name: string;
  current_quantity: number;
  default_unit: string;
  min_stock: number;
  max_stock: number;
}

// --- New Inventory feature ---
export interface InventoryItemInput {
  pre_registered_item_id: string;
  declared_quantity: number;
}

export interface InventoryItemResponse {
  id: string;
  pre_registered_item_id: string;
  item_name: string;
  category_name: string;
  declared_quantity: number;
  previous_quantity: number;
  default_unit: string;
}

export interface InventorySummaryResponse {
  id: string;
  date: string;
  status: string;
  notes: string | null;
  item_count: number;
  created_at: string;
}

export interface InventoryDetailResponse {
  id: string;
  date: string;
  status: string;
  notes: string | null;
  items: InventoryItemResponse[];
  created_at: string;
  updated_at: string;
}

// Old Inventory (tied to shopping lists)
export interface InventoryResponse {
  id: string;
  shopping_list_id: string;
  pre_registered_item_id: string;
  item_name: string;
  declared_quantity: number;
  calculated_need: number;
}

// Shopping List
export interface ListItemResponse {
  id: string;
  pre_registered_item_id: string | null;
  custom_name: string | null;
  item_name: string;
  estimated_quantity: number;
  unit: string;
  checked: boolean;
  price_cents: number | null;
}

export interface ShoppingListResponse {
  id: string;
  name: string;
  status: string;
  store_id: string | null;
  store_name: string | null;
  completed_at: string | null;
  items: ListItemResponse[];
}

// Movement
export interface MovementResponse {
  id: string;
  sequential_code: string;
  item_name: string;
  quantity: number;
  unit: string;
  price_cents: number;
  store_name: string | null;
}

export interface CheckoutResponse {
  movements: MovementResponse[];
  list_status: string;
}
