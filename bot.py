#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = f"""
🤖 **Bot Groq IA - Ultra Rapide !** ⚡

🎯 **Commandes :**
/start - Démarrer
/help - Aide
/info - Infos techniques

🧠 **Modèle :** Llama2-70b
⚡ **Vitesse :** Réponses en 1-2 secondes
🔧 **Statut :** ✅ Groq Connecté

💬 **Posez-moi n'importe quelle question !**
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🆘 **Aide - Bot Groq IA**

• Réponses ultra-rapides (1-2s)
• Modèle Llama2-70b
• Support multilingue
• Conversation fluide

**Exemples :**
"Explique Python simplement"
"Comment créer un site web ?"
"Aide-moi avec mes devoirs"
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['info'])
def info_command(message):
    info_text = """
🧠 **Informations Techniques :**

• **API :** Groq
• **Modèle :** Llama2-70b
• **Vitesse :** ⚡ Ultra-rapide
• **Gratuit :** ✅ Oui
• **Limites :** Quotas généreux
    """
    bot.reply_to(message, info_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Préparer requête Groq
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }

        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": "Tu es un assistant IA utile et concis. Réponds en français de manière claire. Sois direct et évite les introductions trop longues."
                },
                {
                    "role": "user", 
                    "content": message.text
                }
            ],
            "model": "llama2-70b-4096",  # Modèle Groq
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False
        }

        # Envoyer requête
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, answer)
            
        elif response.status_code == 401:
            bot.reply_to(message, "❌ Clé API Groq invalide")
            
        elif response.status_code == 429:
            bot.reply_to(message, "⏰ Trop de requêtes. Réessayez dans 1 minute.")
            
        else:
            bot.reply_to(message, f"❌ Erreur Groq: {response.status_code}")

    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Timeout - Groq est normalement très rapide!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

print("🚀 Bot Groq démarré...")
print(f"🔑 Token Telegram: {'✅' if os.getenv('TELEGRAM_TOKEN') else '❌'}")
print(f"⚡ Clé Groq: {'✅' if GROQ_API_KEY else '❌'}")

bot.infinity_polling()
