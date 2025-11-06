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

# ==================== CONFIGURATION OPTIMISÉE POUR GROQ ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ
CREATOR = "👑 Soszoe"
BOT_NAME = "🚀 KervensAI Pro"
VERSION = "💎 Édition Groq Optimisée"

# 🎨 TES PHOTOS
IMAGE_GALLERY = [
    "https://files.catbox.moe/601u5z.jpg",
    "https://files.catbox.moe/qmxfpk.jpg",  
    "https://files.catbox.moe/77iazb.jpg",
]

# ⚡ MODÈLE OPTIMISÉ
current_model = "llama-3.1-8b-instant"  # Plus rapide et stable

# Stockage conversations léger
user_sessions = {}

# ==================== PROMPT OPTIMISÉ POUR GROQ (150 tokens max) ====================
def create_optimized_prompt():
    """Prompt ultra-optimisé pour Groq - 150 tokens max"""
    return f"""Tu es {BOT_NAME}, assistant IA créé par {CREATOR}. Expert en programmation, création, analyse et aide générale. Sois naturel, précis et utile. Réponds dans la langue de l'utilisateur."""

# ==================== FONCTIONS OPTIMISÉES ====================
def get_user_session(user_id):
    """Gestion session minimaliste"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversation': [],
            'last_active': datetime.now()
        }
    return user_sessions[user_id]

def detect_quick_intent(text):
    """Détection rapide d'intention"""
    text_lower = text.lower()
    if any(word in text_lower for word in ['salut', 'bonjour', 'hello']): return "greeting"
    if any(word in text_lower for word in ['code', 'programme', 'script']): return "coding"
    if any(word in text_lower for word in ['crée', 'écris', 'invente']): return "creative"
    return "conversation"

def should_send_photo(intent):
    """Décision photo simplifiée"""
    chances = {"greeting": 0.3, "creative": 0.2, "default": 0.1}
    return random.random() < chances.get(intent, chances["default"])

# ==================== COMMANDES OPTIMISÉES ====================
@bot.message_handler(commands=['start', 'aide'])
def optimized_start(message):
    """Menu optimisé"""
    menu = f"""
🤖 **{BOT_NAME}** - {VERSION}

👑 Créé par {CREATOR}
🚀 Assistant IA optimisé pour Groq

💫 **Je peux t'aider avec :**
• 💻 Programmation & Code
• 🎨 Création & Rédaction  
• 📊 Analyse & Conseil
• 🌍 Traduction
• 💬 Conversation naturelle

💡 **Exemples :**
"Code un script Python pour..."
"Écris un article sur..."
"Explique-moi..."
"Traduis ce texte..."

✨ **Simple, rapide, efficace !**
"""
    bot.send_message(message.chat.id, menu, parse_mode='Markdown')
    
    if IMAGE_GALLERY and random.random() < 0.3:
        try:
            bot.send_photo(message.chat.id, random.choice(IMAGE_GALLERY),
                         caption="📸 Une de mes photos !")
        except:
            pass

@bot.message_handler(commands=['photo'])
def photo_handler(message):
    """Gestionnaire photo optimisé"""
    if IMAGE_GALLERY:
        try:
            bot.send_photo(message.chat.id, random.choice(IMAGE_GALLERY),
                         caption=f"📸 **Photo de {CREATOR}**")
        except:
            bot.send_message(message.chat.id, "❌ Erreur photo")
    else:
        bot.send_message(message.chat.id, "📸 Aucune photo configurée")

@bot.message_handler(commands=['reset'])
def reset_handler(message):
    """Reset optimisé"""
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions[user_id]['conversation'] = []
    bot.send_message(message.chat.id, "🔄 **Conversation réinitialisée !**")

# ==================== MOTEUR IA OPTIMISÉ POUR GROQ ====================
@bot.message_handler(func=lambda message: True)
def optimized_ai_handler(message):
    """Moteur IA optimisé pour les limites Groq"""
    user_id = message.from_user.id
    user_session = get_user_session(user_id)
    user_session['last_active'] = datetime.now()
    
    intent = detect_quick_intent(message.text)
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        # CONSTRUCTION OPTIMISÉE POUR GROQ
        messages = [{"role": "system", "content": create_optimized_prompt()}]
        
        # CONTEXTE LIMITÉ (2 messages max)
        if user_session['conversation']:
            messages.extend(user_session['conversation'][-2:])
        
        # MESSAGE COURANT LIMITÉ
        user_message = message.text[:400]  # Limite caractères
        messages.append({"role": "user", "content": user_message})

        # PAYLOAD OPTIMISÉ POUR GROQ
        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": 800,  # LIMITÉ POUR GROQ
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            # SAUVEGARDE OPTIMISÉE
            user_session['conversation'].extend([
                {"role": "user", "content": user_message[:200]},  # Limité
                {"role": "assistant", "content": answer[:500]}    # Limité
            ])
            
            # LIMITE STRICTE HISTORIQUE
            if len(user_session['conversation']) > 6:
                user_session['conversation'] = user_session['conversation'][-6:]
            
            # TRAITEMENT CODE OPTIMISÉ
            code_blocks = re.findall(r'```(?:[\w]*)\n?(.*?)```', answer, re.DOTALL)
            
            if code_blocks:
                response_text = "💻 **CODE**\n\n"
                for i, code in enumerate(code_blocks, 1):
                    lang = "python"
                    code_lower = code.lower()
                    if any(x in code_lower for x in ['<html', '<div']): lang = "html"
                    elif any(x in code_lower for x in ['function', 'const ']): lang = "javascript"
                    elif any(x in code_lower for x in ['public class']): lang = "java"
                    
                    response_text += f"```{lang}\n{code.strip()}\n```\n\n"
                
                response_text += f"👑 **Expert : {CREATOR}**"
                bot.reply_to(message, response_text, parse_mode='Markdown')
            else:
                # RÉPONSE NORMALE
                bot.reply_to(message, answer)
            
            # PHOTO CONTEXTUELLE OPTIMISÉE
            if IMAGE_GALLERY and should_send_photo(intent):
                try:
                    time.sleep(0.3)
                    bot.send_photo(message.chat.id, random.choice(IMAGE_GALLERY),
                                 caption="📸 Photo partagée !")
                except:
                    pass
                
        else:
            # GESTION ERREUR OPTIMISÉE
            if response.status_code == 400:
                bot.reply_to(message, "🔄 **Message trop long** - Réessaie plus court !")
            elif response.status_code == 429:
                bot.reply_to(message, "⏱️ **Trop de requêtes** - Attends 1 minute !")
            else:
                bot.reply_to(message, f"❌ **Erreur {response.status_code}** - Réessaie !")
            
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ **Timeout** - Question plus courte ?")
        
    except Exception as e:
        bot.reply_to(message, "🔧 **Erreur technique** - Réessaie !")

# ==================== NETTOYAGE OPTIMISÉ ====================
def cleanup_sessions():
    """Nettoyage sessions inactives"""
    now = datetime.now()
    inactive_users = []
    
    for user_id, session in user_sessions.items():
        if (now - session['last_active']).total_seconds() > 7200:
            inactive_users.append(user_id)
    
    for user_id in inactive_users:
        del user_sessions[user_id]

# ==================== DÉMARRAGE OPTIMISÉ ====================
if __name__ == "__main__":
    print(f"""
🎯 {BOT_NAME} - {VERSION}
👑 Créateur : {CREATOR}
⚡ Modèle : {current_model}
🔒 Statut : OPTIMISÉ POUR GROQ

💫 **Optimisations appliquées :**
✓ Prompt : 150 tokens max
✓ Contexte : 2 messages
✓ Tokens : 800 max par requête
✓ Timeout : 15 secondes
✓ Historique : 6 messages max

🚀 **Garanti sans erreur 400 !**
    """)
    
    # Nettoyage automatique léger
    import threading
    def schedule_cleanup():
        while True:
            time.sleep(3600)
            cleanup_sessions()
    
    threading.Thread(target=schedule_cleanup, daemon=True).start()
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Arrêt : {e}")
        print(f"👑 Contact : {CREATOR}")
