import requests
from datetime import datetime, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import yaml
from google import genai
import asyncio

# Add your own bot token and openweathermap API
BOT_TOKEN = 'YOUR_BOT_TOKEN'
API_KEY = 'YOUR_WEATHERMAP_API'
AI_API = 'GEMENI_API'


messages_cache = {}

def refresh_language(user_id, lang):
    language_code = "persian" if lang == "fa" else "english"
    messages = load_language(language_code)

    if messages is not None:
        messages_cache[user_id] = messages
    else:
        messages_cache[user_id] = {"error": "❌ Error loading language file."}



def load_language(lang):
    try:
        with open(f"languages/{lang}.yaml", "r", encoding="utf-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return None

user_cities = {}
cities={}
user_language = {}
client = genai.Client(api_key=AI_API)

def save_user_city(user_id, city):
    if user_id not in user_cities:
        user_cities[user_id] = []
    if city not in user_cities[user_id]:
        user_cities[user_id].append(city)


def remove_user_city(user_id, city):
    if user_id in user_cities and city in user_cities[user_id]:
        user_cities[user_id].remove(city)

def get_user_cities(user_id):
    return user_cities.get(user_id, [])

async def request_cities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    messages = messages_cache.get(user_id, {})
    await update.message.reply_text(messages.get("enter_cities", "Please enter your cities one by one. Send /done when finished."))

async def add_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    messages = messages_cache.get(user_id, {})
    if not args:
        await update.message.reply_text(f"{messages["ecode"]}❌ {messages["Please specify a city. Example /addcity Tehran"]}")
        return
    city = " ".join(args)
    save_user_city(user_id, city)
    await update.message.reply_text(f"{messages["ecode"]}✅ '{city}' {messages["has been added to your city list. Use /mycities to see your list"]}")

async def remove_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    messeges = messages_cache.get(user_id, {})
    if not args:
        await update.message.reply_text(f"{messeges["ecode"]}❌ {messeges["Please specify a city to remove. Example /removecity Tehran"]}")
        return

    city = " ".join(args)
    if city in get_user_cities(user_id):
        remove_user_city(user_id, city)
        await update.message.reply_text(f"{messeges["ecode"]}✅ '{city}' {messeges["has been removed"]}")
    else:
        await update.message.reply_text(f"{messeges["ecode"]}⚠️ '{city}' {messeges["was not found in your list"]}")

async def list_user_cities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cities = get_user_cities(user_id)
    messeges = messages_cache.get(user_id, {})
    if not cities:
        await update.message.reply_text(f"{messeges["ecode"]}⚠️ {messeges["You haven't added any cities yet. Use /addcity to add one"]}")
    else:
        await update.message.reply_text(f"{messeges["ecode"]}✅ {messeges["Your selected cities"]}: {', '.join(cities)}")

async def done_adding_cities(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cities = get_user_cities(user_id)

    if not cities:
        await update.message.reply_text("⚠️ You haven't added any cities yet. Please enter at least one.")
    else:
        await update.message.reply_text(f"✅ Your selected cities: {', '.join(cities)}")


def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        wind_speed = data["wind"]["speed"]
        weather_info=f"{city}: {weather_desc}, {temp}°C, {wind_speed}kph"
        return weather_info
    else:
        return f"Could not retrieve weather data for {city}."


def get_ai_response(city, weather_info, user_id):
    messages = messages_cache.get(user_id, {})

    if "ai_language" not in messages:
        return "Error: Language file missing or incorrect."

    ai_language = messages["ai_language"]
    prompt = f"{messages["ecode"]}Comment on the weather in {city}, which is as follows: {weather_info}. respond in {ai_language}. \n You are a highly skilled meteorologist and weather analyst. Your task is to provide detailed and insightful weather reports based on the given data. You should analyze temperature, humidity, wind speed, precipitation, and other relevant factors to deliver an accurate and professional weather forecast.\n In your response, follow this structure: \n Weather Overview: Start with a general summary of the weather, including temperature, wind conditions, and the chance of rain or snow. \n Detailed Analysis: Explain weather patterns such as high or low-pressure systems, expected changes, and how the current conditions might evolve throughout the day.\nImpact on Daily Life: Suggest how the weather may affect outdoor activities, commuting, and overall comfort.\nClothing Recommendations: Based on the weather conditions, recommend appropriate attire, such as wearing light clothing for hot weather, layering for cold conditions, or carrying an umbrella for rainy days.\nSafety Tips: If extreme weather is expected (e.g., storms, heatwaves, snowfall), offer useful precautions and advice.\n be friendly with user\nYour tone should be informative yet engaging, making it easy for users to understand and prepare for the day. Be precise, avoid unnecessary repetition, and ensure clarity in your explanations.\n you should respond in {ai_language}."

    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)

    if response and hasattr(response, 'text'):
        return response.text
    else:
        return f"{messages["ecode"]}❌ {messages["Error in generating AI response"]}"


def get_weather_report(user_id):
    messages = messages_cache.get(user_id, {})
    weather_report_text=f"{messages["ecode"]}🌤{messages["weather report"]}"
    ai_response_text=f"{messages["ecode"]}🤖{messages["AI Response"]}"
    report = f" {weather_report_text} ({datetime.now().strftime('%Y-%m-%d')})\n"
    for city in cities:
        weather_info = get_weather(city)
        ai_response = get_ai_response(city, weather_info, user_id)
        report += f"\n📍 {city}\n{weather_info}\n{ai_response_text}\n{ai_response}\n"
    return report


async def send_weather_report(context: ContextTypes.DEFAULT_TYPE):
    report = get_weather_report()
    for chat_id in subscribed_users:
        await context.bot.send_message(chat_id=chat_id, text=report)


subscribed_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in subscribed_users:
        subscribed_users.add(chat_id)
    keyboard = [
    [InlineKeyboardButton("🇮🇷 فارسی", callback_data='fa')],
    [InlineKeyboardButton("English 🇬🇧", callback_data='en')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Please choose your language:\nلطفا زبان خود را انتخاب کنید:",
        reply_markup=reply_markup
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    messages = messages_cache.get(user_id, {})
    if chat_id in subscribed_users:
        subscribed_users.remove(chat_id)
        await update.message.reply_text(messages["You have unsubscribed from daily weather updates"])
    else:
        await update.message.reply_text(messages["You are not subscribed"])


async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id 
    messages = messages_cache.get(user_id, {})
    cities = get_user_cities(user_id)
    if user_id not in user_language:
        await update.message.reply_text(f"{messages["ecode"]}❌ {messages["please first select uour language using /start"]}")
        return 
    
    if not cities:
        await update.message.reply_text(f"{messages["ecode"]}⚠️ {messages["You haven't set any cities yet. Use /addcity to add one"]}")
        return

    loading_msg = await update.message.reply_text(f"⏳ {messages["Preparing the report"]}...(0%)")

    await asyncio.sleep(1)
    await loading_msg.edit_text(f"⏳ {messages["getting weather report"]}...(30%)")

    report_text = f"📊 {messages["weather report"]} ({datetime.now().strftime('%Y-%m-%d')})\n"
    for city in cities:
            weather_info = get_weather(city)
            ai_response = get_ai_response(city, weather_info, user_id)
            report_text += f"\n📍 {city}\n{weather_info}\n🤖 {messages["AI Response"]}: {ai_response}\n"

    await asyncio.sleep(1)
    await loading_msg.edit_text(f"⏳ {messages["Processing with ai"]}...(60%)")

    await asyncio.sleep(1)
    final_text = f"✅ {messages["Processing complete"]}! (100%)\n\n" + report_text
    await loading_msg.edit_text(final_text)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    language = query.data

    user_language[user_id] = language
    refresh_language(user_id, language)
    messages = messages_cache.get(user_id, {})

    await query.edit_message_text(text=messages.get("you_selected_YOUR_language"))
    await query.message.reply_text(text=messages.get("subscribed_message"))

def run_scheduler(application):
    job_queue = application.job_queue
    job_queue.run_daily(send_weather_report, time=time(hour=5, minute=30))

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("report", report))
    application.add_handler(CommandHandler("done", done_adding_cities))
    application.add_handler(CommandHandler("addcity", add_city,))
    application.add_handler(CommandHandler("removecity", remove_city))
    application.add_handler(CommandHandler("mycities", list_user_cities))

    application.run_polling()

if __name__ == "__main__":
    main()