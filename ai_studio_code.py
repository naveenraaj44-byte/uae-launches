import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
import re
from datetime import datetime

STYLES = """
<style>
    .project-card {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #333;
        transition: transform 0.2s;
    }
    .project-card:hover {
        transform: scale(1.02);
        border-color: #FF4B4B;
    }
    .tier-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8em;
        font-weight: bold;
        color: white;
    }
    .tier-1 { background-color: #FFD700; color: black; }
    .tier-2 { background-color: #C0C0C0; color: black; }
    .tier-3 { background-color: #CD7F32; color: black; }
    
    .price-tag {
        color: #4CAF50;
        font-weight: bold;
        font-size: 1.1em;
    }
    .details {
        color: #B0B0B0;
        font-size: 0.9em;
        margin-top: 5px;
    }
</style>
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

class TierManager:
    @staticmethod
    def process_brands(df):
        if 'Brand Name' not in df.columns:
            return None
            
        brands_data = []
        for idx, row in df.iterrows():
            rank = idx + 1
            brand_name = row['Brand Name']
            tier = row['Tier']
            region = row['Main Region']
                
            brands_data.append({
                "Brand": brand_name,
                "Rank": rank,
                "Tier": tier,
                "Region": region
            })
            
        return pd.DataFrame(brands_data)

class LaunchScraper:
    def __init__(self):
        self.base_rss = "https://news.google.com/rss/search?q={query}&hl=en-AE&gl=AE&ceid=AE:en"

    def _extract_details(self, text):
        units = re.findall(r'\b(\d+\s?(?:BR|Bedroom|Bed)|Penthouse|Villa|Townhouse)\b', text, re.IGNORECASE)
        price = re.search(r'(AED\s?[\d,.]+\s?[MK]?)', text, re.IGNORECASE)
        locations = ["Downtown Dubai", "Business Bay", "Palm Jumeirah", "Dubai Hills", "Yas Island"]
        loc_found = "UAE (General)"
        for loc in locations:
            if loc.lower() in text.lower():
                loc_found = loc
                break

        return {
            "unit_types": list(set(units)) if units else ["TBD"],
            "price": price.group(0) if price else "Price on Request",
            "location": loc_found
        }

    def fetch_launches(self, brand_name):
        query = f"{brand_name} real estate launch UAE"
        url = self.base_rss.format(query=query)
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')
                
                launches = []
                for item in items[:2]:
                    title = item.title.text
                    link = item.link.text
                    pub_date = item.pubDate.text
                    details = self._extract_details(title)
                    
                    launches.append({
                        "project_name": title.split('-')[0].strip(),
                        "url": link,
                        "date": pub_date,
                        "image": f"https://source.unsplash.com/800x600/?skyscraper,architecture&sig={random.randint(1,1000)}",
                        "units": random.randint(50, 500),
                        **details
                    })
                return launches
        except Exception as e:
            st.error(f"Error scraping {brand_name}: {e}")
            return []
        return []

    def generate_mock_data(self, brands_df):
        mock_launches = []
        locations = ["Palm Jumeirah", "Dubai Creek", "Yas Island", "Business Bay"]
        unit_types = ["1BR, 2BR", "3BR, Penthouses", "Villas", "Studios"]
        
        for _, row in brands_df.iterrows():
            if random.choice([True, False]): 
                mock_launches.append({
                    "developer": row['Brand'],
                    "tier": row['Tier'],
                    "project_name": f"{row['Brand']} Residences {random.choice(['View', 'Heights', 'Bay', 'Grove'])}",
                    "location": random.choice(locations),
                    "price": f"AED {random.randint(1, 20)}.{random.randint(1,9)}M",
                    "unit_types": random.choice(unit_types),
                    "units": random.randint(100, 800),
                    "image": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=1000",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "url": "#"
                })
        return mock_launches

def main():
    st.set_page_config(page_title="UAE Developer Launch Tracker", layout="wide")
    st.markdown(STYLES, unsafe_allow_html=True)

    st.sidebar.title("Launch Tracker Config")
    
    uploaded_file = st.sidebar.file_uploader("Upload Developers CSV", type=["csv"])
    
    if uploaded_file is None:
        st.sidebar.info("Loading default dataset from Developers.csv")
        try:
            df_brands = pd.read_csv("Developers.csv")
        except:
            st.error("Could not load Developers.csv file")
            return
    else:
        df_brands = pd.read_csv(uploaded_file)

    tm = TierManager()
    tiered_brands = tm.process_brands(df_brands)
    
    if tiered_brands is None:
        st.error("CSV file must have 'Brand Name', 'Tier', and 'Main Region' columns")
        return
    
    st.sidebar.header("Filters")
    available_tiers = tiered_brands['Tier'].unique().tolist()
    selected_tiers = st.sidebar.multiselect(
        "Select Tiers", 
        available_tiers,
        default=available_tiers
    )
    
    data_source = st.sidebar.radio("Data Source", ["Mock Data (Demo)", "Live Scrape (Google News)"])
    
    if st.sidebar.button("Refresh Feed"):
        st.rerun()

    st.title("UAE Real Estate - Developer Launch Tracker")
    st.markdown("Monitoring latest project launches across Top 50 UAE Developers.")
    st.divider()

    scraper = LaunchScraper()
    
    with st.spinner('Fetching latest launch data...'):
        if data_source == "Mock Data (Demo)":
            all_launches = scraper.generate_mock_data(tiered_brands)
        else:
            target_brands = tiered_brands[tiered_brands['Tier'].isin(selected_tiers)]
            all_launches = []
            progress_bar = st.progress(0)
            total = len(target_brands)
            
            for i, row in target_brands.iterrows():
                brand_launches = scraper.fetch_launches(row['Brand'])
                for launch in brand_launches:
                    launch['developer'] = row['Brand']
                    launch['tier'] = row['Tier']
                    all_launches.append(launch)
                progress_bar.progress((i + 1) / total)
                time.sleep(0.5)
            
            progress_bar.empty()

    display_data = [x for x in all_launches if x['tier'] in selected_tiers]
    
    st.write(f"Found {len(display_data)} launches")
    
    if not display_data:
        st.warning("No recent launches found for selected tiers. Try Mock Data mode.")
    else:
        cols = st.columns(3)
        for idx, launch in enumerate(display_data):
            col = cols[idx % 3]
            
            with col:
                st.image(launch['image'], use_column_width=True)
                st.subheader(launch['project_name'])
                st.write(f"**Developer:** {launch['developer']}")
                st.write(f"**Tier:** {launch['tier']}")
                st.write(f"**Price:** {launch['price']}")
                st.write(f"**Location:** {launch['location']}")
                st.write(f"**Units:** {launch['units']}")
                st.write(f"**Types:** {launch['unit_types']}")

if __name__ == "__main__":
    main()
