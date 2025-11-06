#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration DeepSeek
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # À vérifier selon la doc DeepSeek

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = """
🤖 **Bot DeepSeek IA Actif !**

🎯 **Commandes disponibles :**
/start - Démarrer le bot
/help - Aide et informations
/model - Informations sur le modèle

💬 **Posez-moi n'importe quelle question !**

🔧 *Configuration DeepSeek :* ✅
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
🆘 **Aide - Bot DeepSeek**

• Posez des questions normalement
• Le bot utilise l'API DeepSeek
• Réponses en temps réel
• Support technique inclus

📝 **Exemples :**
"Explique la programmation Python"
"Qu'est-ce que l'IA générative ?"
"Aide-moi avec mon code"
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['model'])
def model_info(message):
    info_text = """
🧠 **Informations Modèle :**

• **Fournisseur :** DeepSeek AI
• **Type :** Modèle de langage avancé
• **Capacités :** Code, texte, analyse
• **Statut :** ✅ Opérationnel
    """
    bot.reply_to(message, info_text)

@bot.message_handler(func=lambda message: True)
def reply(message):
    try:
        # Indicateur de frappe
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Vérifier la clé API
        if not DEEPSEEK_API_KEY:
            bot.reply_to(message, "❌ Erreur: Clé API DeepSeek non configurée")
            return

        # Headers pour l'API DeepSeek
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
        }

        # Données pour la requête
        payload = {
            "model": "deepseek-chat",  # À adapter selon le modèle DeepSeek
            "messages": [
                {
                    "role": "system", 
                    "content": "Tu es un assistant IA utile et précis. Réponds en français de manière claire et concise."
                },
                {
                    "role": "user", 
                    "content": message.text
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        # Envoyer la requête à l'API DeepSeek
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=30)
        
        # Vérifier la réponse
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, answer)
        else:
            error_msg = f"❌ Erreur API: {response.status_code} - {response.text}"
            bot.reply_to(message, error_msg)

    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Délai d'attente dépassé. Veuillez réessayer.")
    
    except requests.exceptions.ConnectionError:
        bot.reply_to(message, "🔌 Erreur de connexion. Vérifiez votre internet.")
    
    except Exception as e:
        error_message = f"❌ Erreur: {str(e)}"
        # Version raccourcie pour les erreurs longues
        if len(error_message) > 400:
            error_message = "❌ Erreur interne. Veuillez réessayer."
        bot.reply_to(message, error_message)

# Message de démarrage
print("🚀 Bot DeepSeek démarré...")
print(f"📁 Dossier: {os.getcwd()}")
print(f"🔑 Token Telegram: {'✅' if os.getenv('TELEGRAM_TOKEN') else '❌'}")
print(f"🧠 Clé DeepSeek: {'✅' if DEEPSEEK_API_KEY else '❌'}")

# Démarrer le bot
try:
    bot.infinity_polling()
except Exception as e:
    print(f"❌ Erreur démarrage bot: {e}")
