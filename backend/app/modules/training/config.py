"""
Phase 10B Training Configuration & Clinical Target Specifications.
"""

import os

# Base Directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

PARQUET_DATA_PATH = os.path.join(DATA_DIR, "merged_training_dataset.parquet")
FEATURE_DICT_PATH = os.path.join(DATA_DIR, "feature_dictionary.csv")
TARGET_DICT_PATH = os.path.join(DATA_DIR, "target_dictionary.csv")

# Ensure destination folders exist
for d in [MODELS_DIR, REPORTS_DIR]:
    os.makedirs(d, exist_ok=True)

# Phase 10B Clinical Deficiency Targets (in clinical order)
TARGETS = [
    'target_iron_deficiency',
    'target_iron_deficiency_anemia',
    'target_vitamin_d_deficiency',
    'target_vitamin_d_insufficiency',
    'target_folate_deficiency',
    'target_magnesium_deficiency',
    'target_selenium_deficiency',
    'target_potassium_deficiency',
    'target_calcium_deficiency'
]

TARGET_DISPLAY_NAMES = {
    'target_iron_deficiency': 'Iron Deficiency',
    'target_iron_deficiency_anemia': 'Iron Deficiency Anemia',
    'target_vitamin_d_deficiency': 'Vitamin D Deficiency',
    'target_vitamin_d_insufficiency': 'Vitamin D Insufficiency',
    'target_folate_deficiency': 'Folate Deficiency',
    'target_magnesium_deficiency': 'Magnesium Deficiency',
    'target_selenium_deficiency': 'Selenium Deficiency',
    'target_potassium_deficiency': 'Potassium Deficiency',
    'target_calcium_deficiency': 'Calcium Deficiency'
}

# Phase 10A Audited Class Imbalance scale_pos_weight
AUDITED_SCALE_POS_WEIGHTS = {
    'target_iron_deficiency': 1.60,
    'target_iron_deficiency_anemia': 5.53,
    'target_vitamin_d_deficiency': 3.65,
    'target_vitamin_d_insufficiency': 0.87,
    'target_folate_deficiency': 7.76,
    'target_magnesium_deficiency': 9.87,
    'target_selenium_deficiency': 28.52,
    'target_potassium_deficiency': 53.62,
    'target_calcium_deficiency': 137.30
}

# Cross-Validation Configuration
CV_SPLITS = 5
RANDOM_STATE = 42
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
