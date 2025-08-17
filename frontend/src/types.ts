export interface Card {
  id: number;
  scryfall_id: string;
  name: string;
  mana_cost?: string;
  cmc?: number;
  type_line?: string;
  oracle_text?: string;
  power?: string;
  toughness?: string;
  colors?: string[];
  color_identity?: string[];
  keywords?: string[];
  image_filename?: string;
  num_colors?: number;
  color_sort_key?: string;
  // Target app fields
  rating?: number;
  rating_deviation?: number;
  volatility?: number;
  image_uris?: {
    normal?: string;
    large?: string;
    border_crop?: string;
    art_crop?: string;
    png?: string;
    small?: string;
  };
  card_faces?: Array<{
    name?: string;
    image_uris?: {
      normal?: string;
      large?: string;
    };
  }>;
  layout?: string;
  created_at?: string;
  updated_at?: string;
}

export interface KernelCard {
  id: number;
  card: Card;
  added_at: string;
}

export interface Kernel {
  id: number;
  name: string;
  order: number;
  created_at: string;
  updated_at: string;
  cards: KernelCard[];
  card_count: number;
}

export interface CandidateCard {
  id: number;
  card: Card;
}