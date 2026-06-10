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
    page_title="AI Trip Planner",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling using glassmorphism and HSL-based palettes
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
        
        /* Apply global font and lock scrolling on the page */
        html, body, [class*="css"], .stApp {
            font-family: 'Outfit', sans-serif;
            background-color: #080710;
            color: #f6f8fc;
            overflow: hidden !important;
            height: 100vh !important;
        }
        
        /* Global layout height constraints to block browser scrollbars */
        div[data-testid="stAppViewContainer"], 
        section.main {
            height: 100vh !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stMainBlockContainer"] {
            max-width: 100% !important;
            padding: 5rem 2.5rem 1rem 2.5rem !important;
            height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            overflow: hidden !important;
        }
        
        /* Enforce flex layout on main vertical block */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] {
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            overflow: hidden !important;
            gap: 0px !important;
        }
        
        /* Title block */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:first-child {
            flex: 0 0 auto !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Columns block */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:nth-child(2) {
            flex: 1 1 auto !important;
            height: calc(100vh - 176px) !important;
            overflow: hidden !important;
        }
        
        /* Target columns under the main columns block */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:nth-child(2) > div[data-testid="stColumn"] {
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            overflow: hidden !important;
        }
        
        /* Smooth Entrance Animations */
        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(24px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .animated-section {
            animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        
        /* Custom card elements using Streamlit's native container borders */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(17, 22, 39, 0.65) !important;
            backdrop-filter: blur(14px) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 16px !important;
            padding: 20px !important;
            margin-bottom: 10px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            overflow: hidden !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: rgba(99, 102, 241, 0.4) !important;
            transform: translateY(-2px) scale(1.002) !important;
            box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15) !important;
        }
        
        /* Left Column Chat container styling */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:nth-child(2) > div[data-testid="stColumn"]:first-child div[data-testid="stVerticalBlockBorderWrapper"] {
            height: calc(100vh - 296px) !important;
            overflow-y: auto !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Right Column card container styling */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:nth-child(2) > div[data-testid="stColumn"]:last-child div[data-testid="stVerticalBlockBorderWrapper"] {
            height: calc(100vh - 331px) !important;
            overflow-y: auto !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Ensure image scales beautifully and doesn't exceed bounds */
        div[data-testid="stMainBlockContainer"] > div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"]:nth-child(2) > div[data-testid="stColumn"]:last-child div[data-testid="stVerticalBlockBorderWrapper"] img {
            border-radius: 12px !important;
            object-fit: cover !important;
            width: 100% !important;
            height: 100% !important;
            max-height: calc(100vh - 371px) !important;
            transition: transform 0.4s ease !important;
        }
        
        div[data-testid="stVerticalBlockBorderWrapper"]:hover div[data-testid="stImage"] img {
            transform: scale(1.03) !important;
        }
        
        /* Customize chat bubbles to match the design system */
        div[data-testid="stChatMessage"] {
            background-color: rgba(22, 28, 45, 0.45) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 12px !important;
            padding: 14px 18px !important;
            margin-bottom: 12px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        
        /* Typography responsiveness */
        @media (max-width: 768px) {
            h1, h2, h3, h4, h5 {
                font-size: calc(1.1rem + 0.5vw) !important;
            }
            div[data-testid="stVerticalBlockBorderWrapper"] {
                padding: 16px !important;
                height: auto !important;
            }
        }
        
        /* Badges & Tags */
        .badge {
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
            border: 1px solid rgba(129, 140, 248, 0.3);
            color: #a5b4fc;
            padding: 4px 12px;
            border-radius: 99px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
            margin-right: 6px;
            margin-bottom: 6px;
        }
        .rating-badge {
            background-color: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: #fbbf24;
            padding: 4px 12px;
            border-radius: 99px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 6px;
        }
        
        /* Header typography */
        .gradient-text {
            background: linear-gradient(135deg, #a5b4fc 0%, #a855f7 50%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        
        /* Invoice Receipt Design as a Premium Boarding Pass */
        .receipt-container {
            background: linear-gradient(135deg, #141124 0%, #08070f 100%);
            border: 1px solid rgba(139, 92, 246, 0.25);
            border-radius: 16px;
            padding: 28px;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow-y: auto !important;
            height: calc(100vh - 331px) !important;
            animation: slideUp 0.5s ease-out forwards;
        }
        .receipt-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #6366f1, #a855f7, #6366f1);
        }
        
        /* Sidebar styling override */
        section[data-testid="stSidebar"] {
            background-color: #06050a;
            border-right: 1px solid rgba(255, 255, 255, 0.04);
        }
        
        /* Align layout buttons and elements */
        div.stButton > button {
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            background-color: rgba(255, 255, 255, 0.03) !important;
            color: #f1f3f9 !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }
        div.stButton > button:hover {
            border-color: rgba(139, 92, 246, 0.5) !important;
            background-color: rgba(139, 92, 246, 0.1) !important;
            color: #c084fc !important;
            transform: translateY(-1px);
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
    if st.button("Reset Session State", width="stretch"):
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
        },
        {
            "type": "function",
            "function": {
                "name": "select_hotel",
                "description": "Update the right display pane to show a specific hotel's details and description.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hotel_id": {
                            "type": "string",
                            "description": "The name or ID of the hotel to display, e.g. 'Le Marais Boutique Hotel', 'plaza'."
                        }
                    },
                    "required": ["hotel_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "book_hotel",
                "description": "Book a specific hotel for the user. Requires hotel identifier, number of nights, and number of rooms.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "hotel_id": {
                            "type": "string",
                            "description": "The name or ID of the hotel to book, e.g. 'tokyo-luxury', 'The Aman Tokyo Oasis'."
                        },
                        "nights": {
                            "type": "integer",
                            "description": "The number of nights to book."
                        },
                        "rooms": {
                            "type": "integer",
                            "description": "The number of rooms to book."
                        }
                    },
                    "required": ["hotel_id", "nights", "rooms"]
                }
            }
        }
    ]

    system_message = (
        "You are an expert AI Travel Planner. Engage naturally with the user, "
        "and proactively attempt to extract their desired destination. "
        "When the user mentions or requests a travel destination (such as Tokyo, Paris, or New York), "
        "you MUST call the 'fetch_hotels' function to query the API. "
        "When the user indicates they want to book a hotel or see details for a hotel, you MUST call the 'select_hotel' function "
        "to update the display pane on the right. If the user has not specified both the number of nights and rooms, "
        "ask clarifying questions (e.g., 'How many nights and rooms would you like to stay?'). "
        "Once you have the hotel name/ID, number of nights, and number of rooms, you MUST call the 'book_hotel' function."
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
    st.markdown("## AI Trip Planner <span class='badge'>POC</span>", unsafe_allow_html=True)
with title_col2:
    st.markdown("<div style='text-align: right; margin-top: 10px;'><span class='badge'>Interactive Canvas</span></div>", unsafe_allow_html=True)

left_col, right_col = st.columns([1.2, 1])

# ================= LEFT COLUMN: CHAT ENGINE =================
with left_col:
    st.markdown("### Chat Assistant")
    
    # Create a container for messages to keep layout clean
    chat_container = st.container(height=410)
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
                                            f"I have successfully fetched hotels from the API for '{destination}'. "
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
                            elif tool_call.function.name == "book_hotel":
                                try:
                                    arguments = json.loads(tool_call.function.arguments)
                                    hotel_id = arguments.get("hotel_id", "")
                                    nights = int(arguments.get("nights", 1))
                                    rooms = int(arguments.get("rooms", 1))
                                    
                                    # Find hotel
                                    hotel = mock_data.find_hotel(hotel_id)
                                    
                                    if hotel:
                                        confirmation_id = f"TRIP-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))}"
                                        base_price = hotel["price_per_night"] * nights * rooms
                                        taxes = int(base_price * 0.12)
                                        total_price = base_price + taxes
                                        
                                        st.session_state.selected_hotel = hotel
                                        st.session_state.receipt = {
                                            "confirmation_id": confirmation_id,
                                            "hotel_name": hotel["name"],
                                            "destination": hotel["destination"].upper(),
                                            "price_per_night": hotel["price_per_night"],
                                            "nights": nights,
                                            "rooms": rooms,
                                            "base_price": base_price,
                                            "taxes": taxes,
                                            "total_price": total_price
                                        }
                                        st.session_state.step = "receipt"
                                        
                                        assistant_reply = (
                                            f"I have successfully booked '{hotel['name']}' for you. "
                                            f"Details: {nights} nights, {rooms} rooms. "
                                            "Your booking receipt has been generated in the visual display pane on the right!"
                                        )
                                    else:
                                        assistant_reply = (
                                            f"I tried to book '{hotel_id}', but could not find a hotel matching that identifier. "
                                            "Please check the available hotels list."
                                        )
                                        
                                    st.session_state.chat_history.append({"role": "assistant", "content": assistant_reply})
                                    st.rerun()
                                    
                                except Exception as parse_err:
                                    st.error(f"Failed to parse booking tool call: {str(parse_err)}")
                            elif tool_call.function.name == "select_hotel":
                                try:
                                    arguments = json.loads(tool_call.function.arguments)
                                    hotel_id = arguments.get("hotel_id", "")
                                    
                                    hotel = mock_data.find_hotel(hotel_id)
                                    if hotel:
                                        st.session_state.selected_hotel = hotel
                                        st.session_state.step = "detail_view"
                                        
                                        # Keep LLM assistant text response in sync if present
                                        if message.content:
                                            st.session_state.chat_history.append({"role": "assistant", "content": message.content})
                                        else:
                                            st.session_state.chat_history.append({
                                                "role": "assistant",
                                                "content": f"Showing details for {hotel['name']} on the right display panel. I can finalize this booking for you: just let me know how many nights and rooms you need!"
                                            })
                                        st.rerun()
                                except Exception as parse_err:
                                    st.error(f"Failed to parse select hotel tool call: {str(parse_err)}")
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
        
        if "dest_index" not in st.session_state:
            st.session_state.dest_index = 0
            
        destinations = mock_data.DESTINATIONS
        current_dest = destinations[st.session_state.dest_index]
        
        with st.container(border=True):
            col_img, col_info = st.columns([1.2, 2])
            with col_img:
                st.image(current_dest["image_url"], width="stretch")
            with col_info:
                st.markdown(f"<h4 style='margin: 0 0 4px 0;'>{current_dest['name']}</h4>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #a5b4fc; font-size: 0.85rem; margin: 0 0 10px 0;'>{current_dest['tagline']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 0.8rem; color: #cbd5e1; margin-bottom: 12px;'>{current_dest['description']}</p>", unsafe_allow_html=True)
                if st.button(f"Explore {current_dest['name']}", key=f"btn_explore_{current_dest['id']}", width="stretch"):
                    # Fetch hotels and update session state
                    hotels = mock_data.fetch_hotels(current_dest["name"])
                    st.session_state.current_hotels = hotels
                    st.session_state.selected_destination = current_dest["name"]
                    st.session_state.step = "search_results"
                    st.session_state.hotel_index = 0
                    
                    # Update Chat History to reflect this interaction
                    st.session_state.chat_history.append({"role": "user", "content": f"I want to explore hotels in {current_dest['name']}"})
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"Exploring hotels in {current_dest['name']}. You can view the list on the right pane."
                    })
                    st.rerun()
                    
        # Slider navigation controls
        col_prev, col_indicator, col_next = st.columns([1.2, 1.6, 1.2])
        with col_prev:
            if st.button("Previous", disabled=(st.session_state.dest_index == 0), key="dest_prev", width="stretch"):
                st.session_state.dest_index -= 1
                st.rerun()
        with col_indicator:
            st.markdown(f"<div style='text-align: center; margin-top: 6px; font-size: 0.85rem; color: #a5b4fc;'>{st.session_state.dest_index + 1} / {len(destinations)}</div>", unsafe_allow_html=True)
        with col_next:
            if st.button("Next", disabled=(st.session_state.dest_index == len(destinations) - 1), key="dest_next", width="stretch"):
                st.session_state.dest_index += 1
                st.rerun()

    # Step 2: Search Results
    elif st.session_state.step == "search_results":
        st.markdown(f"#### Hotels in {st.session_state.selected_destination}")
        
        if st.button("Back to Destinations", key="back_to_destinations", width="stretch"):
            st.session_state.step = "discovery"
            st.rerun()
            
        hotels = st.session_state.current_hotels
        if not hotels:
            st.info("No hotels found for this destination.")
        else:
            if "hotel_index" not in st.session_state:
                st.session_state.hotel_index = 0
            if st.session_state.hotel_index >= len(hotels):
                st.session_state.hotel_index = 0
                
            current_hotel = hotels[st.session_state.hotel_index]
            
            with st.container(border=True):
                col_img, col_info = st.columns([1.2, 2])
                with col_img:
                    st.image(current_hotel["image_url"], width="stretch")
                with col_info:
                    st.markdown(f"<h4 style='margin: 0 0 4px 0;'>{current_hotel['name']}</h4>", unsafe_allow_html=True)
                    st.markdown(f"""
                        <div style='margin-bottom: 8px;'>
                            <span class='rating-badge'>Rating: {current_hotel["rating"]}</span>
                            <span class='badge'>${current_hotel["price_per_night"]} / night</span>
                        </div>
                        <p style='font-size: 0.8rem; color: #cbd5e1; margin-bottom: 12px;'>{current_hotel["description"][:130]}...</p>
                    """, unsafe_allow_html=True)
                    if st.button(f"View details for {current_hotel['name']}", key=f"view_detail_{current_hotel['id']}", width="stretch"):
                        st.session_state.selected_hotel = current_hotel
                        st.session_state.step = "detail_view"
                        st.rerun()
                        
            # Slider navigation controls
            col_prev, col_indicator, col_next = st.columns([1.2, 1.6, 1.2])
            with col_prev:
                if st.button("Previous Hotel", disabled=(st.session_state.hotel_index == 0), key="hotel_prev", width="stretch"):
                    st.session_state.hotel_index -= 1
                    st.rerun()
            with col_indicator:
                st.markdown(f"<div style='text-align: center; margin-top: 6px; font-size: 0.85rem; color: #a5b4fc;'>{st.session_state.hotel_index + 1} / {len(hotels)}</div>", unsafe_allow_html=True)
            with col_next:
                if st.button("Next Hotel", disabled=(st.session_state.hotel_index == len(hotels) - 1), key="hotel_next", width="stretch"):
                    st.session_state.hotel_index += 1
                    st.rerun()

    # Step 3: Detail View
    elif st.session_state.step == "detail_view":
        hotel = st.session_state.selected_hotel
        
        st.markdown(f"#### {hotel['name']}")
        
        if st.button("Back to Search Results", key="back_to_search", width="stretch"):
            st.session_state.step = "search_results"
            st.rerun()
            
        with st.container(border=True):
            col_detail_left, col_detail_right = st.columns([1, 1])
            with col_detail_left:
                st.image(hotel["image_url"], width="stretch")
                st.markdown(f"""
                    <div style='margin-top: 10px; margin-bottom: 10px;'>
                        <span class='rating-badge'>Rating: {hotel["rating"]}</span>
                        <span class='badge'>${hotel["price_per_night"]} / night</span>
                    </div>
                    <p style='font-size: 0.8rem; color: #cbd5e1;'>{hotel["description"]}</p>
                """, unsafe_allow_html=True)
            with col_detail_right:
                st.markdown("##### Amenities & Booking")
                
                # Checkbox selection for amenities
                amenity_cols = st.columns(2)
                selected_amenities = {}
                for idx, amenity in enumerate(hotel["amenities"]):
                    col_idx = idx % 2
                    with amenity_cols[col_idx]:
                        selected_amenities[amenity] = st.checkbox(amenity, value=True, key=f"amenity_{amenity}")
                
                st.markdown("---")
                
                # Booking fields
                param_col1, param_col2 = st.columns(2)
                with param_col1:
                    nights = st.number_input("Nights", min_value=1, max_value=30, value=3, step=1)
                with param_col2:
                    rooms = st.number_input("Rooms", min_value=1, max_value=10, value=1, step=1)
                
                if st.button("Confirm Booking", key="confirm_booking", width="stretch"):
                    # Calculate receipt
                    confirmation_id = f"TRIP-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))}"
                    base_price = hotel["price_per_night"] * nights * rooms
                    taxes = int(base_price * 0.12)
                    total_price = base_price + taxes
                    
                    st.session_state.receipt = {
                        "confirmation_id": confirmation_id,
                        "hotel_name": hotel["name"],
                        "destination": st.session_state.selected_destination,
                        "price_per_night": hotel["price_per_night"],
                        "nights": nights,
                        "rooms": rooms,
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
<strong>Duration:</strong> {receipt["nights"]} Night(s)<br/>
<strong>Rooms:</strong> {receipt.get("rooms", 1)} Room(s)
</div>
<div style='border-top: 1px dashed rgba(255,255,255,0.2); padding-top: 12px; margin-top: 12px;'>
<div style='display: flex; justify-content: space-between;'>
<span>Base Cost ({receipt["nights"]} nights x {receipt.get("rooms", 1)} rooms x ${receipt["price_per_night"]}):</span>
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
        
        if st.button("Book Another Trip", key="book_another", width="stretch"):
            st.session_state.step = "discovery"
            st.session_state.selected_destination = None
            st.session_state.current_hotels = []
            st.session_state.selected_hotel = None
            st.session_state.receipt = None
            st.rerun()
