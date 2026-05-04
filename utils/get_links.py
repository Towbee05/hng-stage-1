def get_links (page, limit, total_pages):
    prev_link = f"/api/profiles?page={page-1}&limit={limit}" if page > 1 else "null"
    next_link = f"/api/profiles?page={page+1}&limit={limit}" if (page+1) <= total_pages else "null"
    current_link = f"/api/profiles?page={page}&limit={limit}"

    return prev_link, next_link, current_link
        