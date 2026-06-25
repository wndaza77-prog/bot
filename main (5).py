import telebot
from telebot import types
import sqlite3
import datetime

TOKEN = "8650833362:AAE5NlR_s7l3XCWrzWrc0_zbBd5Ayz8USPc"
ADMIN_ID = 7833653010
CARD_INFO = "9860350143586054 M.J"

bot = telebot.TeleBot(TOKEN)

# ================= БАЗА ДАННЫХ =================

def init_db():
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, username TEXT, joined_date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders
                 (order_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, 
                  item TEXT, status TEXT, date TEXT)''')
    
    # Новая таблица для товаров и цен
    c.execute('''CREATE TABLE IF NOT EXISTS products
                 (code TEXT PRIMARY KEY, category TEXT, name TEXT, price TEXT)''')
    
    # Проверяем, пустая ли таблица товаров. Если да - заполняем стандартными ценами
    c.execute("SELECT COUNT(*) FROM products")
    if c.fetchone()[0] == 0:
        default_products = [
            ("star_50", "stars", "50★", "12.000 sum"),
            ("star_100", "stars", "100★", "23.000 sum"),
            ("star_200", "stars", "200★", "45.000 sum"),
            ("star_350", "stars", "350★", "78.000 sum"),
            ("star_500", "stars", "500★", "115.000 sum"),
            ("star_750", "stars", "750★", "167.000 sum"),
            ("star_1000", "stars", "1.000★", "225.000 sum"),
            ("prem_3", "premium", "Ⰶ Premium 3 Months", "175.000 sum"),
            ("prem_6", "premium", "Ⰶ Premium 6 Months", "235.000 sum"),
            ("prem_12", "premium", "Ⰶ Premium 1 Year", "425.000 sum"),
            ("g_bear", "gifts", "🧸 Ayiqcha", "5.000 sum"),
            ("g_heart", "gifts", "💝 Yurak", "5.000 sum"),
            ("g_box", "gifts", "🎁 Sovg'a qutisi", "6.500 sum"),
            ("g_rose", "gifts", "🌹 Atirgul", "6.500 sum"),
            ("g_cake", "gifts", "🎂 Tort", "13.000 sum"),
            ("g_flower", "gifts", "💐 Gul dasta", "13.000 sum"),
            ("g_rocket", "gifts", "🚀 Raketa", "13.000 sum")
        ]
        c.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", default_products)
        
    conn.commit()
    conn.close()

init_db()

# Вспомогательные функции БД
def add_user(user_id, username):
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, joined_date) VALUES (?, ?, ?)",
              (user_id, username, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()

def create_order(user_id, item):
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_id, item, status, date) VALUES (?, ?, 'pending', ?)",
              (user_id, item, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

def update_order_status(order_id, status):
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
    conn.commit()
    conn.close()

def get_pending_order(user_id):
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute("SELECT order_id, item FROM orders WHERE user_id = ? AND status = 'pending' ORDER BY order_id DESC LIMIT 1", (user_id,))
    res = c.fetchone()
    conn.close()
    return res

def get_user_stats(user_id):
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = 'paid'", (user_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def get_products_by_category(category):
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute("SELECT code, name, price FROM products WHERE category = ?", (category,))
    items = c.fetchall()
    conn.close()
    return items

def update_product_price(code, new_price):
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute("UPDATE products SET price = ? WHERE code = ?", (new_price, code))
    conn.commit()
    conn.close()

def get_product_by_code(code):
    conn = sqlite3.connect('shop_inline.db')
    c = conn.cursor()
    c.execute("SELECT name, price FROM products WHERE code = ?", (code,))
    item = c.fetchone()
    conn.close()
    return item

# ================= КЛАВИАТУРЫ ПОЛЬЗОВАТЕЛЯ =================

def get_main_inline_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("⭐ Stars olish", callback_data="menu_stars"),
        types.InlineKeyboardButton("🍇 Premium olish", callback_data="menu_premium")
    )
    markup.add(types.InlineKeyboardButton("🎁 Sovg'alar (Gifts)", callback_data="menu_gift"))
    markup.add(
        types.InlineKeyboardButton("🏆 Top Reyting", callback_data="menu_rating"),
        types.InlineKeyboardButton("📊 Statistikam", callback_data="menu_stats")
    )
    markup.add(types.InlineKeyboardButton("👤 Profil", callback_data="menu_profile"))
    return markup

def get_back_button():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="menu_main"))
    return markup

# ================= ЛОГИКА ПОЛЬЗОВАТЕЛЯ =================

@bot.message_handler(commands=['start'])
def start_command(message):
    add_user(message.from_user.id, message.from_user.username)
    bot.send_message(message.chat.id, 
                     "😎 Assalom alaykum, botga xush kelibsiz!\n\n🏄‍♂️ Bot orqali «⭐ Telegram Stars», «🍇 Telegram Premium» va «🎁 Sovg'alar» xarid qilishingiz mumkin\n\nKerakli bo'limni tanlang 👇", 
                     reply_markup=types.ReplyKeyboardRemove())
    bot.send_message(message.chat.id, "🎛 **Siz buyurtmalar bo'limidasiz:**", reply_markup=get_main_inline_keyboard(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("menu_"))
def handle_menu_navigation(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == "menu_main":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🎛 **Asosiy menyu:**", reply_markup=get_main_inline_keyboard(), parse_mode="Markdown")
        
    elif call.data in ["menu_stars", "menu_premium", "menu_gift"]:
        category_map = {"menu_stars": "stars", "menu_premium": "premium", "menu_gift": "gifts"}
        category_titles = {"menu_stars": "🌟 **Telegram Stars paketini tanlang:**", 
                           "menu_premium": "🍇 **Telegram Premium muddatini tanlang:**", 
                           "menu_gift": "🎁 **Sovg'alardan (Gifts) birini tanlang:**"}
        
        cat_db_name = category_map[call.data]
        products = get_products_by_category(cat_db_name)
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for code, name, price in products:
            # Динамически собираем кнопки из БД
            markup.add(types.InlineKeyboardButton(f"{name} - {price}", callback_data=f"buy_{code}"))
        markup.add(types.InlineKeyboardButton("⬅️ Ortga", callback_data="menu_main"))
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=category_titles[call.data], reply_markup=markup, parse_mode="Markdown")
        
    elif call.data == "menu_stats":
        count = get_user_stats(call.from_user.id)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"📊 **Sizning statistikangiz:**\n\n👤 ID: `{call.from_user.id}`\n📦 Muvaffaqiyatli xaridlar: {count} ta", reply_markup=get_back_button(), parse_mode="Markdown")
        
    elif call.data == "menu_profile":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"👤 **Sizning profilingiz:**\n\nIsm: {call.from_user.first_name}\nUsername: @{call.from_user.username or 'yoq'}\nID: `{call.from_user.id}`", reply_markup=get_back_button(), parse_mode="Markdown")
        
    elif call.data == "menu_rating":
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🏆 **Top Xaridorlar Reytingi:**\n\nBot yangi, ro'yxat bo'sh. Xarid qiling va birinchi bo'ling! 🚀", reply_markup=get_back_button(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def handle_purchase_selection(call):
    item_code = call.data.replace("buy_", "")
    product = get_product_by_code(item_code)
    
    if product:
        name, price = product
        selected_item = f"{name} ({price})"
        order_id = create_order(call.from_user.id, selected_item)
        
        payment_text = (f"💳 **To'lov ma'lumotlari:**\n\n"
                        f"🆔 Buyurtma raqami: #{order_id}\n"
                        f"📦 Mahsulot: {selected_item}\n"
                        f"🔢 Karta: `{CARD_INFO}`\n\n"
                        f"⚠️ **Muhim:** To'lov qilib, chekni rasm ko'rinishida yuboring!")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=payment_text, reply_markup=get_back_button(), parse_mode="Markdown")

@bot.message_handler(content_types=['photo'])
def handle_receipt(message):
    user_id = message.from_user.id
    order = get_pending_order(user_id)
    if order:
        order_id, item = order
        photo_id = message.photo[-1].file_id
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"acc_{order_id}_{user_id}"),
            types.InlineKeyboardButton("❌ Rad etish", callback_data=f"rej_{order_id}_{user_id}")
        )
        bot.send_photo(ADMIN_ID, photo_id, caption=f"🔔 **Yangi buyurtma #{order_id}**\n👤 @{message.from_user.username or 'yoq'}\n📦 {item}", reply_markup=markup, parse_mode="Markdown")
        bot.send_message(user_id, f"✅ Chek qabul qilindi (Buyurtma #{order_id}). Kuting! 🙏")
    else:
        bot.send_message(user_id, "❌ Oldin menyudan mahsulot tanlang.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("acc_") or call.data.startswith("rej_"))
def handle_admin_decision(call):
    if call.from_user.id != ADMIN_ID:
        return bot.answer_callback_query(call.id, "Siz admin emassiz!", show_alert=True)
        
    action, order_id, target_user_id = call.data.split("_")
    if action == "acc":
        update_order_status(order_id, "paid")
        bot.send_message(target_user_id, f"🎉 Buyurtmangiz (#{order_id}) tasdiqlandi! ✅")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + f"\n\n🟢 **STATUS: TASDIQLANDI!**", parse_mode="Markdown")
    else:
        update_order_status(order_id, "rejected")
        bot.send_message(target_user_id, f"❌ Buyurtma (#{order_id}) rad etildi.")
        bot.edit_message_caption(chat_id=call.message.chat.id, message_id=call.message.message_id, caption=call.message.caption + f"\n\n🔴 **STATUS: RAD ETILDI!**", parse_mode="Markdown")

# ================= АДМИН ПАНЕЛЬ (НАСТРОЙКА ЦЕН) =================

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return bot.send_message(message.chat.id, "Siz admin emassiz!")
        
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⚙️ Stars narxlarini o'zgartirish", callback_data="admcat_stars"),
        types.InlineKeyboardButton("⚙️ Premium narxlarini o'zgartirish", callback_data="admcat_premium"),
        types.InlineKeyboardButton("⚙️ Gifts narxlarini o'zgartirish", callback_data="admcat_gifts")
    )
    bot.send_message(message.chat.id, "🛠 **Admin Panel:** Qaysi bo'lim narxini o'zgartiramiz?", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admcat_"))
def admin_category_select(call):
    if call.from_user.id != ADMIN_ID: return
    
    category = call.data.split("_")[1]
    products = get_products_by_category(category)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for code, name, price in products:
        markup.add(types.InlineKeyboardButton(f"✏️ {name} ({price})", callback_data=f"admedit_{code}"))
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                          text=f"📂 **{category.upper()}** bo'limi.\nO'zgartirmoqchi bo'lgan mahsulotni tanlang:", 
                          reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("admedit_"))
def admin_edit_product(call):
    if call.from_user.id != ADMIN_ID: return
    
    code = call.data.replace("admedit_", "")
    product = get_product_by_code(code)
    
    if product:
        name, old_price = product
        msg = bot.send_message(call.message.chat.id, f"📝 **{name}** uchun yangi narxni yozing (Hozirgi: {old_price}):\n\n*Masalan: 15.000 sum*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, process_new_price, code, name)

def process_new_price(message, code, name):
    new_price = message.text
    update_product_price(code, new_price)
    bot.send_message(message.chat.id, f"✅ **{name}** narxi muvaffaqiyatli o'zgartirildi: **{new_price}**", parse_mode="Markdown")
    # Возвращаем в админку для удобства
    admin_panel(message)

if __name__ == '__main__':
    print("Бот с Админ-панелью успешно запущен!")
    bot.infinity_polling()
