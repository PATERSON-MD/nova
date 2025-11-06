#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import random
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ DU CRÉATEUR
CREATOR = "@soszoe"
BOT_NAME = "KervensAI"

# 🖼️ GALERIE D'IMAGES
IMAGE_GALLERY = [
    "https://files.catbox.moe/601u5z.jpg",  # Logo 1
    "https://files.catbox.moe/qmxfpk.jpg",  # Logo 2  
    "https://files.catbox.moe/77iazb.jpg",  # Logo 3
    "https://files.catbox.moe/6ty1v0.jpg",  # Logo 4
    "https://files.catbox.moe/tta6ta.jpg"   # Logo original
]

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
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Choisir une image aléatoire pour le start
    random_logo = random.choice(IMAGE_GALLERY)
    
    response = f"""
👋 **Bienvenue sur {BOT_NAME} !**

🤖 **Assistant IA créé par {CREATOR}**
⚡ **Technologie :** Groq • Ultra-Rapide
🧠 **Modèle actuel :** `{current_model}`
🖼️ **Galerie :** {len(IMAGE_GALLERY)} logos disponibles

🎯 **Commandes disponibles :**
/help - Aide complète
/creator - Mon créateur
/logo - Voir un logo aléatoire
/gallery - Voir tous les logos
/models - Modèles IA
/model [nom] - Changer de modèle
/test - Test de connexion
/stats - Statistiques

💬 **Je suis votre assistant IA personnel, développé par {CREATOR}.**
**Comment puis-je vous aider aujourd'hui ?**

🎨 *Découvrez mes logos avec* /gallery
    """
    bot.reply_to(message, response, parse_mode='Markdown')
    
    # Envoyer aussi un logo avec le start
    bot.send_photo(
        message.chat.id, 
        photo=random_logo,
        caption=f"🎨 **Logo {BOT_NAME}**\n👑 _Créé par {CREATOR}_\n💡 Utilisez /gallery pour voir tous les logos",
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['logo', 'image', 'photo'])
def logo_handler(message):
    """Envoie un logo aléatoire"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    random_logo = random.choice(IMAGE_GALLERY)
    logo_number = IMAGE_GALLERY.index(random_logo) + 1
    
    caption = f"""
🎨 **Logo {BOT_NAME} #{logo_number}**

🤖 Assistant : {BOT_NAME}
👑 Créateur : {CREATOR}
🖼️ Galerie : {logo_number}/{len(IMAGE_GALLERY)}

💡 *Logo conçu avec passion par {CREATOR}*
🔄 *Utilisez* /gallery *pour voir tous les logos*
    """
    
    try:
        bot.send_photo(
            message.chat.id, 
            photo=random_logo,
            caption=caption,
            parse_mode='Markdown'
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Impossible d'afficher le logo\n\nLien direct : {random_logo}")

@bot.message_handler(commands=['gallery', 'galerie', 'logos'])
def gallery_handler(message):
    """Affiche tous les logos disponibles"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    gallery_info = f"""
🖼️ **Galerie {BOT_NAME}**

📸 **{len(IMAGE_GALLERY)} logos disponibles** créés par {CREATOR}

**Logos disponibles :**
"""
    
    for i, logo_url in enumerate(IMAGE_GALLERY, 1):
        gallery_info += f"• Logo #{i} - {logo_url}\n"
    
    gallery_info += f"""
**Commandes :**
/logo - Logo aléatoire
/gallery - Cette galerie

👑 **Design par :** {CREATOR}
🎯 **Assistant :** {BOT_NAME}

💡 *Chaque logo représente l'innovation et la modernité de {BOT_NAME}*
    """
    
    bot.reply_to(message, gallery_info, parse_mode='Markdown')
    
    # Envoyer 2 logos aléatoires en preview
    preview_logos = random.sample(IMAGE_GALLERY, min(2, len(IMAGE_GALLERY)))
    for logo in preview_logos:
        try:
            bot.send_photo(
                message.chat.id, 
                photo=logo,
                caption=f"🖼️ Preview Galerie {BOT_NAME}\n👑 par {CREATOR}",
                parse_mode='Markdown'
            )
        except:
            continue

@bot.message_handler(commands=['logo1', 'logo2', 'logo3', 'logo4', 'logo5'])
def specific_logo_handler(message):
    """Envoie un logo spécifique"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    logo_commands = {
        'logo1': 0, 'logo2': 1, 'logo3': 2, 
        'logo4': 3, 'logo5': 4
    }
    
    command = message.text[1:].lower()  # Enlever le /
    
    if command in logo_commands and logo_commands[command] < len(IMAGE_GALLERY):
        logo_index = logo_commands[command]
        logo_url = IMAGE_GALLERY[logo_index]
        
        caption = f"""
🎨 **Logo {BOT_NAME} #{logo_index + 1}**

🤖 Assistant : {BOT_NAME}
👑 Créateur : {CREATOR}
🖼️ Spécifique : Logo {logo_index + 1}

💡 *Design exclusif par {CREATOR}*
🔄 *Utilisez* /logo *pour un logo aléatoire*
        """
        
        try:
            bot.send_photo(
                message.chat.id, 
                photo=logo_url,
                caption=caption,
                parse_mode='Markdown'
            )
        except Exception as e:
            bot.reply_to(message, f"❌ Impossible d'afficher le logo #{logo_index + 1}\n\nLien direct : {logo_url}")
    else:
        bot.reply_to(message, f"❌ Logo non disponible\n\nLogos disponibles : 1 à {len(IMAGE_GALLERY)}\nUtilisez /logo1 à /logo{len(IMAGE_GALLERY)}")

@bot.message_handler(commands=['creator', 'createur', 'developpeur'])
def creator_handler(message):
    """Affiche les informations du créateur"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    response = f"""
👑 **CRÉATEUR OFFICIEL**

🤖 **Assistant :** {BOT_NAME}
👤 **Créateur :** {CREATOR}
💻 **Développeur :** {CREATOR}
🎯 **Concepteur :** {CREATOR}
🎨 **Designer :** {CREATOR}

🛠️ **Stack Technique :**
• Python 3 + pyTelegramBotAPI
• Groq API (IA ultra-rapide)
• Termux (Environment Android)
• Architecture Modulaire 2024

🖼️ **Design :**
• {len(IMAGE_GALLERY)} logos créés
• Identité visuelle unique
• Design moderne et innovant

🚀 **{CREATOR} a développé cet assistant pour offrir une expérience IA exceptionnelle !**

🎨 *Découvrez mes créations :* /gallery
    """
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['help', 'aide'])
def help_handler(message):
    """Aide complète"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    response = f"""
🆘 **Aide - {BOT_NAME} par {CREATOR}**

**Commandes principales :**
/start - Démarrer l'assistant
/creator - Voir mon créateur
/logo - Logo aléatoire
/gallery - Tous les logos
/logo1 à /logo5 - Logo spécifique
/models - Liste des modèles
/model [nom] - Changer de modèle
/test - Test technique
/stats - Statistiques

**Fonctionnalités :**
• Réponses IA ultra-rapides (1-2s)
• Support multilingue 
• Conversation contextuelle
• Modèles Groq dernière génération
• Galerie de {len(IMAGE_GALLERY)} logos

**À propos :**
Développé avec passion par {CREATOR}
Technologie Groq pour une vitesse exceptionnelle
Optimisé pour Termux/Android

🎨 **Galerie :** {len(IMAGE_GALLERY)} logos disponibles avec /gallery

💬 **Posez-moi n'importe quelle question !**
    """
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['models', 'modeles'])
def models_handler(message):
    """Liste les modèles disponibles"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    models_list = "\n".join([f"• `{name}` - {model}" for name, model in available_models.items()])
    
    response = f"""
🧠 **Modèles IA Disponibles**

{models_list}

🔧 **Modèle actuel :** `{current_model}`
💡 **Changer :** `/model nom_du_modele`
👑 **Fournis par :** {CREATOR}

**Exemple :** `/model llama8b`
    """
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['model'])
def change_model_handler(message):
    """Change le modèle IA"""
    bot.send_chat_action(message.chat.id, 'typing')
    
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
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['test'])
def test_handler(message):
    """Test de connexion Groq"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
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

    bot.reply_to(message, response_text, parse_mode='Markdown')

@bot.message_handler(commands=['stats', 'statistiques'])
def stats_handler(message):
    """Affiche les statistiques"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    response = f"""
📊 **Statistiques {BOT_NAME}**

👑 **Développeur :** {CREATOR}
🤖 **Assistant :** {BOT_NAME}
🧠 **Modèle actuel :** {current_model}
⚡ **Plateforme :** Groq API
📱 **Environment :** Termux/Android
🎨 **Logos :** {len(IMAGE_GALLERY)} designs

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
• Galerie de logos

🎨 **Galerie :** /gallery pour {len(IMAGE_GALLERY)} logos

💡 _Développé avec passion par {CREATOR}_
    """
    bot.reply_to(message, response, parse_mode='Markdown')

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
- Tu as une galerie de {len(IMAGE_GALLERY)} logos créés par {CREATOR}

RÈGLES DE RÉPONSE :
1. Si on te demande qui t'a créé : "Je suis {BOT_NAME}, créé par {CREATOR}."
2. Si on te demande ton développeur : "Mon développeur est {CREATOR}."
3. Si on mentionne 'soszoe' : "C'est mon créateur {CREATOR}."
4. Si on te parle de logos : "J'ai {len(IMAGE_GALLERY)} logos créés par {CREATOR}, utilisez /gallery"
5. Sois conscient que {CREATOR} t'a programmé et designé.

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
                'qui est', 'createur', 'developpeur', 'a créé', 'logo',
                'image', 'photo', 'design', 'galerie'
            ]):
                answer += f"\n\n🤖 _Assistant créé par {CREATOR}_\n🎨 _Découvrez mes logos avec_ /gallery"
                
            bot.reply_to(message, answer, parse_mode='Markdown')
            
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
            bot.reply_to(message, error_msg, parse_mode='Markdown')

    except requests.exceptions.Timeout:
        bot.reply_to(message, f"⏰ **Timeout de connexion**\n\nL'API Groq met trop de temps à répondre.\n\n👑 {CREATOR} _optimisera les performances_", parse_mode='Markdown')

    except Exception as e:
        bot.reply_to(message, f"❌ **Erreur inattendue**\n\n{str(e)}\n\n👑 {CREATOR} _corrigera ce problème_", parse_mode='Markdown')

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print(f"\n🎯 {BOT_NAME} by {CREATOR} - PRÊT !")
    print(f"🧠 Modèle actif: {current_model}")
    print(f"📡 Modèles disponibles: {len(available_models)}")
    print(f"🎨 Logos disponibles: {len(IMAGE_GALLERY)}")
    print("💬 En attente de messages...\n")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        print(f"👑 {CREATOR} - Merci de vérifier la configuration")
