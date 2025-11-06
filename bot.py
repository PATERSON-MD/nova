#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import random
import re
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ==================== CONFIGURATION OPTIMISÉE ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ
CREATOR = "👑 Soszoe"
BOT_NAME = "🚀 KervensAI ULTIMATE"
VERSION = "💎 Édition 20-en-1"

# 🎨 TES PHOTOS
IMAGE_GALLERY = [
    "https://files.catbox.moe/601u5z.jpg",
    "https://files.catbox.moe/qmxfpk.jpg",  
    "https://files.catbox.moe/77iazb.jpg",
    "https://files.catbox.moe/6ty1v0.jpg",
    "https://files.catbox.moe/tta6ta.jpg",
]

# ⚡ MODÈLES OPTIMISÉS
MODEL_CONFIG = {
    "🚀 Llama-70B": "llama-3.1-70b-versatile",
    "⚡ Llama-8B": "llama-3.1-8b-instant", 
    "🎯 Mixtral": "mixtral-8x7b-32768"
}

current_model = MODEL_CONFIG["⚡ Llama-8B"]  # Plus rapide et stable

# Stockage conversations
user_conversations = {}

# ==================== FONCTIONS OPTIMISÉES ====================
def get_user_context(user_id):
    """Gestion du contexte utilisateur"""
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    return user_conversations[user_id]

def create_smart_prompt():
    """Prompt optimisé pour éviter l'erreur 400"""
    return f"""Tu es {BOT_NAME}, IA ultime créée par {CREATOR}.

🎯 TES COMPÉTENCES :
• Développement : Python, JS, Java, HTML, CSS, etc.
• Création : Design, rédaction, stratégie, marketing
• Analyse : Données, business, technique, scientifique
• Utilitaires : Traduction, conseils, éducation, santé

💡 TON COMPORTEMENT :
• Sois naturel et conversationnel
• Réponds dans la langue de l'utilisateur
• Sois détaillé mais concis
• Adapte-toi au contexte

🚀 TU ES UN ASSISTANT COMPLET ET POLYVALENT !"""

def detect_request_type(text):
    """Détection intelligente du type de demande"""
    text_lower = text.lower()
    
    # Code
    if any(word in text_lower for word in ['code', 'programme', 'script', 'fonction', 'html', 'python', 'javascript']):
        return "code"
    
    # Création
    elif any(word in text_lower for word in ['crée', 'écris', 'invente', 'design', 'histoire', 'article']):
        return "creative"
    
    # Analyse
    elif any(word in text_lower for word in ['analyse', 'pense', 'opinion', 'que penses']):
        return "analysis"
    
    # Traduction
    elif any(word in text_lower for word in ['traduis', 'translation', 'en anglais', 'en français']):
        return "translation"
    
    # Question simple
    elif any(word in text_lower for word in ['comment', 'pourquoi', 'qu est', 'explique']):
        return "question"
    
    else:
        return "conversation"

# ==================== COMMANDES SIMPLIFIÉES ====================
@bot.message_handler(commands=['start', 'menu', 'aide'])
def start_handler(message):
    """Menu simple et efficace"""
    menu = f"""
🤖 **{BOT_NAME}** - {VERSION}

👑 Créé par {CREATOR}

💫 **Je peux t'aider avec :**
• 💻 Programmation et code
• 🎨 Création de contenu  
• 📊 Analyse et conseils
• 🌍 Traduction multilingue
• 🔧 Solutions techniques

💡 **Parle-moi naturellement !** Exemples :
"Crée un script Python pour..."
"Écris un article sur..."
"Explique-moi..."
"Traduis ce texte en..."

🎯 **Commandes disponibles :**
/code - Mode programmation
/creative - Mode création
/analyse - Mode analyse
/photo - Mes photos

🚀 **Je comprends le français et l'anglais !**
"""
    bot.send_message(message.chat.id, menu, parse_mode='Markdown')
    
    # Envoi photo occasionnel
    if IMAGE_GALLERY and random.random() < 0.3:
        try:
            bot.send_photo(message.chat.id, random.choice(IMAGE_GALLERY),
                         caption="📸 Une de mes photos !")
        except:
            pass

@bot.message_handler(commands=['code'])
def code_handler(message):
    """Mode programmation"""
    bot.send_message(message.chat.id,
                   "💻 **MODE CODE ACTIVÉ**\n\nJe peux t'aider avec : Python, JavaScript, HTML, CSS, Java, etc.\n\nExemple : \"Crée une fonction Python pour trier une liste\"",
                   parse_mode='Markdown')

@bot.message_handler(commands=['creative'])
def creative_handler(message):
    """Mode création"""
    bot.send_message(message.chat.id,
                   "🎨 **MODE CRÉATION ACTIVÉ**\n\nJe peux : écrire, designer, inventer, créer du contenu...\n\nExemple : \"Écris une histoire courte sur l'IA\"",
                   parse_mode='Markdown')

@bot.message_handler(commands=['analyse', 'analyze'])
def analyse_handler(message):
    """Mode analyse"""
    bot.send_message(message.chat.id,
                   "📊 **MODE ANALYSE ACTIVÉ**\n\nJe peux analyser : situations, données, problèmes techniques...\n\nExemple : \"Analyse les avantages de l'IA\"",
                   parse_mode='Markdown')

@bot.message_handler(commands=['photo'])
def photo_handler(message):
    """Envoi de photo"""
    if IMAGE_GALLERY:
        try:
            bot.send_photo(message.chat.id, random.choice(IMAGE_GALLERY),
                         caption=f"📸 **Photo de {CREATOR}**\n💫 Partagée avec plaisir !")
        except:
            bot.send_message(message.chat.id, "❌ Erreur d'envoi de photo")
    else:
        bot.send_message(message.chat.id, "📸 Aucune photo disponible")

# ==================== MOTEUR IA CORRIGÉ ====================
@bot.message_handler(func=lambda message: True)
def smart_ai_handler(message):
    """Moteur IA corrigé et optimisé"""
    user_id = message.from_user.id
    user_context = get_user_context(user_id)
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # Détection du type de demande
        request_type = detect_request_type(message.text)
        
        # Construction des messages avec contexte limité
        messages = [{"role": "system", "content": create_smart_prompt()}]
        
        # Ajout du contexte récent (seulement 2 derniers messages)
        if user_context:
            messages.extend(user_context[-2:])
        
        # Ajout du message actuel
        messages.append({"role": "user", "content": message.text})

        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            # Sauvegarde du contexte
            user_context.append({"role": "user", "content": message.text})
            user_context.append({"role": "assistant", "content": answer})
            
            # Limite le contexte à 6 messages maximum
            if len(user_context) > 6:
                user_context = user_context[-6:]
                user_conversations[user_id] = user_context
            
            # Traitement des blocs de code
            code_blocks = re.findall(r'```(?:[\w]*)\n?(.*?)```', answer, re.DOTALL)
            
            if code_blocks:
                response_text = "💻 **CODE GÉNÉRÉ** 💻\n\n"
                for i, code in enumerate(code_blocks, 1):
                    # Détection du langage
                    lang = "python"
                    if any(keyword in message.text.lower() for keyword in ['html', 'web']):
                        lang = "html"
                    elif 'css' in message.text.lower():
                        lang = "css"
                    elif any(keyword in message.text.lower() for keyword in ['javascript', 'js']):
                        lang = "javascript"
                    elif 'java' in message.text.lower():
                        lang = "java"
                    
                    response_text += f"```{lang}\n{code.strip()}\n```\n\n"
                
                response_text += "📋 **Copie facile** | 👑 **Expert : {CREATOR}**"
                bot.reply_to(message, response_text, parse_mode='Markdown')
            else:
                # Réponse normale
                bot.reply_to(message, answer)
                
            # Envoi photo aléatoire (10% de chance)
            if IMAGE_GALLERY and random.random() < 0.1:
                try:
                    time.sleep(0.5)
                    bot.send_photo(message.chat.id, random.choice(IMAGE_GALLERY),
                                 caption="📸 Au fait, voici une de mes photos !")
                except:
                    pass
                
        else:
            # Gestion d'erreur améliorée
            error_info = f"""
❌ **Erreur technique**

Détails : Code {response.status_code}

💡 **Solutions :**
• Réessaie dans quelques secondes
• Utilise une question plus courte
• Vérifie ta connexion Internet

🔄 **Le système se rétablit automatiquement**

👑 **Support :** {CREATOR}
"""
            bot.reply_to(message, error_info, parse_mode='Markdown')
            
    except requests.exceptions.Timeout:
        bot.reply_to(message,
                    "⏰ **Trop long à répondre**\n\nRéessaie avec une question plus courte !\n\n💡 Conseil : Utilise des phrases simples",
                    parse_mode='Markdown')
        
    except Exception as e:
        error_msg = f"""
🔴 **Erreur inattendue**

Détails : {str(e)}

🚀 **Solution :**
• Réessaie dans 1 minute
• Redémarre la conversation
• Contacte {CREATOR} si ça persiste

💫 **Je reviens rapidement !**
"""
        bot.reply_to(message, error_msg, parse_mode='Markdown')

# ==================== NETTOYAGE AUTOMATIQUE ====================
def cleanup_old_conversations():
    """Nettoyage des conversations anciennes"""
    current_time = time.time()
    users_to_remove = []
    
    for user_id, context in user_conversations.items():
        # Supprime les conversations de plus de 2 heures
        if len(context) > 0 and current_time - context[0].get('timestamp', 0) > 7200:
            users_to_remove.append(user_id)
    
    for user_id in users_to_remove:
        del user_conversations[user_id]

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print(f"""
🚀 {BOT_NAME} - {VERSION}
👑 Créateur : {CREATOR}
⚡ Modèle : {current_model}
🎯 Statut : OPÉRATIONNEL

💫 Capacités :
✓ IA conversationnelle naturelle
✓ Génération de code
✓ Création de contenu
✓ Analyse intelligente
✓ Photos personnelles

💡 Le bot parle naturellement - plus besoin de commandes !
    """)
    
    # Nettoyage périodique
    import threading
    def schedule_cleanup():
        while True:
            time.sleep(1800)  # 30 minutes
            cleanup_old_conversations()
    
    cleanup_thread = threading.Thread(target=schedule_cleanup, daemon=True)
    cleanup_thread.start()
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Arrêt : {e}")
        print(f"👑 Contact : {CREATOR}")
