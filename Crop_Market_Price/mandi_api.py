import requests

def fetch_mandi_price(crop, state):
    url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

    params = {
        "api-key": "579b464db66ec23bdd00000150041bf3896d4ea44854721eb39463de",
        "format": "json",
        "filters[commodity]": crop,
        "filters[state]": state,
        "limit": 20
    }

    response = requests.get(url, params=params)

    try:
        data = response.json()
    except:
        return "API did not return JSON"

    if "records" not in data:
        return "No data found"

    results = []

    for item in data["records"]:
        results.append({
            "Market": item.get("market", ""),
            "Commodity": item.get("commodity", ""),
            "Variety": item.get("variety", ""),
            "Min Price": item.get("min_price", ""),
            "Max Price": item.get("max_price", ""),
            "Modal Price": item.get("modal_price", ""),
            "Date": item.get("arrival_date", "")
        })

    return results
