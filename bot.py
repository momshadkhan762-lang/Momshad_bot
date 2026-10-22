import os
import telebot
import requests
from flask import Flask
import threading

app = Flask('')

@app.route('/')
def home():
    return "OK"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

threading.Thread(target=run_flask).start()

API_TOKEN = "8905641525:AAFR-VJcyipT3XRMVcLuM_NQ-bHCHN1Ajnw"
bot = telebot.TeleBot(API_TOKEN)

# Your Admin Telegram ID
ADMIN_ID = 8380823727

# Global variable to control bot status and allowed users
bot_active = True
allowed_users = set()

@bot.message_handler(commands=['off'])
def off_command(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
    global bot_active
    bot_active = False
    bot.reply_to(message, "🔴 Bot services are now OFF.")

@bot.message_handler(commands=['on'])
def on_command(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
    global bot_active
    bot_active = True
    bot.reply_to(message, "🟢 Bot services are now ON.")

@bot.message_handler(commands=['allow'])
def allow_user(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Please provide a User ID. Example: /allow 123456789")
        return
    
    try:
        user_id = int(args[1])
        allowed_users.add(user_id)
        bot.reply_to(message, f"✅ User <code>{user_id}</code> has been allowed.", parse_mode='HTML')
    except ValueError:
        bot.reply_to(message, "❌ Invalid User ID.")

@bot.message_handler(commands=['disallow'])
def disallow_user(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
    
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "⚠️ Please provide a User ID. Example: /disallow 123456789")
        return
    
    try:
        user_id = int(args[1])
        if user_id in allowed_users:
            allowed_users.remove(user_id)
            bot.reply_to(message, f"✅ User <code>{user_id}</code> has been removed from allowed list.", parse_mode='HTML')
        else:
            bot.reply_to(message, f"⚠️ User <code>{user_id}</code> was not in the allowed list.", parse_mode='HTML')
    except ValueError:
        bot.reply_to(message, "❌ Invalid User ID.")

@bot.message_handler(commands=['list'])
def list_users(message):
    if message.from_user is None or message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Only the owner can use this command!")
        return
    
    if not allowed_users:
        bot.reply_to(message, "📂 The allowed users list is currently empty.")
        return
    
    users_list_text = "📋 <b>Allowed Users List :</b>\n──────────────────\n"
    for uid in allowed_users:
        users_list_text += f"👤 <code>{uid}</code>\n"
    users_list_text += "──────────────────"
    
    bot.reply_to(message, users_list_text, parse_mode='HTML')

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = f"""🤖 <b>MOMSHAD BOT HELP MENU</b> 🤖
──────────────────
📌 <b>Available Commands :</b>
🔹 <code>/like {{region}} {{uid}}</code> - Send likes to a Free Fire player
🔹 <code>/help</code> - Show this help menu

👑 <b>Admin Commands (Owner Only) :</b>
🔸 <code>/on</code> - Turn bot services ON
🔸 <code>/off</code> - Turn bot services OFF
🔸 <code>/allow {{user_id}}</code> - Give permission to a user
🔸 <code>/disallow {{user_id}}</code> - Remove permission from a user
🔸 <code>/list</code> - Show all allowed users
──────────────────
👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>
🚀 <b>OWNER :</b> @Momshad_00"""
    bot.reply_to(message, help_text, parse_mode='HTML')

@bot.message_handler(commands=['like'])
def handle_like(message):
    if not bot_active:
        bot.reply_to(message, "⚠️ Bot is currently offline. Send /on to start it.")
        return

    user_id = message.from_user.id
    if user_id != ADMIN_ID and user_id not in allowed_users:
        bot.reply_to(message, "❌ You are not allowed to use this bot! Ask the owner to /allow your User ID.")
        return

    args = message.text.split()
    if len(args) < 3:
        error_text = f"""⚠️ <b>WRONG FORMAT USAGE</b> ⚠️
──────────────────
❌ <b>Incorrect Command Structure</b>
📌 <b>Correct Format :</b> <code>/like {{region}} {{uid}}</code>
💡 <b>Example :</b> <code>/like ind 1772894853</code>
──────────────────
👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>
🚀 <b>OWNER :</b> @Momshad_00"""
        bot.reply_to(message, error_text, parse_mode='HTML')
        return

    region = args[1].lower()
    uid = args[2]

    sent_msg = bot.reply_to(message, "⏳ Processing your request...")
    api_url = f"https://like-apii-one.vercel.app/like?uid={uid}&server_name={region}"

    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(api_url, headers=headers)
        data = response.json()

        name = str(data.get('PlayerNickname', 'Unknown'))
        likes_before = str(data.get('LikesbeforeCommand', '0'))
        likes_given = str(data.get('LikesGivenByAPI', '0'))
        likes_after = str(data.get('LikesafterCommand', '0'))
        remaining = str(data.get('Remaining_requests', '0'))

        if int(likes_after) > int(likes_before) or int(likes_given) > 0:
            reply_text = f"""🎉 <b>LIKE SUCCESSFUL</b> 👍
──────────────────
👑 <b>Name :</b> {name}
🎮 <b>UID :</b> {uid}
🌍 <b>Region :</b> {region.upper()}
──────────────────
❤️ <b>Likes Before :</b> {likes_before}
💙 <b>Likes Given :</b> {likes_given}
💚 <b>Likes After :</b> {likes_after}
⚡ <b>Remaining Requests :</b> {remaining}
──────────────────
👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>
🚀 <b>OWNER :</b> @Momshad_00"""
        else:
            reply_text = f"""⚠️ <b>DAILY LIMIT REACHED</b>
──────────────────
👤 <b>NAME :</b> {name}
🆔 <b>UID :</b> {uid}
🌍 <b>SERVER :</b> {region.upper()}
──────────────────
📊 <b>STATUS :</b> 0 Likes Added
✏️ <b>REASON :</b> Daily Max Limit Reached
──────────────────
👑 <b>ADMIN ID :</b> <code>{ADMIN_ID}</code>
🚀 <b>OWNER :</b> @Momshad_00"""

        bot.edit_message_text(reply_text, chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

    except Exception as e:
        bot.edit_message_text(f"❌ <b>API Error:</b> {str(e)}", chat_id=sent_msg.chat.id, message_id=sent_msg.message_id, parse_mode='HTML')

if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
    

        
    
        
        
    
    
    
    
