def get_pagination(page: int, page_size: int, total: int) -> tuple[int, int]:
    skip = (page - 1) * page_size
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return skip, total_pages
