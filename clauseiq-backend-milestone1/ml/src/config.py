from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Dataset
DATA_FILE = PROJECT_ROOT / "clauses_final.csv"

# Output directories
MODEL_DIR = PROJECT_ROOT / "ml" / "models"
REPORT_DIR = PROJECT_ROOT / "ml" / "reports"

# CSV columns
TEXT_COLUMN = "text"
LABEL_COLUMN = "label"
SPLIT_COLUMN = "split"

# Eight ClauseIQ categories
CATEGORIES = [
    "Privacy",
    "Financial",
    "Cancellation",
    "Data",
    "Intellectual Property",
    "Contractual",
    "Account",
    "Changes",
]

RANDOM_STATE = 42