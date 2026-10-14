export interface User {
  id: number;
  email: string;
  full_name: string | null;
  role: 'user' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  latitude: number | null;
  longitude: number | null;
  preferred_radius_km: number;
  created_at: string;
  last_login: string | null;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface Supermarket {
  id: number;
  name: string;
  brand: string | null;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  latitude: number | null;
  longitude: number | null;
  phone: string | null;
  website: string | null;
  opening_hours: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  distance_km?: number;
  prices_count?: number;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  parent_id: number | null;
  icon: string | null;
  sort_order: number;
  is_active: boolean;
  children?: Category[];
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  brand: string | null;
  barcode: string | null;
  image_url: string | null;
  unit: string;
  unit_size: number | null;
  category_id: number | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  category?: Category;
  current_prices?: Price[];
}

export interface Price {
  id: number;
  product_id: number;
  supermarket_id: number;
  price: string; // Decimal as string
  original_price: string | null;
  is_promotion: boolean;
  promotion_label: string | null;
  promotion_end_date: string | null;
  currency: string;
  source_url: string | null;
  is_available: boolean;
  scraped_at: string;
  product?: Product;
  supermarket?: Supermarket;
}

export interface PriceComparison {
  product: Product;
  prices: Price[];
  cheapest: Price | null;
  most_expensive: Price | null;
  average_price: string;
  price_spread: string;
}

export interface PriceHistoryPoint {
  date: string;
  price: string;
  original_price: string | null;
  is_promotion: boolean;
  supermarket_id: number;
  supermarket_name: string;
}

export interface PriceHistory {
  product_id: number;
  product_name: string;
  history: PriceHistoryPoint[];
  period_days: number;
}

export interface PriceAlert {
  id: number;
  user_id: number;
  product_id: number;
  supermarket_id: number | null;
  target_price: string;
  current_price: string | null;
  is_active: boolean;
  notify_email: boolean;
  notify_push: boolean;
  last_triggered_at: string | null;
  created_at: string;
  updated_at: string;
  product?: Product;
  supermarket?: Supermarket;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ProductSearchParams {
  query?: string;
  category_id?: number;
  brand?: string;
  barcode?: string;
  min_price?: string;
  max_price?: string;
  supermarket_id?: number;
  city?: string;
  latitude?: number;
  longitude?: number;
  radius_km?: number;
  is_promotion?: boolean;
  in_stock_only?: boolean;
  sort_by?: 'price_asc' | 'price_desc' | 'relevance' | 'newest';
  page?: number;
  page_size?: number;
}