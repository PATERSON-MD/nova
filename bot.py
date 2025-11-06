#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 🎯 MODÈLES GROQ 2025 - TOUJOURS ACTUALISÉS :
AVAILABLE_MODELS = {
    # ✅ MODÈLES CONFIRMÉS 2024-2025
    "llama3.1-70b": "llama-3.1-70b-versatile",
    "llama3.1-8b": "llama-3.1-8b-instant", 
    "mixtral": "mixtral-8x7b-32768",
    "gemma2": "gemma2-9b-it",
    
    # 🔮 MODÈLES ATTENDUS 2025 (à tester)
    "llama3.2-70b": "llama-3.2-70b",  # Peut-être disponible bientôt
    "llama3.2-8b": "llama-3.2-8b",
    "qwen2-72b": "qwen2-72b-instruct",  # Nouveaux modèles chinois
}

# Fonction pour détecter automatiquement les modèles disponibles
def detect_available_models():
    available = {}
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Modèles à tester
    test_models = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "mixtral-8x7b-32768",
        "gemma2-9b-it",
        "llama-3.2-70b",  # Futur
        "llama-3.2-8b",   # Futur
        "qwen2-72b-instruct"  # Futur
    ]
    
    for model in test_models:
        try:
            payload = {
                "messages": [{"role": "user", "content": "Test"}],
                "model": model,
                "max_tokens": 5
            }
            response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                # Nom court pour les commandes
                short_name = model.split('-')[0] + model.split('-')[1]
                available[short_name] = model
                print(f"✅ Modèle détecté: {model}")
        except:
            continue
    
    return available

# Détection automatique au démarrage
print("🔍 Détection des modèles Groq 2025...")
ACTIVE_MODELS = detect_available_models()

# Si aucun modèle détecté, utiliser les garantis
if not ACTIVE_MODELS:
    ACTIVE_MODELS = {
        "llama3170b": "llama-3.1-70b-versatile",
        "llama318b": "llama-3.1-8b-instant",
        "mixtral": "mixtral-8x7b-32768"
    }
    print("⚠️  Utilisation des modèles par défaut")

SELECTED_MODEL = list(ACTIVE_MODELS.values())[0]  # Premier modèle disponible

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = f"""
🤖 **Bot Groq IA - Édition 2025 !** 🎉

🎯 **Commandes :**
/start - Démarrer
/models - Modèles disponibles  
/test - Test de connexion
/scan - Scanner nouveaux modèles
/current - Modèle actuel

🧠 **Modèle actuel :** {SELECTED_MODEL}
⚡ **Vitesse :** Réponses ultra-rapides
🔮 **IA 2025 :** Dernière génération

💬 **Posez-moi n'importe quelle question !**
    """
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['scan'])
def scan_models(message):
    bot.reply_to(message, "🔍 Scan des nouveaux modèles Groq...")
    global ACTIVE_MODELS, SELECTED_MODEL
    
    ACTIVE_MODELS = detect_available_models()
    
    if ACTIVE_MODELS:
        models_list = "\n".join([f"• {name} -> {model}" for name, model in ACTIVE_MODELS.items()])
        bot.reply_to(message, f"✅ Modèles détectés:\n{models_list}")
    else:
        bot.reply_to(message, "❌ Aucun modèle détecté")

@bot.message_handler(commands=['models'])
def models_command(message):
    models_text = f"""
🧠 **Modèles Groq 2025 Disponibles :**

"""
    
    for short_name, full_model in ACTIVE_MODELS.items():
        models_text += f"• **{short_name}** -> {full_model}\n"
    
    models_text += f"""
🔧 **Actuel :** {SELECTED_MODEL}
💡 **Changer :** /{ " /".join(ACTIVE_MODELS.keys())}
🔄 **Scanner :** /scan pour nouveaux modèles
    """
    bot.reply_to(message, models_text)

# Générer dynamiquement les handlers pour chaque modèle
for model_short in ACTIVE_MODELS.keys():
    @bot.message_handler(commands=[model_short])
    def change_model_dynamic(message, model_short=model_short):
        global SELECTED_MODEL
        SELECTED_MODEL = ACTIVE_MODELS[model_short]
        bot.reply_to(message, f"✅ Modèle changé pour : {SELECTED_MODEL}")

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
                    "content": f"Réponds UNIQUEMENT par '✅ 2025 - Modèle {SELECTED_MODEL} opérationnel !'"
                }
            ],
            "model": SELECTED_MODEL,
            "max_tokens": 50,
            "temperature": 0.1
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, f"🧪 {answer}\n\n🚀 Prêt pour 2025 !")
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
                    "content": "Tu es un assistant IA de pointe 2025. Réponds en français de manière claire, concise et moderne. Sois direct et utile."
                },
                {
                    "role": "user", 
                    "content": message.text
                }
            ],
            "model": SELECTED_MODEL,
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 0.9,
            "stream": False
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            bot.reply_to(message, answer)
            
        else:
            error_info = f"""
❌ **Erreur API 2025**

Code: {response.status_code}
Message: {response.text}

Modèle: {SELECTED_MODEL}
🔧 Essayez:
/models - pour changer
/scan - nouveaux modèles
/test - diagnostiquer
            """
            bot.reply_to(message, error_info)

    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Timeout - IA 2025 trop demandée!")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Erreur: {str(e)}")

print("🚀 Bot Groq 2025 - Intelligence Nouvelle Génération!")
print(f"🧠 Modèles détectés: {len(ACTIVE_MODELS)}")
print(f"🔑 Token Telegram: {'✅' if os.getenv('TELEGRAM_TOKEN') else '❌'}")
print(f"⚡ Clé Groq: {'✅' if GROQ_API_KEY else '❌'}")

bot.infinity_polling()
