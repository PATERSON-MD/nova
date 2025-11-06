#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# ⚠️ URL CORRECTE :
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = f"""
🤖 **Bot Groq IA - Ultra Rapide !** ⚡

🎯 **Commandes :**
/start - Démarrer
/help - Aide
/test - Test de connexion
/models - Liste des modèles

🧠 **Modèles disponibles :**
• llama2-70b-4096
• mixtral-8x7b-32768  
• gemma-7b-it

⚡ **Vitesse :** Réponses en 1-2 secondes
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['test'])
def test_command(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }

        payload = {
            "messages": [
                {
                    "role": "user", 
                    "content": "Réponds uniquement par '✅ Groq fonctionne !'"
                }
            ],
            "model": "llama2-70b-4096",
            "max_tokens": 50
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, f"🧪 {answer}\n\n🚀 API Groq connectée !")
        else:
            bot.reply_to(message, f"❌ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur test: {str(e)}")

@bot.message_handler(commands=['models'])
def models_command(message):
    models_text = """
🧠 **Modèles Groq Disponibles :**

1. **llama2-70b-4096**
   - 70 milliards de paramètres
   - Très intelligent
   - Bon en code

2. **mixtral-8x7b-32768** 
   - 8 experts Mixtral
   - Excellente qualité
   - Contexte long

3. **gemma-7b-it**
   - Modèle Google
   - Léger et rapide
   - Bon pour le chat

💡 **Essaye :** /test pour vérifier la connexion
    """
    bot.reply_to(message, models_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }

        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": "Tu es un assistant IA utile. Réponds en français de manière claire et concise."
                },
                {
                    "role": "user", 
                    "content": message.text
                }
            ],
            "model": "llama2-70b-4096",
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, answer)
            
        else:
            error_info = f"""
❌ **Erreur Groq API**

Code: {response.status_code}
Message: {response.text}

🔧 **Solutions :**
• Vérifiez votre clé API
• Essayez /test pour diagnostiquer
• Modèle peut-être temporairement indisponible
            """
            bot.reply_to(message, error_info)

    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Timeout - Groq est normalement très rapide!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

print("🚀 Bot Groq démarré...")
print(f"🔗 URL API: {GROQ_API_URL}")
print(f"🔑 Token Telegram: {'✅' if os.getenv('TELEGRAM_TOKEN') else '❌'}")
print(f"⚡ Clé Groq: {'✅' if GROQ_API_KEY else '❌'}")

bot.infinity_polling()
