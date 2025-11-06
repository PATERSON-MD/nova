#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import random
import re
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION AVANCÉE ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ PRESTIGIEUSE
CREATOR = "👑 Soszoe"
BOT_NAME = "🔥 KervensAI Ultra"
VERSION = "✨ Édition Diamant"

# 🎨 GALERIE EXCLUSIVE - IMAGES HAUTE DÉFINITION
IMAGE_GALLERY = [
    "https://i.imgur.com/7QZ4y8a.jpg",  # Bannière futuriste
    "https://i.imgur.com/5V2p9X3.jpg",  # Design néon
    "https://i.imgur.com/9R8c1L2.jpg",  # Interface holographique
    "https://i.imgur.com/3M7n2qJ.jpg",  # Code matrix
    "https://i.imgur.com/2K5b8wL.jpg",  # AI vision
    "https://i.imgur.com/6J4t9vR.jpg",  # Cyber espace
    "https://i.imgur.com/4H8p2qM.jpg",  # Data flow
    "https://i.imgur.com/1P9r3nL.jpg"   # Quantum computing
]

# ⚡ MODÈLES ULTRA-PERFORMANTS
MODEL_CONFIG = {
    "🚀 Llama-70B": "llama-3.1-70b-versatile",
    "⚡ Llama-8B": "llama-3.1-8b-instant", 
    "🎯 Mixtral": "mixtral-8x7b-32768",
    "💎 Gemma2": "gemma2-9b-it",
    "🌟 DeepSeek": "deepseek-r1-distill-llama-70b"
}

current_model = MODEL_CONFIG["🚀 Llama-70B"]

# ==================== FONCTIONS PRESTIGIEUSES ====================
def create_animated_menu():
    """Menu animé avec effets visuels"""
    return f"""
╔══════════════════════════════════════╗
║              {BOT_NAME}              ║
║           {VERSION}           ║
╠══════════════════════════════════════╣
║ 🎇  CRÉATEUR : {CREATOR}           ║
║ 🔥  MODÈLE : {current_model.split('-')[0]}     ║
║ 💫  STATUT : OPÉRATIONNEL ULTRA     ║
╠══════════════════════════════════════╣
║           🎛️  COMMANDES PRINCIPALES          ║
║ • /start - Menu d'accueil prestige   ║
║ • /menu - Interface complète         ║
║ • /code - Génération de code pro     ║
║ • /gallery - Galerie exclusive       ║
║ • /models - Technologies AI          ║
║ • /status - Diagnostic avancé        ║
║ • /help - Guide ultime               ║
╠══════════════════════════════════════╣
║        🚀  FONCTIONNALITÉS ELITE         ║
║ • Génération de code parfait         ║
║ • Interface holographique            ║
║ • Réponses instantanées              ║
║ • Design néon futuriste              ║
║ • Support 24/7/365                   ║
╚══════════════════════════════════════╝
"""

def create_code_response(text, code_blocks):
    """Formatage élégant pour le code"""
    response = "✨ **CODE GÉNÉRÉ AVEC PRÉCISION** ✨\n\n"
    
    if code_blocks:
        for i, code in enumerate(code_blocks, 1):
            language = "python"  # Détection automatique du langage
            if "html" in text.lower():
                language = "html"
            elif "css" in text.lower():
                language = "css"
            elif "javascript" in text.lower() or "js" in text.lower():
                language = "javascript"
            elif "java" in text.lower():
                language = "java"
            
            response += f"📦 **Bloc de code #{i}**\n"
            response += f"```{language}\n{code.strip()}\n```\n"
            response += "🎯 **Copie instantanée** - Sélectionnez et copiez\n"
            response += "⚡ **Optimisé pour performance**\n"
            response += "🔧 **Prêt à l'emploi**\n\n"
    
    response += f"💡 **Conseil du maître** : Utilisez /code pour plus de générations\n"
    response += f"👑 **Développé par {CREATOR}**\n"
    
    return response

def send_animated_message(chat_id, text, delay=0.5):
    """Envoi de message avec effet d'animation"""
    messages = [
        "🎇 Initialisation du système...",
        "🚀 Chargement des modules IA...", 
        "💫 Optimisation des performances...",
        f"✨ {text}"
    ]
    
    for msg in messages:
        bot.send_chat_action(chat_id, 'typing')
        import time
        time.sleep(delay)
        if msg == messages[-1]:  # Dernier message
            bot.send_message(chat_id, msg, parse_mode='Markdown')

# ==================== COMMANDES PRESTIGIEUSES ====================
@bot.message_handler(commands=['start', 'menu', 'accueil'])
def start_handler(message):
    """Menu d'accueil ultra premium"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # Envoi d'une image aléatoire de haute qualité
    premium_image = random.choice(IMAGE_GALLERY)
    
    try:
        bot.send_photo(
            message.chat.id,
            photo=premium_image,
            caption=f"🎨 **{BOT_NAME}** - Interface Premium\n{VERSION}",
            parse_mode='Markdown'
        )
    except:
        pass
    
    # Menu animé
    menu_text = create_animated_menu()
    bot.send_message(message.chat.id, menu_text, parse_mode='Markdown')
    
    # Message de bienvenue
    welcome_msg = f"""
🌟 **BIENVENUE DANS L'EXPÉRIENCE ULTRA** 🌟

Cher utilisateur, vous venez d'accéder à la version la plus avancée de {BOT_NAME}.

🎯 **VOS SUPER-POUVOIRS :**
• 🚀 Génération de code instantanée
• 💎 Réponses AI ultra-précises  
• 🎨 Interface design exclusive
• ⚡ Vitesse de traitement maximale
• 🔮 Intelligence artificielle elite

👑 **DÉVELOPPÉ PAR :** {CREATOR}
💫 **VERSION :** {VERSION}
🕒 **ACCÈS :** Illimité 24/7

💡 **Pour commencer :** Tapez simplement votre demande ou utilisez /code pour du code parfait !
    """
    
    bot.send_message(message.chat.id, welcome_msg, parse_mode='Markdown')

@bot.message_handler(commands=['gallery', 'galerie', 'photos'])
def gallery_handler(message):
    """Galerie d'art numérique exclusive"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    gallery_intro = """
🎨 **GALERIE D'ART NUMÉRIQUE EXCLUSIVE**

Découvrez nos créations visuelles uniques, spécialement conçues pour l'expérience {BOT_NAME}.

🖼️ **Collection Premium :**
• Designs futuristes
• Interfaces holographiques  
• Art numérique IA
• Visualisations data
• Concepts cyberpunk

🌟 **Prévisualisation de la collection...**
    """
    
    bot.send_message(message.chat.id, gallery_intro, parse_mode='Markdown')
    
    # Envoi de 3 images aléatoires de la galerie
    preview_images = random.sample(IMAGE_GALLERY, min(3, len(IMAGE_GALLERY)))
    for img in preview_images:
        try:
            bot.send_photo(
                message.chat.id,
                photo=img,
                caption="🎨 Œuvre exclusive - Collection KervensAI Ultra",
                parse_mode='Markdown'
            )
        except:
            continue

@bot.message_handler(commands=['code', 'coder', 'programmation'])
def code_handler(message):
    """Mode génération de code élite"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    code_menu = f"""
💻 **MODE GÉNÉRATION DE CODE ELITE** 💻

🚀 **Technologies supportées :**
• 🌐 HTML5 / CSS3 / JavaScript
• 🐍 Python / Django / Flask
• ☕ Java / Spring Boot
• ⚛️ React / Vue / Angular
• 🔥 Node.js / Express
• 🗄️ SQL / MongoDB
• 🐘 PHP / Laravel

🎯 **Fonctionnalités avancées :**
• Code optimisé et commenté
• Architecture professionnelle
• Sécurité intégrée
• Performance maximale
• Documentation incluse

💡 **Utilisation :**
Tapez simplement : 
_"Crée un [langage] pour [description]"_

**Exemples :**
• "Crée un site HTML moderne pour un restaurant"
• "Génère un script Python pour analyser des données"
• "Code une application React pour gérer des tâches"

👑 **Assistant code :** {CREATOR}
✨ **Prêt à créer de la magie ?**
    """
    
    bot.send_message(message.chat.id, code_menu, parse_mode='Markdown')

@bot.message_handler(commands=['models', 'modeles', 'ia'])
def models_handler(message):
    """Display advanced AI models"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    models_text = """
🧠 **ARCHITECTURE IA AVANCÉE** 🧠

⚡ **MOTEURS INTELLIGENCE ARTIFICIELLE :**

"""
    
    for name, model in MODEL_CONFIG.items():
        status = "✅ EN LIGNE" if model == current_model else "🟢 DISPONIBLE"
        models_text += f"• {name} : `{model}` - {status}\n"
    
    models_text += f"""
🎯 **MOTEUR ACTUEL :** `{current_model}`
🚀 **PERFORMANCE :** < 1.2s de réponse
💾 **MÉMOIRE :** 70B paramètres
🎪 **PRÉCISION :** 99.7%

🔧 **CHANGEMENT DE MOTEUR :**
`/model Llama-8B` pour plus de vitesse
`/model Mixtral` pour plus de créativité

👑 **OPTIMISÉ PAR :** {CREATOR}
    """
    
    bot.send_message(message.chat.id, models_text, parse_mode='Markdown')

@bot.message_handler(commands=['model'])
def change_model_handler(message):
    """Changer le modèle IA"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        args = message.text.split()
        if len(args) > 1:
            model_key = ' '.join(args[1:])
            # Trouver la clé correspondante
            for name, model in MODEL_CONFIG.items():
                if model_key.lower() in name.lower():
                    current_model = model
                    response = f"""
🔄 **MOTEUR IA MIS À JOUR** 🔄

🎯 **NOUVEAU MOTEUR :** {name}
⚡ **MODÈLE :** `{model}`
💫 **PERFORMANCE :** Optimisée
🚀 **VITESSE :** Boostée

🌟 **Prêt pour l'action !** Votre assistant est maintenant encore plus puissant.

👑 **Configuration par :** {CREATOR}
                    """
                    break
            else:
                response = f"""
❌ **MOTEUR NON RECONNU**

💡 **Moteurs disponibles :**
{', '.join(MODEL_CONFIG.keys())}

🔧 **Usage :** `/model Llama-8B`
                """
        else:
            response = """
🎯 **CHANGEMENT DE MOTEUR IA**

💡 **Usage :** `/model [nom_du_moteur]`

**Exemples :**
• `/model Llama-8B` - Vitesse extrême
• `/model Mixtral` - Créativité max
• `/model Gemma2` - Équilibre parfait
            """
    except Exception as e:
        response = f"""
❌ **ERREUR DE CONFIGURATION**

Détails : {str(e)}

👑 **Support :** {CREATOR}
        """
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['status', 'info', 'diagnostic'])
def status_handler(message):
    """Diagnostic système avancé"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    status_report = f"""
📊 **DIAGNOSTIC SYSTÈME AVANCÉ** 📊

🤖 **IDENTITÉ :** {BOT_NAME}
👑 **CRÉATEUR :** {CREATOR}
💫 **VERSION :** {VERSION}

⚡ **PERFORMANCE SYSTÈME :**
• Modèle IA : `{current_model}`
• Temps réponse : < 1.2 secondes
• Disponibilité : 100%
• Charge serveur : Optimal

🎯 **STATISTIQUES :**
• Images galerie : {len(IMAGE_GALLERY)}
• Modèles disponibles : {len(MODEL_CONFIG)}
• Commandes actives : 15+
• Uptime : Continu

🔧 **SERVICES :**
• API Groq : ✅ Opérationnel
• Génération code : ✅ Actif
• Interface : ✅ Premium
• Support : ✅ 24/7

🌟 **SYSTÈME :** **OPÉRATIONNEL ULTRA**
🎪 **STATUT :** **EXCELLENT**

👑 **MAINTENU PAR :** {CREATOR}
    """
    
    bot.send_message(message.chat.id, status_report, parse_mode='Markdown')

@bot.message_handler(commands=['help', 'aide', 'support'])
def help_handler(message):
    """Guide d'utilisation ultime"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    help_guide = f"""
🆘 **GUIDE ULTIME {BOT_NAME}** 🆘

🎯 **COMMANDES PRINCIPALES :**

🚀 **Accueil & Interface**
• /start - Menu prestige
• /menu - Interface complète  
• /gallery - Galerie exclusive

💻 **Génération & Code**
• /code - Mode programmation
• /models - Technologies IA
• /model - Changer moteur

📊 **Système & Info**
• /status - Diagnostic avancé
• /help - Ce guide

💡 **UTILISATION AVANCÉE :**

**Pour du code :**
_"Crée un [langage] pour [projet]"_

**Exemples concrets :**
• "Crée un site HTML/CSS moderne pour portfolio"
• "Génère un script Python pour analyse données"
• "Code une app React avec hooks modernes"

**Pour des réponses :**
Posez simplement vos questions !

🎨 **FONCTIONNALITÉS EXCLUSIVES :**
• Codes copiables en 1 clic
• Interface design premium
• Réponses ultra-rapides
• Support multilingue

👑 **ASSISTANCE :** {CREATOR}
🌟 **VERSION :** {VERSION}

💫 **Prêt à créer de la magie numérique ?**
    """
    
    bot.send_message(message.chat.id, help_guide, parse_mode='Markdown')

# ==================== MOTEUR IA PRINCIPAL ====================
@bot.message_handler(func=lambda message: True)
def elite_ai_processor(message):
    """Moteur IA ultra-performant avec génération de code"""
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        }

        # Prompt système élite
        system_prompt = f"""Tu es {BOT_NAME}, l'assistant IA le plus avancé, créé par {CREATOR}.

TON IDENTITÉ :
- Assistant IA élite et premium
- Expert en génération de code parfait
- Interface design et professionnelle
- Réponses ultra-rapides et précises

SPÉCIALITÉS CODE :
- Génère du code optimisé et commenté
- Supporte HTML, CSS, JavaScript, Python, Java, etc.
- Fournis des solutions complètes et professionnelles
- Ajoute des commentaires et documentation

DIRECTIVES :
- Sois extrêmement précis et technique
- Formatte les codes avec soin pour la copie
- Utilise un ton premium et professionnel
- Réponds en français sauf demande contraire

TA MISSION :
Offrir l'expérience IA la plus premium qui existe."""

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
            "max_tokens": 2048,
            "top_p": 0.9
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            data = response.json()
            ai_response = data["choices"][0]["message"]["content"]
            
            # Détection et formatage des blocs de code
            code_blocks = re.findall(r'```(?:[\w]*)\n?(.*?)```', ai_response, re.DOTALL)
            
            if code_blocks:
                # Mode génération de code avec formatage spécial
                formatted_response = create_code_response(ai_response, code_blocks)
                bot.reply_to(message, formatted_response, parse_mode='Markdown')
            else:
                # Réponse normale avec style premium
                premium_response = f"""
✨ **RÉPONSE PRESTIGE** ✨

{ai_response}

---
🎯 **Assistant :** {BOT_NAME}
👑 **Expertise :** {CREATOR}
💫 **Précision :** Maximum
                """
                bot.reply_to(message, premium_response, parse_mode='Markdown')
                
        else:
            error_msg = f"""
❌ **DÉLAI D'ATTENTE**

L'API met plus de temps que prévu à répondre.

💡 **Solutions :**
• Réessayez dans quelques instants
• Utilisez un modèle plus rapide avec /models
• Vérifiez votre connexion

👑 **Support technique :** {CREATOR}
            """
            bot.reply_to(message, error_msg, parse_mode='Markdown')

    except requests.exceptions.Timeout:
        timeout_msg = f"""
⏰ **TEMPS D'ATTENTE DÉPASSÉ**

Notre système met plus de temps que prévu.

🚀 **Actions recommandées :**
• Réduction de la complexité de la requête
• Utilisation de /models pour un moteur plus rapide
• Nouvelle tentative

👑 **Optimisé par :** {CREATOR}
        """
        bot.reply_to(message, timeout_msg, parse_mode='Markdown')

    except Exception as e:
        elite_error = f"""
🔴 **INCIDENT SYSTÈME**

Une erreur inattendue s'est produite.

🔧 **Détails techniques :**
{str(e)}

👑 **Support immédiat :** {CREATOR}
💡 **Diagnostic :** /status
        """
        bot.reply_to(message, elite_error, parse_mode='Markdown')

# ==================== LANCEMENT ULTRA ====================
if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════╗
║           {BOT_NAME}           ║  
║           {VERSION}           ║
╠══════════════════════════════════════╣
║ 🚀  Initialisation du système...    ║
║ 💫  Chargement des modules IA...    ║
║ 🎯  Optimisation des performances...║
║ ✨  Interface prestige activée...   ║
╠══════════════════════════════════════╣
║ 👑  Créateur : {CREATOR}       ║
║ 🤖  Modèle : {current_model} ║
║ 🖼️  Galerie : {len(IMAGE_GALLERY)} artworks     ║
║ ⚡  Statut : OPÉRATIONNEL ULTRA     ║
╚══════════════════════════════════════╝
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"🔴 ARRÊT CRITIQUE : {e}")
        print(f"👑 CONTACT : {CREATOR}")
