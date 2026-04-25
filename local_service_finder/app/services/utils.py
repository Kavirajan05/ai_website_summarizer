def clean_business_data(data_list: list) -> list:
    cleaned = []
    seen = set()
    
    for item in data_list:
        name = item.get("name")
        address = item.get("address", "")
        
        # Use name + first part of address for de-duplication
        unique_key = f"{name}_{address[:20]}".lower()
        
        if not name or unique_key in seen:
            continue
        
        rating = item.get("rating", 0)
        # Re-enable high quality filtering
        # Filter out low rated entries if they have at least 1 review
        if rating > 0 and rating < 3.5:
            continue
            
        seen.add(unique_key)
        cleaned.append(item)
    
    # Sort by Rating then review count
    cleaned.sort(key=lambda x: (x.get("rating", 0), x.get("reviews_count", 0)), reverse=True)
    
    # Return top 20
    return cleaned[:20]
