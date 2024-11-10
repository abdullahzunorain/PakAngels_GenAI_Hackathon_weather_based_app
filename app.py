import requests
import streamlit as st
import groq

# Access API keys from Streamlit secrets
openweather_api_key = st.secrets["weather_api_key"]
groq_api_key = st.secrets["groq_api_key"]

# Function to get weather data from OpenWeatherMap
def get_weather_data(city):
    api_key = openweather_api_key  # Use the secret API key
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
        return response.json()
    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error occurred: {err}")
    except Exception as err:
        st.error(f"An error occurred: {err}")
    return None

# Function to parse weather data and categorize weather
def parse_weather_data(weather_data):
    temperature = weather_data["main"]["temp"]
    weather_description = weather_data["weather"][0]["description"]
    return temperature, weather_description

# Categorizing weather conditions
def categorize_weather(description):
    description = description.lower()
    if "clear" in description or "sun" in description:
        return "Sunny", "☀️"
    elif "rain" in description or "drizzle" in description or "shower" in description:
        return "Rainy", "🌧️"
    elif "snow" in description or "sleet" in description:
        return "Cold", "❄️"
    elif "cloud" in description:
        return "Cloudy", "☁️"
    elif "wind" in description:
        return "Windy", "💨"
    elif "smoke" in description or "haze" in description:
        return "Smoky", "🌫️"
    else:
        return "Uncategorized", "🔍"

# Function to get outfit suggestion using Groq's LLaMA model
def get_outfit_suggestion(temperature, description, style, fabric, weather_category, weather_icon, time_of_day, activity):
    # Initialize Groq's API
    try:
        client = groq.Groq(api_key=groq_api_key)  # Use the secret API key
        
        # Adjust the prompt based on the weather category
        prompt = f"The current weather is {description} with a temperature of {temperature}°C. The weather category is {weather_category}. The time of day is {time_of_day} and the user is planning to do {activity}. Suggest an outfit. The user prefers a {style} style and {fabric} fabric."

        # Use Groq's chat completion to get the text response
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",  # Change to a valid Groq model if necessary
        )
        return response.choices[0].message.content.strip(), weather_icon
    except Exception as e:
        st.error(f"Error using Groq API: {e}")
        return None, None

# Streamlit UI for user input
st.set_page_config(page_title="Weather-Based Outfit Suggestion", page_icon="🌤️", layout="wide")

# Custom styles
st.markdown("""<style>
    .reportview-container {
        background: linear-gradient(135deg, #ffcc00, #ff7b00);
    }
    .stButton>button {
        background-color: #ff5733;
        color: white;
        font-size: 18px;
        border-radius: 10px;
        padding: 10px;
    }
    .stTextInput input {
        font-size: 16px;
        padding: 10px;
        border-radius: 10px;
    }
    .stSelectbox select {
        font-size: 16px;
        padding: 10px;
        border-radius: 10px;
    }
    .stWrite, .stImage {
        font-family: "Arial", sans-serif;
        font-size: 18px;
        color: #333;
    }
    .weather-header {
        text-align: center;
        font-size: 36px;
        color: #ffffff;
        font-family: "Arial", sans-serif;
    }
    .outfit-header {
        font-size: 24px;
        color: #444;
        font-family: "Arial", sans-serif;
        margin-top: 30px;
    }
    .left-column {
        padding-right: 20px;
    }
    .right-column {
        padding-left: 20px;
    }
</style>""", unsafe_allow_html=True)

# Title and layout for columns
st.title("🌤️ Weather-Based Outfit Suggestion App")

# Create two columns: one for the user input and one for displaying results
col1, col2 = st.columns([1, 2])  # 1: left column (user input), 2: right column (outfit suggestions)

# User input in the left column (col1)
with col1:
    city = st.text_input("Enter your location:", placeholder="E.g. Peshawar")
    gender = st.selectbox("Select your gender", ["Male", "Female"])
    personalized_style = st.text_input("Enter your personalized style (optional)", placeholder="E.g. Peshawari")
    fabric = st.selectbox("Select your preferred fabric", ["Cotton", "Linen", "Wool", "Polyester", "Silk", "Leather"])
    time_of_day = st.selectbox("Select time of day", ["Morning", "Afternoon", "Evening"])
    activity = st.selectbox("Select your activity", ["Work", "Outdoor", "Casual", "Exercise", "Other"])

# Result display in the right column (col2)
with col2:
    if city:
        with st.spinner("Fetching weather data..."):
            weather_data = get_weather_data(city)
        
        if weather_data and weather_data["cod"] == 200:
            temperature, description = parse_weather_data(weather_data)
            # Categorize the weather
            weather_category, weather_icon = categorize_weather(description)

            # Display current weather info
            st.write(f"Current temperature in {city}: {temperature}°C")
            st.write(f"Weather: {description} {weather_icon}")
            st.write(f"Weather Category: {weather_category} {weather_icon}")

            # Get outfit suggestion based on user preferences
            outfit_suggestion, weather_icon = get_outfit_suggestion(temperature, description, personalized_style, fabric, weather_category, weather_icon, time_of_day, activity)

            if outfit_suggestion:
                # Display outfit suggestion
                st.markdown(f"### 🌟 Outfit Suggestion 🌟")
                st.write(outfit_suggestion)
                
                # Additional section for Health and Comfort Tips
                st.markdown(f"### 🌿 Health & Comfort Tips 🌿")
                st.write(f"Given the {weather_category} weather, it's important to take care of your health:")
                st.write("- **Breathing**: A face mask or scarf covering your nose and mouth can help protect you from smoke inhalation.")
                st.write("- **Hydration**: Keep a water bottle with you, as smoke can dehydrate your body.")
                st.write("- **Rest**: Try to avoid strenuous activity outdoors and take breaks if you're feeling fatigued.")
                st.write("- **Eyes**: If you're feeling irritated, use eye drops to soothe any discomfort caused by smoke.")
            
            # Display weather icon
            icon_code = weather_data["weather"][0]["icon"]
            icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
            st.image(icon_url)
        else:
            st.write("Could not retrieve weather data. Please check the location.")







# import requests
# import streamlit as st
# import groq

# # Access API keys from Streamlit secrets
# openweather_api_key = st.secrets["weather_api_key"]
# groq_api_key = st.secrets["groq_api_key"]

# # Function to get weather data from OpenWeatherMap
# def get_weather_data(city):
#     api_key = openweather_api_key  # Use the secret API key
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
#         return response.json()
#     except requests.exceptions.HTTPError as err:
#         st.error(f"HTTP error occurred: {err}")
#     except Exception as err:
#         st.error(f"An error occurred: {err}")
#     return None

# # Function to parse weather data and categorize weather
# def parse_weather_data(weather_data):
#     temperature = weather_data["main"]["temp"]
#     weather_description = weather_data["weather"][0]["description"]
#     return temperature, weather_description

# # Categorizing weather conditions
# def categorize_weather(description):
#     description = description.lower()
#     if "clear" in description or "sun" in description:
#         return "Sunny", "☀️"
#     elif "rain" in description or "drizzle" in description or "shower" in description:
#         return "Rainy", "🌧️"
#     elif "snow" in description or "sleet" in description:
#         return "Cold", "❄️"
#     elif "cloud" in description:
#         return "Cloudy", "☁️"
#     elif "wind" in description:
#         return "Windy", "💨"
#     elif "smoke" in description or "haze" in description:
#         return "Smoky", "🌫️"
#     else:
#         return "Uncategorized", "🔍"

# # Function to get outfit suggestion using Groq's LLaMA model
# def get_outfit_suggestion(temperature, description, style, fabric, weather_category, weather_icon):
#     # Initialize Groq's API
#     try:
#         client = groq.Groq(api_key=groq_api_key)  # Use the secret API key
        
#         # Adjust the prompt based on the weather category
#         prompt = f"The current weather is {description} with a temperature of {temperature}°C. The weather category is {weather_category}. Suggest an outfit. The user prefers a {style} style and {fabric} fabric."

#         # Use Groq's chat completion to get the text response
#         response = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama3-8b-8192",  # Change to a valid Groq model if necessary
#         )
#         return response.choices[0].message.content.strip(), weather_icon
#     except Exception as e:
#         st.error(f"Error using Groq API: {e}")
#         return None, None

# # Streamlit UI for user input
# st.set_page_config(page_title="Weather-Based Outfit Suggestion", page_icon="🌤️", layout="wide")

# # Custom styles
# st.markdown("""<style>
#     .reportview-container {
#         background: linear-gradient(135deg, #ffcc00, #ff7b00);
#     }
#     .stButton>button {
#         background-color: #ff5733;
#         color: white;
#         font-size: 18px;
#         border-radius: 10px;
#         padding: 10px;
#     }
#     .stTextInput input {
#         font-size: 16px;
#         padding: 10px;
#         border-radius: 10px;
#     }
#     .stSelectbox select {
#         font-size: 16px;
#         padding: 10px;
#         border-radius: 10px;
#     }
#     .stWrite, .stImage {
#         font-family: "Arial", sans-serif;
#         font-size: 18px;
#         color: #333;
#     }
#     .weather-header {
#         text-align: center;
#         font-size: 36px;
#         color: #ffffff;
#         font-family: "Arial", sans-serif;
#     }
#     .outfit-header {
#         font-size: 24px;
#         color: #444;
#         font-family: "Arial", sans-serif;
#         margin-top: 30px;
#     }
#     .left-column {
#         padding-right: 20px;
#     }
#     .right-column {
#         padding-left: 20px;
#     }
# </style>""", unsafe_allow_html=True)

# # Title and layout for columns
# st.title("🌤️ Weather-Based Outfit Suggestion App")

# # Create two columns: one for the user input and one for displaying results
# col1, col2 = st.columns([1, 2])  # 1: left column (user input), 2: right column (outfit suggestions)

# # User input in the left column (col1)
# with col1:
#     city = st.text_input("Enter your location:", placeholder="E.g. Peshawar")
#     gender = st.selectbox("Select your gender", ["Male", "Female"])
#     personalized_style = st.text_input("Enter your personalized style (optional)", placeholder="E.g. Peshawari")
#     fabric = st.selectbox("Select your preferred fabric", ["Cotton", "Linen", "Wool", "Polyester", "Silk", "Leather"])

# # Result display in the right column (col2)
# with col2:
#     if city:
#         weather_data = get_weather_data(city)
        
#         if weather_data and weather_data["cod"] == 200:
#             temperature, description = parse_weather_data(weather_data)
#             # Categorize the weather
#             weather_category, weather_icon = categorize_weather(description)

#             # Display current weather info
#             st.write(f"Current temperature in {city}: {temperature}°C")
#             st.write(f"Weather: {description} {weather_icon}")
#             st.write(f"Weather Category: {weather_category} {weather_icon}")

#             # Get outfit suggestion based on user preferences
#             outfit_suggestion, weather_icon = get_outfit_suggestion(temperature, description, personalized_style, fabric, weather_category, weather_icon)

#             if outfit_suggestion:
#                 # Display outfit suggestion
#                 st.markdown(f"### 🌟 Outfit Suggestion 🌟")
#                 st.write(outfit_suggestion)
                
#                 # Additional section for Health and Comfort Tips
#                 st.markdown(f"### 🌿 Health & Comfort Tips 🌿")
#                 st.write(f"Given the {weather_category} weather, it's important to take care of your health:")
#                 st.write("- **Breathing**: A face mask or scarf covering your nose and mouth can help protect you from smoke inhalation.")
#                 st.write("- **Hydration**: Keep a water bottle with you, as smoke can dehydrate your body.")
#                 st.write("- **Rest**: Try to avoid strenuous activity outdoors and take breaks if you're feeling fatigued.")
#                 st.write("- **Eyes**: If you're feeling irritated, use eye drops to soothe any discomfort caused by smoke.")
            
#             # Display weather icon
#             icon_code = weather_data["weather"][0]["icon"]
#             icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
#             st.image(icon_url)
#         else:
#             st.write("Could not retrieve weather data. Please check the location.")


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# import requests
# import streamlit as st
# import groq
# import os

# # Function to get weather data from OpenWeatherMap

# import os

# # Replace with environment variables
# openweather_api_key = os.getenv("weather_api_key")
# groq_api_key = os.getenv("groq_api_key")


# def get_weather_data(city):
#     api_key = openweather_api_key  # Replace with your OpenWeatherMap API key
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an HTTPError if the HTTP request returned an unsuccessful status code
#         return response.json()
#     except requests.exceptions.HTTPError as err:
#         st.error(f"HTTP error occurred: {err}")
#     except Exception as err:
#         st.error(f"An error occurred: {err}")
#     return None

# # Function to parse weather data
# def parse_weather_data(weather_data):
#     temperature = weather_data["main"]["temp"]
#     weather_description = weather_data["weather"][0]["description"]
#     return temperature, weather_description

# # Function to get outfit suggestion using Groq's LLaMA model
# def get_outfit_suggestion(temperature, description, style, fabric):
#     # Initialize Groq's API
#     try:
#         client = groq.Groq(api_key=groq_api_key)  # Replace with your Groq API key
        
#         prompt = f"The current weather is {description} with a temperature of {temperature}°C. Suggest an outfit. The user prefers a {style} style and {fabric} fabric."

#         # Use Groq's chat completion to get the text response
#         response = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama3-8b-8192",  # Change to a valid Groq model if necessary
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         st.error(f"Error using Groq API: {e}")
#         return None

# # Streamlit UI for user input
# st.title("Weather-Based Outfit Suggestion App")

# city = st.text_input("Enter your location:")

# # Add style and fabric input options
# style = st.selectbox("Select your preferred style", ["Casual", "Formal", "Sporty", "Business", "Chic"])
# fabric = st.selectbox("Select your preferred fabric", ["Cotton", "Linen", "Wool", "Polyester", "Silk", "Leather"])

# if city:
#     weather_data = get_weather_data(city)
    
#     if weather_data and weather_data["cod"] == 200:
#         temperature, description = parse_weather_data(weather_data)
        
#         # Display current weather info
#         st.write(f"Current temperature in {city}: {temperature}°C")
#         st.write(f"Weather: {description}")
        
#         # Get outfit suggestion based on user preferences
#         outfit_suggestion = get_outfit_suggestion(temperature, description, style, fabric)
        
#         if outfit_suggestion:
#             # Display outfit suggestion
#             st.write("Outfit Suggestion:")
#             st.write(outfit_suggestion)
        
#         # Display weather icon
#         icon_code = weather_data["weather"][0]["icon"]
#         icon_url = f"http://openweathermap.org/img/wn/{icon_code}.png"
#         st.image(icon_url)
#     else:
#         st.write("Could not retrieve weather data. Please check the location.")
        
# # Optional: Add CSS for styling
# st.markdown(
#     """
#     <style>
#     .reportview-container {
#         background: #f5f5f5;
#     }
#     .stButton>button {
#         background-color: #ff5733;
#         color: white;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True
# )
