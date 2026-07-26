def filter_profile_data(full_data: dict, fields: str) -> dict:
    if not fields or fields.lower() == "all":
        return full_data
    req_fields = [f.strip().lower() for f in fields.split(",")]
    
    filtered = {"username": full_data["username"], "meta": full_data["meta"]}
    for field in req_fields:
        if field in full_data and field not in ["username", "meta"]:
            filtered[field] = full_data[field]
    return filtered