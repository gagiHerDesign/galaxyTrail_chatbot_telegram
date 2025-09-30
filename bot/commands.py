from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
import requests
import traceback
from telegram.ext import ContextTypes
from .apis import fetch_weather, fetch_nasa_apod, fetch_news_events


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Nature park around you 🌲", callback_data="near_park"),
            InlineKeyboardButton("Future sky event 🌌", callback_data="future_events"),
        ]
    ]
    await update.message.reply_text(
        "Hello! 🌌 Welcome to Galaxy Trail Bot! Nice to meet you here!Select an option：", reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Step 2: 處理主選單的點擊
async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        print("[menu_handler] entered")
        if query is None:
            print("[menu_handler] update.callback_query is None")
            return

        print(f"[menu_handler] callback from user_id={getattr(query.from_user, 'id', None)} chat_id={getattr(query.message.chat, 'id', None)} data={query.data}")

        # 必要時回覆 callback，避免 Telegram 顯示 loading
        await query.answer()
        print("[menu_handler] answered callback query")

        if query.data == "near_park":
            print("[menu_handler] near_park selected")
            # 出現一個要求分享位置的鍵盤
            location_keyboard = [
                [KeyboardButton("📍 Share my location", request_location=True)]
            ]
            reply_markup = ReplyKeyboardMarkup(location_keyboard, one_time_keyboard=True)
            sent = await query.message.reply_text(
                "Please share your location, I can help you find the nearest nature park：",
                reply_markup=reply_markup,
            )
            print(f"[menu_handler] sent location request message id={getattr(sent, 'message_id', None)}")

        elif query.data == "future_events":
            print("[menu_handler] future_events selected - delegating to future_events handler")
            # 建立一個簡單的 DummyUpdate，包裝原本的 message，讓 future_events 可以重用相同的回覆邏輯
            DummyUpdate = type("DummyUpdate", (), {})
            dummy = DummyUpdate()
            dummy.message = query.message
            # 直接呼叫同檔案內定義的 future_events coroutine，達成點按時等同於輸入 /future 的效果
            await future_events(dummy, context)
            print("[menu_handler] delegated to future_events")

    except Exception as e:
        print(f"[menu_handler] exception: {e}")

# Step 3: 處理位置訊息並查詢附近公園
async def location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print("[location_handler] entered")
        if not update.message or not getattr(update.message, 'location', None):
            print("[location_handler] no location in update.message")
            await update.message.reply_text("I didn't accept your location, use '📍 share location' to share。")
            return

        lat = update.message.location.latitude
        lon = update.message.location.longitude
        print(f"[location_handler] received lat={lat}, lon={lon}")

        # 使用 Overpass API (OpenStreetMap) 搜尋 20 公里範圍內的國家公園
        overpass_url = "https://overpass-api.de/api/interpreter"
        query = f"""
        [out:json];
        (
          node["leisure"="nature_reserve"](around:20000,{lat},{lon});
          way["leisure"="nature_reserve"](around:20000,{lat},{lon});
          relation["leisure"="nature_reserve"](around:20000,{lat},{lon});
        );
        out center 5;
        """
        print(f"[location_handler] querying Overpass: url={overpass_url} (query length={len(query)})")
        res = requests.post(overpass_url, data=query, timeout=15)
        print(f"[location_handler] Overpass status_code={res.status_code}")
        data = res.json()

        elements = data.get("elements") or []
        print(f"[location_handler] Overpass returned elements_count={len(elements)}")

        if not elements:
            await update.message.reply_text("There is no nature parks in 20 kms 🌲")
            print("[location_handler] no parks found, exiting")
            return

        parks = []
        buttons = []
        for i, el in enumerate(elements[:5]):
            name = el.get("tags", {}).get("name", "cute park")
            center = el.get("center") or {"lat": el.get("lat"), "lon": el.get("lon")}
            maps_link = f"https://www.openstreetmap.org/?mlat={center['lat']}&mlon={center['lon']}#map=15/{center['lat']}/{center['lon']}"
            parks.append(f"{i+1}. {name}")
            # 每個公園加入一個 Inline button 打開地圖
            buttons.append([InlineKeyboardButton("open in map", url=maps_link)])
            print(f"[location_handler] park #{i+1}: name={name} lat={center['lat']} lon={center['lon']}")

        reply_text = "nature park nearby：\n\n" + "\n".join(parks)
        # 回覆名稱與對應的 inline buttons
        await update.message.reply_text(reply_text, reply_markup=InlineKeyboardMarkup(buttons))
        print("[location_handler] replied with parks list and inline buttons")

    except Exception as e:
        print(f"[location_handler] exception: {e}")
        print(traceback.format_exc())

# 幫助指令和其他指令
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "Here are the commands you can use:\n"
        "/start - Start the bot and get a welcome message\n"
        "/help - Show this help message\n"
        "/park - see nature park nearby you\n"
        "/sky - see the weather in the city and the beautiful sky picture\n"
        "/future - follow the updating astronomy news\n"
        "/lightpollution - see the light pollution map\n"
    )
    await update.message.reply_text(help_text)


async def park(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        print(f"[park] invoked by user chat_id={getattr(update.message.chat, 'id', None)}")
        # 要求使用者分享位置
        location_keyboard = [[KeyboardButton("📍 share my location", request_location=True)]]
        reply_markup = ReplyKeyboardMarkup(location_keyboard, one_time_keyboard=True)
        sent = await update.message.reply_text(
            "Please share your location. I will help you find the nature parks nearby：",
            reply_markup=reply_markup,
        )
        print(f"[park] sent location request message id={getattr(sent, 'message_id', None)}")
    except Exception as e:
        print(f"[park] exception: {e}")
        # fallback: 提供靜態示例
        reply = (
            "🌲 Example National Parks:\n"
            "- Yellowstone National Park (Wyoming, Montana, Idaho)\n"
            "- Yosemite National Park (California)\n"
            "- Grand Canyon National Park (Arizona)\n"
            "\nTry /sky <city> to check stargazing conditions!"
        )
        await update.message.reply_text(reply)


async def sky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Usage: /sky <city>")
        return
    city = " ".join(context.args)

    w = fetch_weather(city)
    if not w or w.get('cod') != 200:
        await update.message.reply_text("❌ City not found or API error.")
        return

    temp = w['main']['temp']
    clouds = w['clouds']['all']
    description = w['weather'][0]['description']

    apod_title, apod_url = fetch_nasa_apod()
    if not apod_title:
        apod_title = "NASA APOD not available"
        apod_url = ""

    reply = (
        f"🔭 Tonight's sky in {city.title()}:\n"
        f"Temperature: {temp}°C\n"
        f"Cloud Cover: {clouds}%\n"
        f"Condition: {description}\n\n"
        f"✨ NASA Astronomy Picture of the Day:\n"
        f"{apod_title}\n{apod_url}"
    )
    await update.message.reply_text(reply)


async def future_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """抓取最新天文新聞，並檢查是否超過免費額度"""
    status, data = fetch_news_events(page_size=3)

    if status is None:
        await update.message.reply_text("⚠️ Cannot link to service, try again later")
        print("fetch_news_events error:", data)
        return

    if status == 429:
        await update.message.reply_text(
            "this robot is developed by a student, so she cannot afford too many requests one day, because this will charge a lot of money"
        )
        print("Hit daily request limit for NewsAPI.")
        return

    if status != 200:
        await update.message.reply_text(f"⚠️ Something wrong when fetching data ({status})。")
        print("NewsAPI error:", data)
        return

    articles = data.get("articles", [])
    if not articles:
        await update.message.reply_text("There is no astronomy news now 🌌")
        return

    # 建立顯示標題的文字與對應的 Inline buttons（每篇新聞一個按鈕）
    lines = []
    buttons = []
    for i, art in enumerate(articles, start=1):
        title = art.get("title") or "(no title)"
        url = art.get("url")
        lines.append(f"{i}. {title}")
        if url:
            buttons.append([InlineKeyboardButton(f"Open the {i} News", url=url)])

    header = "🌠 Latest astronomy news：\n\n"
    body = header + "\n".join(lines)

    if buttons:
        await update.message.reply_text(body, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        # 若沒有可用連結，退回純文字顯示
        await update.message.reply_text(body)


async def lightpollution(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """顯示 lightpollution 地圖的網址並附上開啟按鈕"""
    url = "https://www.lightpollutionmap.info/?utm_source=chatgpt.com#zoom=4.00&lat=45.8720&lon=14.5470&state=eyJiYXNlbWFwIjoiTGF5ZXJCaW5nUm9hZCIsIm92ZXJsYXkiOiJ3YV8yMDE1Iiwib3ZlcmxheWNvbG9yIjpmYWxzZSwib3ZlcmxheW9wYWNpdHkiOiI2MCIsImZlYXR1cmVzb3BhY2l0eSI6Ijg1In0="
    keyboard = [[InlineKeyboardButton("Open Light Pollution Map", url=url)]]
    text = f"Light pollution map:\n{url}"
    try:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print(f"[lightpollution] exception: {e}")
        await update.message.reply_text(url)

