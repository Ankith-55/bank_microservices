# Account service currently reuses core dependencies.
# This module can host account‑specific dependencies in the future (e.g., rate limiting, ownership checks).
from app.core.dependencies import get_current_user, get_db