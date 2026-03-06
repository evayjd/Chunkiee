from typing import Dict, List, Optional


def apply_metadata_filter(
    results: List[Dict],
    doc_id: Optional[str] = None,
    section: Optional[str] = None,
    page: Optional[int] = None,
) -> List[Dict]:

    filtered = []

    for r in results:

        if doc_id and r["doc_id"] != doc_id:
            continue
        meta = r.get("meta", {})

        if section and meta.get("section") != section:
            continue

        if page and meta.get("page_start") != page:
            continue

        filtered.append(r)

    return filtered