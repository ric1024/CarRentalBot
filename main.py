import os
from dotenv import load_dotenv
from apify_client import ApifyClient

# 1. Load your secret API key from the .env file
load_dotenv()
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

def find_hidden_rentals(location):
    print(f"Searching for local car rentals in {location}...")
    
    # 2. Updated input: Separating search terms from location
    run_input = {
        "searchStringsArray": ["car rental"],
        "locationQuery": location,
        "maxCrawledPlacesPerSearch": 5,
    }

    # 3. Use the verified 2026 Actor ID
    run = client.actor("compass/crawler-google-places").call(run_input=run_input)

    # 4. Fetch and print the results
    print("\n--- RESULTS FOUND ---")
    
    # We check the 'defaultDatasetId' where the results are stored
    results = client.dataset(run["defaultDatasetId"]).list_items().items
    
    if not results:
        print("No results found. Try a broader location or check your API credits.")
    
    for item in results:
        name = item.get("title")
        rating = item.get("totalScore")
        address = item.get("address")
        
        # This checks if it's a 'Hidden Gem' (Good rating but not a massive chain)
        is_big_chain = any(chain in name.lower() for chain in ["hertz", "enterprise", "avis", "budget", "sixt"])
        
        status = " [LOCAL GEM]" if not is_big_chain and (rating and rating >= 4.0) else ""
        
        print(f"FOUND: {name}{status}")
        print(f"   Rating: {rating} | Address: {address}\n")

# 5. Run the bot!
find_hidden_rentals("Brooklyn, NY")