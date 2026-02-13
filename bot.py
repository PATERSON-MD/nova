#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 CHATGPT | 𓃦 - Comme ChatGPT sur WhatsApp
📱 Pose une question, reçois une réponse
⚡ Simple, rapide, efficace
"""

import telebot
import requests
import os
import time
import logging
from dotenv import load_dotenv

# Configuration simple
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    # Image de bienvenue
    WELCOME_IMAGE_URL = "https://files.catbox.moe/2l0dld.jpg"

bot = telebot.TeleBot(Config.TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    """Message de bienvenue avec photo"""
    try:
        # Télécharger et envoyer la photo
        photo_data = requests.get(Config.WELCOME_IMAGE_URL).content
        
        welcome_text = """🤖 **CHATGPT | 𓃦**

**Salut! Je suis ton assistant personnel.**

Pose-moi simplement ta question et je te répondrai.

**Exemples:**
• Explique-moi les bases de Python
• Comment créer une fonction?
• Quelle est la capitale de la France?
• Aide-moi à debugger ce code...

💡 _Pas de menus compliqués, juste des questions/réponses!_

Utilise /help pour plus d'infos"""
        
        # Envoyer la photo avec la légende
        bot.send_photo(
            message.chat.id, 
            photo_data, 
            caption=welcome_text,
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Erreur envoi photo: {e}")
        # Fallback si la photo ne s'envoie pas
        bot.reply_to(
            message, 
            "🤖 **CHATGPT | 𓃦**\n\nSalut! Je suis ton assistant. Pose-moi ta question!",
            parse_mode='Markdown'
        )

@bot.message_handler(commands=['help'])
def help(message):
    """Aide simple"""
    help_text = """📚 **CHATGPT | 𓃦 - Aide**

**Commandes disponibles:**
/start - Démarrer le bot
/help - Afficher cette aide
/clear - Effacer la conversation

**Comment utiliser:**
1. Envoie moi une question
2. Je te réponds directement
3. C'est tout! Simple non?

_Pose n'importe quelle question, je suis là pour t'aider!_"""
    
    bot.reply_to(message, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['clear'])
def clear(message):
    """Simule un reset de conversation"""
    bot.reply_to(message, "🧹 Conversation réinitialisée! Pose ta prochaine question.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Gère tous les messages - simple question/réponse"""
    try:
        user_message = message.text.strip()
        
        # Ignorer les commandes
        if user_message.startswith('/'):
            return
        
        # Montrer que le bot tape
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Appel à l'API
        if Config.GROQ_API_KEY:
            headers = {
                "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": "Tu es CHATGPT | 𓃦, un assistant IA utile, amical et concis. Réponds de manière claire et directe, comme ChatGPT."},
                    {"role": "user", "content": user_message}
                ],
                "model": "llama-3.1-8b-instant",
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            response = requests.post(Config.GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Répondre directement
                bot.reply_to(message, ai_response)
            else:
                bot.reply_to(message, "❌ Désolé, je n'arrive pas à répondre pour le moment. Réessaie dans quelques secondes.")
        else:
            # Mode démo sans API
            demo_responses = {
                "bonjour": "Bonjour ! Comment puis-je t'aider aujourd'hui ?",
                "comment ça va": "Je vais bien, merci ! Et toi ?",
                "qui es-tu": "Je suis CHATGPT | 𓃦, ton assistant IA.",
                "python": "Python est un langage de programmation puissant et facile à apprendre. Tu veux savoir quelque chose de spécifique ?",
            }
            
            # Réponse simple ou par défaut
            response = "Désolé, je suis en mode démo. Configure ta clé API Groq pour des vraies réponses!"
            for key in demo_responses:
                if key in user_message.lower():
                    response = demo_responses[key]
                    break
            
            time.sleep(1)  # Simule la réflexion
            bot.reply_to(message, f"🤖 **CHATGPT | 𓃦**\n\n{response}", parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Erreur: {e}")
        bot.reply_to(message, "❌ Une erreur s'est produite. Peux-tu reformuler ta question ?")

# Point d'entrée
if __name__ == "__main__":
    print("""
    🤖 CHATGPT | 𓃦
    ================
    Mode: Question/Réponse Simple
    Statut: 🟢 En ligne
    ================
    En attente de vos messages...
    """)
    
    try:
        bot.infinity_polling(timeout=60)
    except Exception as e:
        logger.error(f"Erreur: {e}")
        time.sleep(5)
