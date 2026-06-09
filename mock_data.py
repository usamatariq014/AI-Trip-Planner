# Mock dataset simulating a local travel API

DESTINATIONS = [
    {
        "id": "tokyo",
        "name": "Tokyo",
        "tagline": "Neon lights and ancient temples",
        "image_url": "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80",
        "description": "Experience the perfect blend of ultra-modern technology and centuries-old culture in Japan's bustling capital."
    },
    {
        "id": "paris",
        "name": "Paris",
        "tagline": "The city of light and romance",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80",
        "description": "Immerse yourself in world-class art, culinary masterpieces, and the historic charm of the Seine riverbanks."
    },
    {
        "id": "new-york",
        "name": "New York",
        "tagline": "The concrete jungle that never sleeps",
        "image_url": "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80",
        "description": "Explore iconic skyscrapers, Broadway shows, Central Park, and the melting pot of cultures in the Big Apple."
    }
]

HOTELS = [
    # Tokyo Hotels
    {
        "id": "tokyo-luxury",
        "name": "The Aman Tokyo Oasis",
        "destination": "tokyo",
        "price_per_night": 950,
        "rating": 4.9,
        "amenities": ["Wi-Fi", "Infinity Pool", "Luxury Spa", "24/7 Butler Service", "Sushi Bar"],
        "image_url": "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?auto=format&fit=crop&w=800&q=80",
        "description": "Perched high above Otemachi, this sanctuary combines traditional design with modern luxury, offering panoramic views of Mount Fuji on clear days."
    },
    {
        "id": "tokyo-boutique",
        "name": "Shibuya Stream Hotel",
        "destination": "tokyo",
        "price_per_night": 320,
        "rating": 4.5,
        "amenities": ["Wi-Fi", "Fitness Center", "Co-working Space", "Rooftop Terrace"],
        "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
        "description": "A vibrant boutique hotel in the heart of Shibuya, perfect for creative minds looking to explore the city's fashion and nightlife."
    },
    
    # Paris Hotels
    {
        "id": "paris-palace",
        "name": "Hôtel Plaza Athénée",
        "destination": "paris",
        "price_per_night": 1200,
        "rating": 4.9,
        "amenities": ["Wi-Fi", "Michelin Restaurant", "Dior Spa", "Chauffeur Service", "Balcony Views"],
        "image_url": "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?auto=format&fit=crop&w=800&q=80",
        "description": "Located on the prestigious Avenue Montaigne, this legendary palace features iconic red awnings and offers haute couture service."
    },
    {
        "id": "paris-charming",
        "name": "Le Marais Boutique Hotel",
        "destination": "paris",
        "price_per_night": 280,
        "rating": 4.4,
        "amenities": ["Wi-Fi", "Complimentary Breakfast", "Bicycle Rental", "Courtyard Garden"],
        "image_url": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?auto=format&fit=crop&w=800&q=80",
        "description": "Nestled in the historic Marais district, this chic hotel offers cobblestone courtyard charm and steps-away access to local bakeries."
    },
    
    # New York Hotels
    {
        "id": "ny-iconic",
        "name": "The Plaza Hotel Fifth Avenue",
        "destination": "ny", # Let's support both 'ny' and 'new-york' in destination matching
        "price_per_night": 850,
        "rating": 4.8,
        "amenities": ["Wi-Fi", "Champagne Bar", "Spa & Wellness", "Valet Parking", "Concierge"],
        "image_url": "https://images.unsplash.com/photo-1582719508461-905c673771fd?auto=format&fit=crop&w=800&q=80",
        "description": "An iconic luxury hotel since 1907, situated at Central Park South, defining timeless elegance and historic charm."
    },
    {
        "id": "ny-loft",
        "name": "The Beekman Soho",
        "destination": "ny",
        "price_per_night": 390,
        "rating": 4.6,
        "amenities": ["Wi-Fi", "Rooftop Lounge", "Pet Friendly", "Craft Cocktail Bar"],
        "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?auto=format&fit=crop&w=800&q=80",
        "description": "Featuring a breathtaking 9-story Victorian atrium and eclectic vintage decor, located near the vibrant neighborhoods of Soho and Tribeca."
    }
]

# Helper function to match destination string to API
def fetch_hotels(destination_query: str):
    q = destination_query.lower().strip()
    # Normalize destination queries
    target = None
    if "tokyo" in q:
        target = "tokyo"
    elif "paris" in q:
        target = "paris"
    elif "new york" in q or "ny" in q or "manhattan" in q or "brooklyn" in q:
        target = "ny"
        
    if not target:
        return []
        
    return [h for h in HOTELS if h["destination"] == target]
