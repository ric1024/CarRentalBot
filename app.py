import streamlit as st
import os
from dotenv import load_dotenv
from apify_client import ApifyClient

# Load secret API key
load_dotenv()
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

# Page Setup
st.set_page_config(page_title="Hidden Gem Rentals", page_icon="🚗")

# Branding & USP
st.title("🚗 Hidden Gem Car Rentals")
st.markdown("### Find local shops that **Expedia** and **Kayak** miss.")
st.write("We scan local directories to find high-rated, non-chain rentals.")

# Input Field
location = st.text_input("Enter City and State/Country:", placeholder="e.g. Newark, NJ or Paris, France")

if st.button("Search for Hidden Gems"):
    if location:
        # The 'Pro-tip' nudge for accuracy
        if "," not in location:
            st.warning("⚠️ Pro-tip: Adding a state or country (like 'Newark, NJ') helps find the exact right spot!")
            
        with st.spinner(f"Scraping local deals in {location}..."):
            run_input = {
                "searchStringsArray": ["car rental"],
                "locationQuery": location,
                "maxCrawledPlacesPerSearch": 10, 
            }
            
            # Call the AI Scraper
            run = client.actor("compass/crawler-google-places").call(run_input=run_input)
            results = client.dataset(run["defaultDatasetId"]).list_items().items

            if results:
                st.subheader(f"Curated Results for {location}")
                found_any_gems = False 
                
                for item in results:
                    name = item.get("title", "")
                    # Convert rating to float for comparison
                    raw_rating = item.get("totalScore") or item.get("rating") or 0
                    try:
                        rating = float(raw_rating)
                    except ValueError:
                        rating = 0
                    
                    address = item.get("address") or "Address available on map"
                    website = item.get("website")
                    phone = item.get("phoneNumber")
                    
                    # 1. BULLETPROOF FILTER: The "No-Go" list
                    big_guys = [
                        "hertz", "enterprise", "avis", "budget", "sixt", 
                        "alamo", "national", "thrifty", "dollar", "fox", 
                        "payless", "ace rent a car", "europcar"
                    ]
                    is_big_chain = any(chain in name.lower() for chain in big_guys)
                    
                    # 2. RELEVANCE FILTER: Kills insurance agents like "Greg Daniels"
                    rental_keywords = ["rental", "rent", "car", "auto", "hire", "wheels", "vehicle"]
                    is_relevant = any(word in name.lower() for word in rental_keywords)
                    
                    # THE GATEKEEPER LOGIC: Must be NOT a chain AND Relevant AND 4.0+ Stars
                    if not is_big_chain and is_relevant and rating >= 4.0:
                        found_any_gems = True
                        with st.expander(f"{name} — ⭐ {rating}"):
                            st.caption("✓ Verified Independent Local Business")
                            
                            st.write(f"**📍 Address:** {address}")
                            st.write(f"**⭐ Rating:** {rating} / 5")
                            
                            if phone:
                                st.write(f"**📞 Phone:** {phone}")
                            
                            # Create layout for buttons
                            col1, col2 = st.columns(2)
                            with col1:
                                if website:
                                    st.link_button("🌐 Go to Website", website)
                            with col2:
                                google_maps_url = f"https://www.google.com/maps/search/{name.replace(' ', '+')}+{location.replace(' ', '+')}"
                                st.link_button("📍 View on Maps", google_maps_url)
                
                # --- MONETIZATION BLOCK ---
                st.divider()
                st.subheader("🚀 Travel Like a Pro")
                st.write("Want to master independent rentals anywhere in the world? Grab my **Global Local's Car Rental Playbook** for insider tips and a framework to avoid the 'tourist' markups.")
                st.link_button("Get the Playbook ($7)", "https://jobreadyhq.gumroad.com/l/vuyfve")
                
                if not found_any_gems:
                    st.info("We found rentals, but none met our strict 'Independent Rental' criteria. Try a nearby city!")
            else:
                st.warning("No results found. Try being more specific with the City and State.")
    else:
        st.error("Please enter a location first!")