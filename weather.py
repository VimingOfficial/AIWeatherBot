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

cities = ["City1", "City2"]  # Replace with your chosen cities
user_language = {}
client = genai.Client(api_key=AI_API)

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
    prompt = f"Comment on the weather in {city}, which is as follows: {weather_info}. Please respond in {ai_language}."

    response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)

    if response and hasattr(response, 'text'):
        return response.text
    else:
        return "❌ Error in generating AI response."


def get_weather_report(user_id):
    messages = messages_cache.get(user_id, {})
    weather_report_text=messages["weather report"]
    ai_response_text=messages["AI Response"]
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
    if user_id not in user_language:
        await update.message.reply_text("❌" + messages["please first select uour language using /start"])
        return 

    loading_msg = await update.message.reply_text("⏳" + messages["Fetching weather data"] +"(0%)")

    await asyncio.sleep(1)
    await loading_msg.edit_text("⏳" + messages["getting weather report"] + "(30%)")

    report_text = get_weather_report(user_id)
    await asyncio.sleep(1)
    await loading_msg.edit_text("⏳" + messages["Processing with ai"] + "(60%)")

    await asyncio.sleep(1)
    final_text = "✅" + messages["Processing complete"] + "(100%)\n\n" + report_text
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
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("report", report))

    run_scheduler(application)

    application.run_polling()

if __name__ == "__main__":
    main()