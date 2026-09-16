export const NUTRIENTS = [
  'Protein', 'Vitamin A', 'Vitamin B12', 'Folate', 'Vitamin C',
  'Vitamin D', 'Vitamin E', 'Iron', 'Calcium', 'Zinc', 'Magnesium',
  'Vitamin B1', 'Vitamin B2', 'Vitamin B3', 'Vitamin B6',
  'Potassium', 'Selenium', 'Iodine'
] as const

export type NutrientName = typeof NUTRIENTS[number]

export const NUTRIENT_ICONS: Record<string, string> = {
  'Protein': '🥩',
  'Vitamin A': '🥕',
  'Vitamin B12': '🐟',
  'Folate': '🥬',
  'Vitamin C': '🍊',
  'Vitamin D': '☀️',
  'Vitamin E': '🥑',
  'Iron': '🩸',
  'Calcium': '🦴',
  'Zinc': '⚡',
  'Magnesium': '💎',
  'Vitamin B1': '🌾',
  'Vitamin B2': '🥛',
  'Vitamin B3': '🍄',
  'Vitamin B6': '🍌',
  'Potassium': '🥔',
  'Selenium': '🌰',
  'Iodine': '🧂',
}

export const RISK_COLORS = {
  LOW: { bg: '#DCFCE7', text: '#166534', fill: '#16A34A' },
  MODERATE: { bg: '#FEF3C7', text: '#92400E', fill: '#F59E0B' },
  HIGH: { bg: '#FEE2E2', text: '#991B1B', fill: '#DC2626' },
  SEVERE: { bg: '#FEE2E2', text: '#991B1B', fill: '#DC2626' },
} as const

export const DIET_PATTERNS = [
  { value: 'OMNIVORE', label: 'Omnivore' },
  { value: 'VEGETARIAN', label: 'Vegetarian' },
  { value: 'VEGAN', label: 'Vegan' },
  { value: 'PESCATARIAN', label: 'Pescatarian' },
  { value: 'KETO', label: 'Keto' },
  { value: 'PALEO', label: 'Paleo' },
  { value: 'MEDITERRANEAN', label: 'Mediterranean' },
  { value: 'OTHER', label: 'Other' },
] as const

export const ACTIVITY_LEVELS = [
  { value: 'SEDENTARY', label: 'Sedentary' },
  { value: 'LIGHTLY_ACTIVE', label: 'Lightly Active' },
  { value: 'MODERATELY_ACTIVE', label: 'Moderately Active' },
  { value: 'VERY_ACTIVE', label: 'Very Active' },
  { value: 'EXTRA_ACTIVE', label: 'Extra Active' },
] as const

export const SYMPTOM_LIST = [
  { key: 'fatigue', label: 'Fatigue / Low Energy' },
  { key: 'hair_loss', label: 'Hair Loss' },
  { key: 'muscle_weakness', label: 'Muscle Weakness' },
  { key: 'bone_pain', label: 'Bone Pain' },
  { key: 'pale_skin', label: 'Pale Skin' },
  { key: 'brittle_nails', label: 'Brittle Nails' },
  { key: 'muscle_cramps', label: 'Muscle Cramps' },
  { key: 'numbness_tingling', label: 'Numbness / Tingling' },
  { key: 'slow_wound_healing', label: 'Slow Wound Healing' },
  { key: 'frequent_infections', label: 'Frequent Infections' },
  { key: 'mood_changes', label: 'Mood Changes / Irritability' },
  { key: 'brain_fog', label: 'Brain Fog / Poor Concentration' },
  { key: 'irritability', label: 'Irritability & Restlessness' },
  { key: 'poor_appetite', label: 'Poor Appetite / Anorexia' },
  { key: 'cracked_lips', label: 'Cracked Lips / Angular Cheilitis' },
  { key: 'eye_irritation', label: 'Eye Irritation / Photophobia' },
  { key: 'dermatitis', label: 'Dermatitis & Skin Rashes' },
  { key: 'digestive_disturbances', label: 'Digestive Disturbances' },
  { key: 'irregular_heartbeat', label: 'Irregular Heartbeat / Palpitations' },
  { key: 'thyroid_dysfunction', label: 'Thyroid Dysfunction Symptoms' },
  { key: 'unexplained_weight_gain', label: 'Unexplained Weight Gain' },
] as const
