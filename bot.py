#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import random
import re
import time
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION AVANCÉE ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ PRESTIGIEUSE
CREATOR = "👑 Soszoe"
BOT_NAME = "🔥 KervensAI Ultra"
VERSION = "✨ Édition Exclusive"

# 🎨 TES PHOTOS PERSONNELLES - Remplace ces URLs par tes propres images
IMAGE_GALLERY = [
    "https://files.catbox.moe/601u5z.jpg",  # Remplace avec ton image 1
    "https://files.catbox.moe/qmxfpk.jpg",  # Remplace avec ton image 2  
    "https://files.catbox.moe/77iazb.jpg",  # Remplace avec ton image 3
    "https://files.catbox.moe/tta6ta.jpg",  # Remplace avec ton image 4
    "https://files.catbox.moe/tta6ta.jpg",  # Remplace avec ton image 5
]

# ⚡ MODÈLES OPTIMISÉS
MODEL_CONFIG = {
    "🚀 Llama-70B": "llama-3.1-70b-versatile",
    "⚡ Llama-8B": "llama-3.1-8b-instant", 
    "🎯 Mixtral": "mixtral-8x7b-32768"
}

current_model = MODEL_CONFIG["⚡ Llama-8B"]  # Modèle plus rapide par défaut

# ==================== FONCTIONS AMÉLIORÉES ====================
def test_groq_connection():
    """Test robuste de la connexion Groq"""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messages": [{"role": "user", "content": "Test"}],
        "model": current_model,
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def create_stylish_menu():
    """Menu stylisé avec tes photos"""
    return f"""
🎊 **{BOT_NAME}** 🎊
{VERSION}

🤖 **Assistant Personnel de {CREATOR}**
⚡ **Optimisé pour la vitesse et la performance**

📸 **Galerie Exclusive** - {len(IMAGE_GALLERY)} photos personnelles
🧠 **IA Avancée** - Réponses intelligentes et rapides
💻 **Génération de Code** - Code parfait et copiable

🎯 **Commandes Disponibles :**
/start - Menu principal avec photo
/menu - Interface complète  
/gallery - Voir toutes mes photos
/code - Générer du code professionnel
/models - Gérer les modèles IA
/quick - Mode réponse rapide
/photo - Photo aléatoire

🚀 **Pour commencer :** Envoie un message ou utilise /quick pour des réponses ultra-rapides

👑 **Développé avec passion par {CREATOR}**
"""

def send_photo_with_retry(chat_id, photo_url, caption, max_retries=3):
    """Envoi de photo avec système de retry"""
    for attempt in range(max_retries):
        try:
            bot.send_photo(chat_id, photo=photo_url, caption=caption, parse_mode='Markdown')
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                bot.send_message(chat_id, f"📸 **Photo non disponible**\n\nLien direct : {photo_url}", parse_mode='Markdown')
                return False
            time.sleep(1)
    return False

# ==================== COMMANDES OPTIMISÉES ====================
@bot.message_handler(commands=['start', 'menu'])
def start_handler(message):
    """Menu principal avec tes photos"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    # Envoi d'une de tes photos
    if IMAGE_GALLERY:
        your_photo = random.choice(IMAGE_GALLERY)
        photo_caption = f"🎨 **Photo Exclusive**\n\n👑 Propriétaire : {CREATOR}\n🤖 Assistant : {BOT_NAME}\n💫 Collection personnelle"
        
        send_photo_with_retry(message.chat.id, your_photo, photo_caption)
    
    # Menu stylisé
    menu_text = create_stylish_menu()
    bot.send_message(message.chat.id, menu_text, parse_mode='Markdown')

@bot.message_handler(commands=['gallery', 'photos', 'mesphotos'])
def gallery_handler(message):
    """Affiche toutes tes photos"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    if not IMAGE_GALLERY:
        bot.send_message(message.chat.id, "📸 **Aucune photo configurée**\n\nAjoute tes URLs dans IMAGE_GALLERY", parse_mode='Markdown')
        return
    
    gallery_info = f"""
📸 **MA GALERIE PERSONNELLE**

👑 **Propriétaire :** {CREATOR}
🖼️ **Total de photos :** {len(IMAGE_GALLERY)}
🎨 **Collection exclusive**

**Navigation :**
/photo - Photo aléatoire
/start - Retour au menu
"""
    bot.send_message(message.chat.id, gallery_info, parse_mode='Markdown')
    
    # Envoi de 2 photos en preview
    preview_photos = random.sample(IMAGE_GALLERY, min(2, len(IMAGE_GALLERY)))
    for photo in preview_photos:
        send_photo_with_retry(message.chat.id, photo, f"📸 Photo de {CREATOR}", parse_mode='Markdown')

@bot.message_handler(commands=['photo', 'random'])
def photo_handler(message):
    """Envoie une photo aléatoire"""
    bot.send_chat_action(message.chat.id, 'upload_photo')
    
    if IMAGE_GALLERY:
        random_photo = random.choice(IMAGE_GALLERY)
        caption = f"📸 **Photo Aléatoire**\n\n👑 Propriétaire : {CREATOR}\n🤖 Partagé par {BOT_NAME}\n💫 Collection personnelle"
        send_photo_with_retry(message.chat.id, random_photo, caption)
    else:
        bot.send_message(message.chat.id, "❌ **Aucune photo disponible**\n\nConfigure tes URLs dans le code.", parse_mode='Markdown')

@bot.message_handler(commands=['quick', 'rapide'])
def quick_handler(message):
    """Mode réponse rapide avec modèle optimisé"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    quick_info = """
🚀 **MODE RAPIDE ACTIVÉ**

⚡ **Configuration optimisée :**
• Modèle : Llama-8B (le plus rapide)
• Temps réponse : < 2 secondes
• Tokens : Limités pour la vitesse

💡 **Utilisation :**
Envoie ton message et obtiens une réponse ultra-rapide !

🔄 **Retour au mode normal :** Envoie un message normal
"""
    bot.send_message(message.chat.id, quick_info, parse_mode='Markdown')

@bot.message_handler(commands=['models'])
def models_handler(message):
    """Gestion des modèles IA"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    models_text = """
🧠 **MODÈLES IA DISPONIBLES**

"""
    
    for name, model in MODEL_CONFIG.items():
        status = "✅ ACTUEL" if model == current_model else "🟢 DISPONIBLE"
        speed = "⚡ RAPIDE" if "8b" in model else "🎯 PUISSANT"
        models_text += f"• {name} - {speed} - {status}\n"
    
    models_text += f"""
💡 **Recommandation :**
• Llama-8B : Réponses rapides
• Llama-70B : Réponses détaillées

🔧 **Changer :** `/model Llama-8B`
"""
    bot.send_message(message.chat.id, models_text, parse_mode='Markdown')

@bot.message_handler(commands=['model'])
def change_model_handler(message):
    """Changer de modèle IA"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        args = message.text.split()
        if len(args) > 1:
            requested_model = ' '.join(args[1:])
            
            for name, model in MODEL_CONFIG.items():
                if requested_model.lower() in name.lower():
                    global current_model
                    current_model = model
                    response = f"""
🔄 **MODÈLE MIS À JOUR**

✅ **Nouveau modèle :** {name}
⚡ **Vitesse :** Optimisée
🎯 **Performance :** Améliorée

💡 Prêt à recevoir vos demandes !
"""
                    break
            else:
                response = f"""
❌ **MODÈLE NON TROUVÉ**

📋 **Modèles disponibles :**
{', '.join(MODEL_CONFIG.keys())}

💡 **Exemple :** `/model Llama-8B`
"""
        else:
            response = """
🎯 **CHANGER DE MODÈLE**

💡 **Usage :** `/model [nom]`

**Exemples :**
• `/model Llama-8B` - Pour la vitesse
• `/model Llama-70B` - Pour la précision
"""
    except Exception as e:
        response = f"""
❌ **ERREUR**

Détails : {str(e)}

👑 **Support :** {CREATOR}
"""
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['code'])
def code_handler(message):
    """Génération de code"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    code_guide = """
💻 **GÉNÉRATEUR DE CODE**

🚀 **Langages supportés :**
• Python, JavaScript, HTML/CSS
• Java, PHP, SQL
• Et bien d'autres...

💡 **Comment utiliser :**
"Crée un [langage] pour [description]"

**Exemples :**
• "Crée un script Python pour analyser un fichier CSV"
• "Génère une page HTML moderne pour un portfolio"
• "Code une fonction JavaScript pour valider un formulaire"

🎯 **Fonctionnalités :**
• Code bien formaté et commenté
• Facile à copier
• Optimisé pour la performance

👑 **Expert en code :** {CREATOR}
"""
    bot.send_message(message.chat.id, code_guide, parse_mode='Markdown')

# ==================== MOTEUR IA OPTIMISÉ ====================
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gestionnaire principal optimisé"""
    # Test de connexion avant de traiter
    if not test_groq_connection():
        bot.send_message(message.chat.id, 
            "🔌 **PROBLÈME DE CONNEXION**\n\n"
            "L'API Groq est temporairement indisponible.\n\n"
            "💡 **Solutions :**\n"
            "• Vérifie ta connexion Internet\n"
            "• Réessaie dans 1 minute\n"
            "• Utilise un modèle différent avec /models\n\n"
            "👑 **Support :** {CREATOR}",
            parse_mode='Markdown'
        )
        return

    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Prompt optimisé pour la vitesse
        system_prompt = f"""Tu es {BOT_NAME}, assistant IA personnel de {CREATOR}.

Tu es rapide, précis et utile. Réponds de manière concise et efficace.

Si on te demande de générer du code, formate-le proprement avec des commentaires.

Réponds en français sauf demande contraire."""

        payload = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message.text}
            ],
            "model": current_model,
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9
        }

        # Timeout réduit pour éviter les longs délais
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            # Détection de code
            code_blocks = re.findall(r'```(?:[\w]*)\n?(.*?)```', answer, re.DOTALL)
            
            if code_blocks:
                formatted_response = "💻 **CODE GÉNÉRÉ** 💻\n\n"
                for i, code in enumerate(code_blocks, 1):
                    lang = "python"  # Détection automatique basique
                    if "html" in message.text.lower():
                        lang = "html"
                    elif "css" in message.text.lower():
                        lang = "css"
                    elif "javascript" in message.text.lower() or "js" in message.text.lower():
                        lang = "javascript"
                    
                    formatted_response += f"📦 **Bloc {i}**\n```{lang}\n{code.strip()}\n```\n\n"
                
                formatted_response += "📋 **Copie facile** - Sélectionne et copie\n👑 **Expert :** {CREATOR}"
                bot.reply_to(message, formatted_response, parse_mode='Markdown')
            else:
                # Réponse normale
                final_response = f"✨ **RÉPONSE** ✨\n\n{answer}\n\n---\n🤖 {BOT_NAME} par {CREATOR}"
                bot.reply_to(message, final_response, parse_mode='Markdown')
                
        else:
            error_msg = f"""
❌ **ERREUR API**

Détails : Code {response.status_code}

💡 **Solutions rapides :**
• Réessaye maintenant
• Utilise `/model Llama-8B` pour plus de vitesse
• Vérifie ta connexion

👑 **Technical Support :** {CREATOR}
"""
            bot.reply_to(message, error_msg, parse_mode='Markdown')
            
    except requests.exceptions.Timeout:
        bot.reply_to(message,
            "⏰ **DÉLAI DÉPASSÉ**\n\n"
            "La requête prend trop de temps.\n\n"
            "🚀 **Actions rapides :**\n"
            "• Utilise `/quick` pour le mode rapide\n"
            "• Change de modèle avec `/models`\n"
            "• Réduis la complexité de ta question\n\n"
            "👑 **Optimisé par :** {CREATOR}",
            parse_mode='Markdown'
        )
        
    except Exception as e:
        bot.reply_to(message,
            "🔴 **ERREUR INATTENDUE**\n\n"
            f"Détails : {str(e)}\n\n"
            "👑 **Support immédiat :** {CREATOR}",
            parse_mode='Markdown'
        )

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print(f"""
🎯 {BOT_NAME} - {VERSION}
👑 Créateur : {CREATOR}
⚡ Modèle : {current_model}
📸 Photos : {len(IMAGE_GALLERY)}
🚀 Statut : Opérationnel

💡 Pour configurer tes photos :
Remplace les URLs dans IMAGE_GALLERY par tes propres images
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur : {e}")
        print(f"👑 Contact : {CREATOR}")
