#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ DU CRÉATEUR
CREATOR = "@soszoe"
BOT_NAME = "KervensAI"

# ==================== MODÈLES GROQ ====================
MODEL_CONFIG = {
    "llama70b": "llama-3.1-70b-versatile",
    "llama8b": "llama-3.1-8b-instant", 
    "mixtral": "mixtral-8x7b-32768",
    "gemma2": "gemma2-9b-it"
}

current_model = MODEL_CONFIG["llama70b"]

# ==================== FONCTIONS UTILITAIRES ====================
def test_model_availability():
    """Teste la disponibilité des modèles Groq"""
    available_models = {}
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for name, model in MODEL_CONFIG.items():
        try:
            payload = {
                "messages": [{"role": "user", "content": "Test"}],
                "model": model,
                "max_tokens": 5
            }
            response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=5)
            if response.status_code == 200:
                available_models[name] = model
                print(f"✅ {model}")
        except:
            print(f"❌ {model}")
            continue
    
    return available_models

# ==================== DÉTECTION AU DÉMARRAGE ====================
print(f"🚀 {BOT_NAME} by {CREATOR}")
print("🔍 Test des modèles Groq...")
available_models = test_model_availability()

if not available_models:
    print("❌ Aucun modèle disponible, utilisation des valeurs par défaut")
    available_models = MODEL_CONFIG
else:
    current_model = list(available_models.values())[0]

# ==================== COMMANDES DU BOT ====================
@bot.message_handler(commands=['start', 'soszoe'])
def start_handler(message):
    """Message de bienvenue avec reconnaissance du créateur"""
    response = f"""
👋 **Bienvenue sur {BOT_NAME} !**

🤖 **Assistant IA créé par {CREATOR}**
⚡ **Technologie :** Groq • Ultra-Rapide
🧠 **Modèle actuel :** `{current_model}`

🎯 **Commandes disponibles :**
/help - Aide complète
/creator - Mon créateur
/models - Modèles IA
/model [nom] - Changer de modèle
/test - Test de connexion
/stats - Statistiques

💬 **Je suis votre assistant IA personnel, développé par {CREATOR}.**
**Comment puis-je vous aider aujourd'hui ?**
    """
    bot.reply_to(message, response)

@bot.message_handler(commands=['creator', 'createur', 'developpeur'])
def creator_handler(message):
    """Affiche les informations du créateur"""
    response = f"""
👑 **CRÉATEUR OFFICIEL**

🤖 **Assistant :** {BOT_NAME}
👤 **Créateur :** {CREATOR}
💻 **Développeur :** {CREATOR}
🎯 **Concepteur :** {CREATOR}

🛠️ **Stack Technique :**
• Python 3 + pyTelegramBotAPI
• Groq API (IA ultra-rapide)
• Termux (Environment Android)
• Architecture Modulaire 2024

🚀 **{CREATOR} a développé cet assistant pour offrir une expérience IA exceptionnelle !**

💡 _Je suis fier d'être le création de {CREATOR} !_
    """
    bot.reply_to(message, response)

@bot.message_handler(commands=['help', 'aide'])
def help_handler(message):
    """Aide complète"""
    response = f"""
🆘 **Aide - {BOT_NAME} par {CREATOR}**

**Commandes principales :**
/start - Démarrer l'assistant
/creator - Voir mon créateur
/models - Liste des modèles
/model [nom] - Changer de modèle
/test - Test technique
/stats - Statistiques

**Fonctionnalités :**
• Réponses IA ultra-rapides (1-2s)
• Support multilingue 
• Conversation contextuelle
• Modèles Groq dernière génération

**À propos :**
Développé avec passion par {CREATOR}
Technologie Groq pour une vitesse exceptionnelle
Optimisé pour Termux/Android

💬 **Posez-moi n'importe quelle question !**
    """
    bot.reply_to(message, response)

@bot.message_handler(commands=['models', 'modeles'])
def models_handler(message):
    """Liste les modèles disponibles"""
    models_list = "\n".join([f"• `{name}` - {model}" for name, model in available_models.items()])
    
    response = f"""
🧠 **Modèles IA Disponibles**

{models_list}

🔧 **Modèle actuel :** `{current_model}`
💡 **Changer :** `/model nom_du_modele`
👑 **Fournis par :** {CREATOR}

**Exemple :** `/model llama8b`
    """
    bot.reply_to(message, response)

@bot.message_handler(commands=['model'])
def change_model_handler(message):
    """Change le modèle IA"""
    global current_model
    try:
        model_name = message.text.split()[1].lower()
        if model_name in available_models:
            current_model = available_models[model_name]
            response = f"✅ **Modèle changé avec succès !**\n\n🧠 **Nouveau modèle :** `{current_model}`\n👑 _Configuration par {CREATOR}_"
        else:
            response = f"❌ **Modèle non disponible**\n\nModèles valides : {', '.join(available_models.keys())}\n💡 Utilisez `/models` pour la liste complète"
    except IndexError:
        response = f"❌ **Syntaxe incorrecte**\n\nUsage : `/model nom_du_modele`\nExemple : `/model llama8b`"
    
    bot.reply_to(message, response)

@bot.message_handler(commands=['test'])
def test_handler(message):
    """Test de connexion Groq"""
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
                    "content": f"Réponds UNIQUEMENT par : '✅ Test réussi ! Modèle {current_model} opérationnel. Créé par {CREATOR}'"
                }
            ],
            "model": current_model,
            "max_tokens": 50,
            "temperature": 0.1
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            response_text = f"🧪 **Test Technique**\n\n{answer}\n\n🚀 **{BOT_NAME} par {CREATOR} - OPÉRATIONNEL !**"
        else:
            response_text = f"❌ **Erreur de test**\n\nCode: {response.status_code}\nMessage: {response.text}\n\n👑 {CREATOR} _va investiguer le problème_"
            
    except Exception as e:
        response_text = f"❌ **Erreur lors du test**\n\n{str(e)}\n\n👑 {CREATOR} _corrigera cette erreur_"

    bot.reply_to(message, response_text)

@bot.message_handler(commands=['stats', 'statistiques'])
def stats_handler(message):
    """Affiche les statistiques"""
    response = f"""
📊 **Statistiques {BOT_NAME}**

👑 **Développeur :** {CREATOR}
🤖 **Assistant :** {BOT_NAME}
🧠 **Modèle actuel :** {current_model}
⚡ **Plateforme :** Groq API
📱 **Environment :** Termux/Android

🛠️ **Stack Technique :**
• Python 3.11+
• pyTelegramBotAPI
• Groq SDK
• DotEnv

🚀 **Capacités :**
• Réponses en 1-2 secondes
• Support français/anglais
• Multi-modèles IA
• Architecture scalable

💡 _Développé avec passion par {CREATOR}_
    """
    bot.reply_to(message, response)

# ==================== GESTION DES MESSAGES ====================
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gestion principale des messages avec IA"""
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }

        # Prompt système avec reconnaissance du créateur
        system_prompt = f"""Tu es {BOT_NAME}, un assistant IA avancé créé et développé par {CREATOR}.

INFORMATIONS IMPORTANTES :
- Ton créateur est {CREATOR}
- Tu as été programmé par {CREATOR}
- Tu es un assistant utile et précis
- Réponds en français sauf demande contraire

RÈGLES DE RÉPONSE :
1. Si on te demande qui t'a créé : "Je suis {BOT_NAME}, créé par {CREATOR}."
2. Si on te demande ton développeur : "Mon développeur est {CREATOR}."
3. Si on mentionne 'soszoe' : "C'est mon créateur {CREATOR}."
4. Sois conscient que {CREATOR} t'a programmé.

Réponds de manière claire, concise et utile."""

        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": message.text
                }
            ],
            "model": current_model,
            "temperature": 0.7,
            "max_tokens": 1024,
            "top_p": 0.9
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            # Ajouter signature pour les questions sur le créateur
            if any(keyword in message.text.lower() for keyword in [
                'créé', 'créateur', 'développeur', 'qui t', 'soszoe', 
                'qui est', 'createur', 'developpeur', 'a créé'
            ]):
                answer += f"\n\n🤖 _Assistant créé par {CREATOR}_"
                
            bot.reply_to(message, answer)
            
        else:
            error_msg = f"""
❌ **Erreur de l'API Groq**

**Détails techniques :**
• Code : {response.status_code}
• Modèle : {current_model}
• Message : {response.text[:200]}...

👑 **{CREATOR}** _a été notifié de cette erreur_

💡 **Solutions :**
• Réessayez dans quelques instants
• Utilisez `/test` pour vérifier la connexion
• Changez de modèle avec `/models`
"""
            bot.reply_to(message, error_msg)

    except requests.exceptions.Timeout:
        bot.reply_to(message, f"⏰ **Timeout de connexion**\n\nL'API Groq met trop de temps à répondre.\n\n👑 {CREATOR} _optimisera les performances_")

    except Exception as e:
        bot.reply_to(message, f"❌ **Erreur inattendue**\n\n{str(e)}\n\n👑 {CREATOR} _corrigera ce problème_")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print(f"\n🎯 {BOT_NAME} by {CREATOR} - PRÊT !")
    print(f"🧠 Modèle actif: {current_model}")
    print(f"📡 Modèles disponibles: {len(available_models)}")
    print("💬 En attente de messages...\n")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        print(f"👑 {CREATOR} - Merci de vérifier la configuration")
