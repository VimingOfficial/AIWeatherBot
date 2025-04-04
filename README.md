 You can read the published article (story) on Medium: [Building AIWeatherBot: An AI-Powered Telegram Weather Bot to Start Your Day](https://medium.com/@AmiraliPouyanrad/building-aiweatherbot-an-ai-powered-telegram-weather-bot-to-start-your-day-2cc272a5295a)
# WeatherBot v2.0.0 🌤️
### AI-Powered & Multi-Language Weather Update🚀
**WeatherBot** is a **multi-language** Telegram bot that provides **AI-powered** daily weather updates for selected cities. With **AI-enhanced insights**, users can get more detailed weather analysis alongside hourly weather data. Whether you're in **English 🇬🇧** or **Persian 🇮🇷**, WeatherBot has got you covered. Subscribers receive daily weather reports and can manually request weather updates anytime.

# Features :white_check_mark:
- **AI-Powered Weather Insights:** Get AI-generated weather commentary for each city.
- **Multi-Language Support:** Choose between English and Persian. More languages can be added easily!
- **Daily Weather Updates:** Weather reports sent at 5:30 AM every day (you can customize the time).
- **Manual Report Command:** Request an instant weather report with the `/report` command.
- **Easy Subscription:** Use `/start` to subscribe and `/stop` to unsubscribe.
- **Customizable Cities:** Modify the cities in the code to fetch data for other locations.
- **Optimized Performance:** Enhanced speed and reliability with AI integration and efficient data handling.

# Installation :envelope_with_arrow:
### Prerequisites
- [Python](python.org) 3.8+
- Telegram Bot Token: Obtain it by creating a bot on [BotFather](t.me/BotFather).
- OpenWeather API Key: Sign up at [OpenWeather](https://openweathermap.org/) to get a free API key.
- Gemini API Key: Get gemini [api key](https://aistudio.google.com/apikey) for ai response.

### Setup
1. **Clone the repository:**
   ```
   git clone https://github.com/VimingOfficial/AIWeatherBot.git
   cd AIWeatherBot
   ```
2. **Install the required Python packages:**

   ```
   pip install -r requirements.txt
   ```
   **or**
   
   ```
   pip install python-telegram-bot requests PyYAML google-generativeai asyncio
   ```
3. **Replace the `YOUR_BOT_TOKEN`, `YOUR_WEATHERMAP_API` and `GEMENI_API` in weather.py with your actual Telegram bot token, OpenWeather API key and gemini API key.**

# Usage :desktop_computer:	
1. **Run the Bot:**

   ```
   python weather.py
   ```
   **on Linux servers**
   
   ```
   nohup python3 weather.py &
   ```
   > [!NOTE]
   > On Linux servers you can use this line to keep it running
2. **Commands:**
- `/start`: Subscribe to daily weather updates at 5:30 AM (you can customize the time).
- `/stop`: Unsubscribe from daily weather updates.
- `/report`: Request an instant weather report with the latest data for the specified hours.

# Customization :memo:
1. **Change Cities:** Modify the cities list in weather.py to add or change cities for weather reports.
2. **Change Report Time:** Adjust the time in run_scheduler if you need the report at a different time than 5:30 AM.

# Example Output :arrow_forward:	
 🌤 weather report (2025-03-20)

📍 Newyork
<br>
Newyork: clear sky, 26.6°C, 0kph
<br>
🤖 AI Response:
The weather in Newyork is pleasant and mild. With a clear sky and a temperature of 26.6°C, it's a nice, sunny day. The absence of wind (0 kph) suggests a very still and calm atmosphere. Overall, it sounds like a comfortable day in Newyork.

📍 Tehran
<br>
Tehran: scattered clouds, 15.7°C, 1.03kph
<br>
🤖 AI Response:
The weather in Tehran sounds quite pleasant. It's 15.7°C, which is a mild temperature, and there are only scattered clouds, suggesting a relatively bright day with some sun. The wind is very light at 1.03 kph, so it's unlikely to be windy. Overall, it's a nice day to be outdoors.

# Changelog - v2.0.0 🚀
- **AI-Powered Insights:** WeatherBot now provides AI-enhanced weather analysis for each city.
- **Multi-Language Support:** Users can select between English and Persian for the interface and reports.
- **Optimized User Experience:** Enhanced message handling and smoother interactions.
- **Performance Improvements:** Faster weather data fetching and better error handling.
