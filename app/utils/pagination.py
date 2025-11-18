"""Reusable pagination helpers."""

from __future__ import annotations

from math import ceil
from typing import Dict, Optional


def paginate_metadata(*, total: int, page: int, limit: int) -> Dict[str, int | bool]:
    """Return metadata block for paginated responses."""
    total_pages = max(ceil(total / limit), 1) if limit else 1
    return {
        "currentPage": page,
        "itemsPerPage": limit,
        "totalItems": total,
        "totalPages": total_pages,
        "hasNextPage": page < total_pages,
        "hasPreviousPage": page > 1,
    }
