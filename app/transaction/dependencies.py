# Transaction service currently reuses core dependencies.
# This module can host transaction‑specific dependencies in the future (e.g., transaction limits, fraud checks).
from app.core.dependencies import get_current_user, get_db