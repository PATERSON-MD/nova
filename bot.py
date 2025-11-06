#!/data/data/com.termux/files/usr/bin/python3
import telebot
import openai
import os
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
openai.api_key = os.getenv('OPENAI_API_KEY')

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🤖 Bot IA actif! Pose-moi une question.")

@bot.message_handler(func=lambda message: True)
def reply(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        # SYNTAXE CORRECTE
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message.text}],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        bot.reply_to(message, answer)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

print("🚀 Bot démarré...")
bot.infinity_polling()
