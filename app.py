import os
import random
import json
import streamlit as st
import openai
from dotenv import load_dotenv
import mock_data

# Load environment variables
load_dotenv()

# --- Page Configuration & Styling ---
st.set_page_config(
    page_title="AI Trip Planner | Layla.ai POC",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using glassmorphism and HSL-based palettes
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        /* Apply global font */
        html, body, [class*="css"], .stApp {
            font-family: 'Outfit', sans-serif;
            background-color: #0d0e15;
            color: #f1f3f9;
        }
        
        /* Custom card elements */
        .glass-card {
            background: rgba(22, 28, 45, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }
        .glass-card:hover {
            border-color: rgba(255, 255, 255, 0.2);
            transform: translateY(-2px);
        }
        
        /* Custom image framing */
        .hotel-image {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 12px;
        }
        
        .destination-image {
            width: 100%;
            height: 140px;
            object-fit: cover;
            border-radius: 12px;
            margin-bottom: 10px;
        }
        
        /* Badges & Tags */
        .badge {
            background-color: rgba(99, 102, 241, 0.2);
            color: #818cf8;
            padding: 4px 10px;
            border-radius: 99px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .rating-badge {
            background-color: rgba(245, 158, 11, 0.2);
            color: #fbbf24;
            padding: 4px 10px;
            border-radius: 99px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 6px;
        }
        
        /* Header typography */
        .gradient-text {
            background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
        }
        
        /* Invoice Receipt Design */
        .receipt-container {
            background: #111827;
            border: 1px dashed rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 24px;
            font-family: monospace;
            color: #e5e7eb;
        }
        
        /* Sidebar styling override */
        section[data-testid="stSidebar"] {
            background-color: #0b0c10;
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Align layout buttons and elements */
        div.stButton > button {
            border-radius: 8px !important;
            transition: all 0.2s ease;
        }
    </style>
""", unsafe_allow_html=True)

# --- State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "Hello! I am your AI Travel Planner. Where would you like to travel next? I can show you options in Tokyo, Paris, or New York."}
    ]

if "step" not in st.session_state:
    # Journey Steps: "discovery", "search_results", "detail_view", "receipt"
    st.session_state.step = "discovery"

if "selected_destination" not in st.session_state:
    st.session_state.selected_destination = None

if "current_hotels" not in st.session_state:
    st.session_state.current_hotels = []

if "selected_hotel" not in st.session_state:
    st.session_state.selected_hotel = None

if "receipt" not in st.session_state:
    st.session_state.receipt = None

# --- Sidebar Configuration ---
with st.sidebar:
    st.markdown("### <span class='gradient-text'>Settings & API Configuration</span>", unsafe_allow_html=True)
    st.markdown("This proof-of-concept integrates with OpenRouter for natural language parsing and smart destination routing.")
    
    # Check if API Key is in environment
    env_key = os.getenv("OPENROUTER_API_KEY")
    if env_key:
        st.success("OpenRouter API Key found in environment variables.")
        api_key = env_key
    else:
        user_key = st.text_input("Enter your OpenRouter API Key", type="password", help="Get a key from openrouter.ai")
        if user_key:
            st.session_state.openrouter_key = user_key
            api_key = user_key
        else:
            st.warning("Please enter your OpenRouter API Key to chat with the LLM.")
            api_key = ""

    st.markdown("---")
    st.markdown("### Reset Application")
    if st.button("Reset Session State", use_container_width=True):
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I am your AI Travel Planner. Where would you like to travel next? I can show you options in Tokyo, Paris, or New York."}
        ]
        st.session_state.step = "discovery"
        st.session_state.selected_destination = None
        st.session_state.current_hotels = []
        st.session_state.selected_hotel = None
        st.session_state.receipt = None
        st.rerun()

# --- LLM Communication Layer (OpenRouter) ---
def call_openrouter_api(messages):
    """Calls OpenRouter with function calling capabilities."""
    if not api_key:
        return {"error": "API Key is missing. Please configure it in the sidebar or environment variables."}

    client = openai.OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "fetch_hotels",
                "description": "Fetch a list of available hotels for a specific travel destination.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "destination": {
                            "type": "string",
                            "description": "The destination city or region, e.g. 'Tokyo', 'Paris', 'New York'."
                        }
                    },
                    "required": ["destination"]
                }
            }
        }
    ]

    system_message = (
        "You are an expert AI Travel Planner inspired by Layla.ai. Engage naturally with the user, "
        "and proactively attempt to extract their desired destination. "
        "When the user mentions or requests a travel destination (such as Tokyo, Paris, or New York), "
        "you MUST call the 'fetch_hotels' function to query the system database. "
        "Do not write down hypothetical hotel listings yourself. Let the function call handle the data retrieval."
    )

    full_messages = [{"role": "system", "content": system_message}] + messages

    try:
        response = client.chat.completions.create(
            model="nex-agi/nex-n2-pro:free",
            messages=full_messages,
            tools=tools,
            tool_choice="auto"
        )
        return response
    except Exception as e:
        return {"error": str(e)}

# --- Split-Screen UI Layout ---
title_col1, title_col2 = st.columns([1, 1])
with title_col1:
    st.markdown("## ✈️ AI Trip Planner <span class='badge'>POC</span>", unsafe_allow_html=True)
with title_col2:
    st.markdown("<div style='text-align: right; margin-top: 10px;'><span class='badge'>Interactive Canvas</span></div>", unsafe_allow_html=True)

left_col, right_col = st.columns([1.2, 1])

# ================= LEFT COLUMN: CHAT ENGINE =================
with left_col:
    st.markdown("### Chat Assistant")
    
    # Create a container for messages to keep layout clean
    chat_container = st.container(height=550)
    with chat_container:
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # User chat input
    user_input = st.chat_input("Ask about destinations or specific hotels...")

    if user_input:
        # Append and display user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with chat_container:
            with st.chat_message("user"):
                st.write(user_input)

        if not api_key:
            st.error("OpenRouter API key is missing. Please add it in the sidebar.")
        else:
            with st.spinner("Thinking..."):
                # Call OpenRouter API
                response = call_openrouter_api(st.session_state.chat_history)
                
                if isinstance(response, dict) and "error" in response:
                    st.error(f"API Error: {response['error']}")
                else:
                    # Parse response
                    choice = response.choices[0]
                    message = choice.message
                    
                    # Check for tool calls
                    if message.tool_calls:
                        for tool_call in message.tool_calls:
                            if tool_call.function.name == "fetch_hotels":
                                try:
                                    arguments = json.loads(tool_call.function.arguments)
                                    destination = arguments.get("destination", "")
                                    
                                    # Fetch hotels
                                    hotels = mock_data.fetch_hotels(destination)
                                    
                                    if hotels:
                                        st.session_state.current_hotels = hotels
                                        st.session_state.selected_destination = destination
                                        st.session_state.step = "search_results"
                                        
                                        assistant_reply = (
                                            f"I have successfully searched the database for hotels in '{destination}'. "
                                            "Please check the right display panel to browse the available properties!"
                                        )
                                    else:
                                        assistant_reply = (
                                            f"I searched for hotels in '{destination}', but we do not have mock data "
                                            "for that region. Please select Tokyo, Paris, or New York."
                                        )
                                        
                                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                                    st.rerun()
                                    
                                except Exception as parse_err:
                                    st.error(f"Failed to parse tool call: {str(parse_err)}")
                    else:
                        # Standard text response
                        st.session_state.chat_history.append({"role": "assistant", "content": message.content})
                        st.rerun()

# ================= RIGHT COLUMN: DYNAMIC VISUAL DISPLAY =================
with right_col:
    st.markdown("### Visual Explorer")

    # Step 1: Discovery
    if st.session_state.step == "discovery":
        st.markdown("#### Featured Destinations")
        st.markdown("Select a featured destination to begin exploring hotels:")
        
        # Display destinations in a 3-column layout
        dest_cols = st.columns(3)
        for idx, dest in enumerate(mock_data.DESTINATIONS):
            with dest_cols[idx]:
                st.markdown(
                    f"""
                    <div class='glass-card'>
                        <img class='destination-image' src='{dest["image_url"]}' alt='{dest["name"]}' />
                        <h4 style='margin: 8px 0 4px 0;'>{dest["name"]}</h4>
                        <p style='font-size: 0.85rem; color: #a5b4fc; margin-bottom: 12px;'>{dest["tagline"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(f"Explore {dest['name']}", key=f"btn_explore_{dest['id']}", use_container_width=True):
                    # Fetch hotels and update session state
                    hotels = mock_data.fetch_hotels(dest["name"])
                    st.session_state.current_hotels = hotels
                    st.session_state.selected_destination = dest["name"]
                    st.session_state.step = "search_results"
                    
                    # Update Chat History to reflect this interaction
                    st.session_state.chat_history.append({"role": "user", "content": f"I want to explore hotels in {dest['name']}"})
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"Exploring hotels in {dest['name']}. You can view the list on the right pane."
                    })
                    st.rerun()

    # Step 2: Search Results
    elif st.session_state.step == "search_results":
        st.markdown(f"#### Hotels in {st.session_state.selected_destination}")
        
        if st.button("← Back to Destinations", key="back_to_destinations", use_container_width=True):
            st.session_state.step = "discovery"
            st.rerun()
            
        if not st.session_state.current_hotels:
            st.info("No hotels found for this destination.")
        else:
            for hotel in st.session_state.current_hotels:
                st.markdown(
                    f"""
                    <div class='glass-card'>
                        <img class='hotel-image' src='{hotel["image_url"]}' alt='{hotel["name"]}' />
                        <h4 style='margin: 8px 0 4px 0;'>{hotel["name"]}</h4>
                        <div style='margin-bottom: 10px;'>
                            <span class='rating-badge'>★ {hotel["rating"]}</span>
                            <span class='badge'>${hotel["price_per_night"]} / night</span>
                        </div>
                        <p style='font-size: 0.9rem; color: #cbd5e1;'>{hotel["description"][:120]}...</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(f"View details for {hotel['name']}", key=f"view_detail_{hotel['id']}", use_container_width=True):
                    st.session_state.selected_hotel = hotel
                    st.session_state.step = "detail_view"
                    st.rerun()

    # Step 3: Detail View
    elif st.session_state.step == "detail_view":
        hotel = st.session_state.selected_hotel
        
        st.markdown(f"#### {hotel['name']}")
        
        if st.button("← Back to Search Results", key="back_to_search", use_container_width=True):
            st.session_state.step = "search_results"
            st.rerun()
            
        st.markdown(
            f"""
            <div class='glass-card'>
                <img class='hotel-image' src='{hotel["image_url"]}' alt='{hotel["name"]}' />
                <div style='margin-bottom: 12px;'>
                    <span class='rating-badge'>★ {hotel["rating"]}</span>
                    <span class='badge'>${hotel["price_per_night"]} / night</span>
                </div>
                <p style='margin-bottom: 16px;'>{hotel["description"]}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("##### Included Amenities")
        selected_amenities = {}
        for amenity in hotel["amenities"]:
            selected_amenities[amenity] = st.checkbox(amenity, value=True, key=f"amenity_{amenity}")
            
        st.markdown("---")
        
        # Select booking parameters
        nights = st.number_input("Number of Nights", min_value=1, max_value=30, value=3, step=1)
        
        if st.button("Confirm Booking", key="confirm_booking", use_container_width=True):
            # Calculate receipt
            confirmation_id = f"TRIP-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))}"
            base_price = hotel["price_per_night"] * nights
            taxes = int(base_price * 0.12)
            total_price = base_price + taxes
            
            st.session_state.receipt = {
                "confirmation_id": confirmation_id,
                "hotel_name": hotel["name"],
                "destination": st.session_state.selected_destination,
                "price_per_night": hotel["price_per_night"],
                "nights": nights,
                "base_price": base_price,
                "taxes": taxes,
                "total_price": total_price
            }
            st.session_state.step = "receipt"
            
            # Update Chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"Booking confirmed at '{hotel['name']}'! Your booking receipt has been generated in the visual display panel."
            })
            st.rerun()

    # Step 4: Receipt
    elif st.session_state.step == "receipt":
        receipt = st.session_state.receipt
        
        st.markdown("#### Booking Receipt")
        
        st.markdown(
            f"""<div class='receipt-container'>
<div style='text-align: center; border-bottom: 1px dashed rgba(255,255,255,0.2); padding-bottom: 12px; margin-bottom: 16px;'>
<h3 style='margin: 0; color: #818cf8;'>BOOKING CONFIRMATION</h3>
<p style='margin: 4px 0 0 0; font-size: 0.9rem;'>CONFIRMATION ID: {receipt["confirmation_id"]}</p>
</div>
<div style='margin-bottom: 12px;'>
<strong>Hotel:</strong> {receipt["hotel_name"]}<br/>
<strong>Destination:</strong> {receipt["destination"]}<br/>
<strong>Duration:</strong> {receipt["nights"]} Night(s)
</div>
<div style='border-top: 1px dashed rgba(255,255,255,0.2); padding-top: 12px; margin-top: 12px;'>
<div style='display: flex; justify-content: space-between;'>
<span>Base Cost ({receipt["nights"]} x ${receipt["price_per_night"]}):</span>
<span>${receipt["base_price"]}</span>
</div>
<div style='display: flex; justify-content: space-between; margin-top: 6px;'>
<span>Taxes & Fees (12%):</span>
<span>${receipt["taxes"]}</span>
</div>
<div style='display: flex; justify-content: space-between; margin-top: 12px; border-top: 1px dashed rgba(255,255,255,0.2); padding-top: 8px; font-weight: bold; font-size: 1.1rem; color: #818cf8;'>
<span>TOTAL CHARGED:</span>
<span>${receipt["total_price"]}</span>
</div>
</div>
<div style='text-align: center; margin-top: 20px; font-size: 0.8rem; color: #9ca3af;'>
Thank you for booking with AI Trip Planner!
</div>
</div>""",
            unsafe_allow_html=True
        )
        
        if st.button("Book Another Trip", key="book_another", use_container_width=True):
            st.session_state.step = "discovery"
            st.session_state.selected_destination = None
            st.session_state.current_hotels = []
            st.session_state.selected_hotel = None
            st.session_state.receipt = None
            st.rerun()
