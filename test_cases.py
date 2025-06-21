# -------------------------------
# Example Test Cases for parse_hike_preferences
# -------------------------------

# Test 1: Terrain + Intensity + Public Transport
# Expected:
# origin_city: "Glasgow"
# max_travel_time_minutes: 150
# station_keywords: []
# soft_preferences: ["challenging", "scrambling", "ridge walking", "accessible by public transport"]
# user_prompt:
# "Looking for a challenging hike accessible by train from Glasgow, ideally with scrambling sections and some ridge walking. Under 2.5 hours travel time would be ideal."

# Test 2: Named Stations + Scenery + Quiet
# Expected:
# origin_city: null
# max_travel_time_minutes: null
# station_keywords: ["Corrour", "Bridge of Orchy"]
# soft_preferences: ["quiet", "scenic", "remote"]
# user_prompt:
# "Are there any quiet, scenic day hikes starting from Corrour or Bridge of Orchy? I’d like to avoid busy trails and get a remote feel."

# Test 3: Weather + Suitability + Beginner
# Expected:
# origin_city: "Edinburgh"
# max_travel_time_minutes: 90
# station_keywords: []
# soft_preferences: ["suitable for poor weather", "dog-friendly", "beginner-friendly"]
# user_prompt:
# "Please recommend beginner-friendly hikes from Edinburgh that are good in poor weather and dog-friendly. I don’t mind taking the train up to 90 minutes."

# Test 4: Specific Scenery + Terrain Constraints
# Expected:
# origin_city: "Glasgow"
# max_travel_time_minutes: 120
# station_keywords: []
# soft_preferences: ["coastal", "forest", "flat", "well-marked", "solo-hiker suitable"]
# user_prompt:
# "I want to find a coastal hike with forest sections, preferably flat and well-marked, as I’ll be going solo. Starting from Glasgow, reachable within 2 hours by train."

# Test 5: Multi-day + Child-friendly + Remote
# Expected:
# origin_city: null
# max_travel_time_minutes: null
# station_keywords: ["Rannoch", "Crianlarich"]
# soft_preferences: ["multi-day", "child-friendly", "remote"]
# user_prompt:
# "Looking to plan a multi-day remote hiking trip that’s also suitable for kids. Ideally starting near Rannoch or Crianlarich. Doesn’t need to be difficult, but should feel wild."
