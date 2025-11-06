#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 🎯 MODÈLES CORRECTS GROQ :
AVAILABLE_MODELS = {
    "llama3-8b": "llama3-8b-8192",
    "llama3-70b": "llama3-70b-8192", 
    "mixtral": "mixtral-8x7b-32768",
    "gemma": "gemma-7b-it"
}

# Modèle par défaut (choisissez-en un)
SELECTED_MODEL = AVAILABLE_MODELS["llama3-70b"]

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = f"""
🤖 **Bot Groq IA - Modèles Corrigés !** ⚡

🎯 **Commandes :**
/start - Démarrer
/models - Changer de modèle
/test - Test de connexion
/current - Modèle actuel

🧠 **Modèle actuel :** {SELECTED_MODEL}
⚡ **Vitesse :** Réponses ultra-rapides

💬 **Posez-moi n'importe quelle question !**
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['models'])
def models_command(message):
    models_text = f"""
🧠 **Modèles Groq Disponibles :**

1. **llama3-70b-8192** (recommandé)
   - Llama 3 70B dernier cri
   - Très intelligent
   - Bon en tout

2. **llama3-8b-8192**
   - Llama 3 8B rapide
   - Léger et efficace
   - Parfait pour le chat

3. **mixtral-8x7b-32768**
   - 8 experts Mixtral
   - Excellente qualité
   - Contexte long

4. **gemma-7b-it** 
   - Modèle Google
   - Léger et rapide

🔧 **Actuel :** {SELECTED_MODEL}
💡 **Changer :** /llama3-70b /llama3-8b /mixtral /gemma
    """
    bot.reply_to(message, models_text)

@bot.message_handler(commands=['llama3-70b', 'llama3-8b', 'mixtral', 'gemma'])
def change_model(message):
    global SELECTED_MODEL
    
    model_command = message.text[1:]  # Enlever le /
    if model_command in AVAILABLE_MODELS:
        SELECTED_MODEL = AVAILABLE_MODELS[model_command]
        bot.reply_to(message, f"✅ Modèle changé pour : {SELECTED_MODEL}")
    else:
        bot.reply_to(message, "❌ Commande de modèle invalide")

@bot.message_handler(commands=['current'])
def current_model(message):
    bot.reply_to(message, f"🧠 Modèle actuel : {SELECTED_MODEL}")

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
                    "content": "Réponds UNIQUEMENT par '✅ Test réussi avec [MODÈLE]' en remplaçant [MODÈLE] par le modèle utilisé."
                }
            ],
            "model": SELECTED_MODEL,
            "max_tokens": 50
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, f"🧪 {answer}\n\n🚀 API Groq fonctionne !")
        else:
            bot.reply_to(message, f"❌ Erreur {response.status_code}: {response.text}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur test: {str(e)}")

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
                    "content": "Tu es un assistant IA utile. Réponds en français de manière claire et concise. Sois direct dans tes réponses."
                },
                {
                    "role": "user", 
                    "content": message.text
                }
            ],
            "model": SELECTED_MODEL,
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

Modèle utilisé: {SELECTED_MODEL}
🔧 Essayez /models pour changer de modèle
            """
            bot.reply_to(message, error_info)

    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Timeout - Réessayez!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

print("🚀 Bot Groq démarré avec modèles corrigés!")
print(f"🧠 Modèle par défaut: {SELECTED_MODEL}")
print(f"🔑 Token Telegram: {'✅' if os.getenv('TELEGRAM_TOKEN') else '❌'}")
print(f"⚡ Clé Groq: {'✅' if GROQ_API_KEY else '❌'}")

bot.infinity_polling()
