#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import random
import re
import time
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

# ==================== CONFIGURATION ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ
CREATOR = "👑 Soszoe"
BOT_NAME = "🚀 KervensAI Pro"
VERSION = "💎 Édition Groq Optimisée"
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
current_model = "llama-3.1-8b-instant"

# Stockage conversations
user_sessions = {}

# ==================== SYSTÈME PREMIUM ====================
def init_db():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS groups
                 (group_id INTEGER PRIMARY KEY, 
                  group_name TEXT,
                  member_count INTEGER,
                  added_date TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS user_access
                 (user_id INTEGER PRIMARY KEY,
                  has_premium BOOLEAN DEFAULT FALSE)''')
    conn.commit()
    conn.close()

def check_group_requirements():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM groups')
    total_groups = c.fetchone()[0]
    conn.close()
    return total_groups >= 5

def check_premium_access(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT has_premium FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0]

def get_group_stats():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM groups')
    total = c.fetchone()[0]
    conn.close()
    return total

def get_progress_bar():
    total = get_group_stats()
    filled = '█' * min(total, 5)
    empty = '░' * (5 - min(total, 5))
    return f"`[{filled}{empty}]` {total}/5"

def activate_premium_for_all():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('UPDATE user_access SET has_premium = TRUE')
    conn.commit()
    conn.close()

def add_group_to_db(group_id, group_name, member_count):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO groups 
                 (group_id, group_name, member_count, added_date)
                 VALUES (?, ?, ?, ?)''', 
                 (group_id, group_name, member_count, datetime.now()))
    conn.commit()
    conn.close()

# ==================== FONCTIONS ====================
def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversation': [],
            'last_active': datetime.now()
        }
    return user_sessions[user_id]

def create_main_menu():
    keyboard = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    keyboard.add(support_button)
    return keyboard

def create_premium_menu():
    keyboard = InlineKeyboardMarkup()
    
    # Récupération dynamique du username du bot
    try:
        bot_user = bot.get_me()
        bot_username = bot_user.username
        
        if bot_username:
            add_button = InlineKeyboardButton(
                "📥 Ajouter à un groupe", 
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        else:
            # Si pas de username, utiliser l'ID
            add_button = InlineKeyboardButton(
                "📥 Ajouter à un groupe", 
                url=f"https://t.me/{bot_user.id}?startgroup=true"
            )
    except Exception as e:
        print(f"Erreur username: {e}")
        return keyboard
    
    status_button = InlineKeyboardButton("📊 Vérifier le statut", callback_data="check_status")
    keyboard.add(add_button)
    keyboard.add(status_button)
    return keyboard

def create_optimized_prompt():
    return f"""Tu es {BOT_NAME}, assistant IA créé par {CREATOR}. Expert en programmation, création, analyse et aide générale. Sois naturel, précis et utile. Réponds dans la langue de l'utilisateur."""

# ==================== COMMANDES ====================
@bot.message_handler(commands=['start', 'aide'])
def start_handler(message):
    user_id = message.from_user.id
    
    # Enregistrer l'utilisateur
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('INSERT OR IGNORE INTO user_access (user_id) VALUES (?)', (user_id,))
    conn.commit()
    conn.close()
    
    try:
        bot.send_photo(
            message.chat.id, 
            MAIN_PHOTO,
            caption=f"📸 **{CREATOR}** - Créateur du bot\n*Votre expert en IA* 👑",
            parse_mode='Markdown'
        )
        time.sleep(0.5)
    except Exception as e:
        print(f"Photo non chargée: {e}")
    
    if check_premium_access(user_id):
        menu = f"""
🎉 **{BOT_NAME}** - {VERSION} **PREMIUM**

👑 **Créé par {CREATOR}**
⭐ **Version Premium Activée !**

💫 **Fonctionnalités débloquées :**
• 💻 Programmation & Code
• 🎨 Création & Rédaction  
• 📊 Analyse & Conseil
• 🌍 Traduction
• 💬 Conversation naturelle

✨ **Envoyez-moi un message pour commencer !**
"""
        bot.send_message(message.chat.id, menu, parse_mode='Markdown', reply_markup=create_main_menu())
    else:
        total = get_group_stats()
        menu = f"""
🔒 **{BOT_NAME}** - {VERSION} **LIMITÉE**

👑 **Créé par {CREATOR}**

🚀 **Assistant IA optimisé pour Groq**
*Version limitée - Débloquez le premium gratuitement !*

{get_progress_bar()}

🎁 **Conditions pour le Premium GRATUIT :**
• ➕ Bot dans 5 groupes
• ✅ Déblocage immédiat après validation

📊 **Statut actuel :**
• Groupes : {total}/5

💡 **Comment débloquer :**
1. Cliquez sur "Ajouter à un groupe" ci-dessous
2. Choisissez n'importe quel groupe
3. Le premium se débloque à 5 groupes

👑 **La communauté grandit ensemble !**
"""
        bot.send_message(message.chat.id, menu, parse_mode='Markdown', reply_markup=create_premium_menu())

@bot.message_handler(commands=['status', 'premium'])
def status_command(message):
    user_id = message.from_user.id
    if check_premium_access(user_id):
        bot.reply_to(message, "✅ **Vous avez la version PREMIUM !** Profitez-en ! 🚀")
    else:
        total = get_group_stats()
        status_msg = f"""
🔒 **STATUT PREMIUM**

{get_progress_bar()}

📊 **Progression :**
• Groupes : {total}/5

🎁 **Il reste {5-total} groupes à ajouter pour débloquer le premium !**

👇 **Ajoutez le bot à des groupes pour accélérer le processus :**
"""
        bot.reply_to(message, status_msg, parse_mode='Markdown', reply_markup=create_premium_menu())

@bot.message_handler(commands=['photo'])
def photo_handler(message):
    try:
        bot.send_photo(
            message.chat.id, 
            MAIN_PHOTO,
            caption=f"📸 **{CREATOR}** - Créateur du bot\n*Merci pour votre support !* 💝",
            parse_mode='Markdown',
            reply_markup=create_main_menu()
        )
    except:
        bot.send_message(message.chat.id, "❌ Erreur photo")

@bot.message_handler(commands=['support'])
def support_handler(message):
    support_text = f"""
💝 **Support {CREATOR}**

Merci de soutenir mon travail ! 
Votre support m'aide à améliorer ce bot.

👇 **Cliquez ci-dessous pour me contacter :**
"""
    bot.send_message(message.chat.id, support_text, parse_mode='Markdown', reply_markup=create_main_menu())

@bot.message_handler(commands=['reset'])
def reset_handler(message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions[user_id]['conversation'] = []
    bot.send_message(message.chat.id, "🔄 **Conversation réinitialisée !**")

# ==================== DÉTECTION GROUPES ====================
@bot.message_handler(content_types=['new_chat_members', 'new_chat_participant'])
def new_member_handler(message):
    try:
        new_members = getattr(message, 'new_chat_members', [])
        if not new_members:
            new_members = [getattr(message, 'new_chat_participant', None)]
            new_members = [m for m in new_members if m is not None]
        
        bot_id = bot.get_me().id
        
        for member in new_members:
            if member.id == bot_id:
                group_id = message.chat.id
                group_name = message.chat.title
                
                try:
                    member_count = bot.get_chat_members_count(group_id)
                except:
                    member_count = 0
                
                # Vérifier si nouveau groupe
                conn = sqlite3.connect('bot_groups.db')
                c = conn.cursor()
                c.execute('SELECT * FROM groups WHERE group_id = ?', (group_id,))
                existing_group = c.fetchone()
                conn.close()
                
                if not existing_group:
                    add_group_to_db(group_id, group_name, member_count)
                    
                    welcome_msg = f"""
🤖 **{BOT_NAME}** - Merci de m'avoir ajouté !

👑 Créé par {CREATOR}
🚀 Assistant IA optimisé

📊 **Ce groupe compte pour le déblocage du premium gratuit !**
"""
                    try:
                        bot.send_message(group_id, welcome_msg, parse_mode='Markdown')
                    except:
                        pass
                
                # Vérifier déblocage premium
                if check_group_requirements():
                    activate_premium_for_all()
                    announcement = """
🎉 **FÉLICITATIONS ! PREMIUM DÉBLOQUÉ !**

✅ 5 groupes atteints !
🚀 **Version Premium activée pour tous !**

✨ **Toutes les fonctionnalités disponibles !**
"""
                    try:
                        bot.send_message(group_id, announcement, parse_mode='Markdown')
                    except:
                        pass
                
                break
                
    except Exception as e:
        print(f"Erreur nouveau groupe: {e}")

# ==================== MOTEUR IA ====================
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    # Ignorer les messages de groupe
    if message.chat.type in ['group', 'supergroup']:
        return
    
    user_id = message.from_user.id
    
    # Vérifier premium
    if not check_premium_access(user_id):
        total = get_group_stats()
        restriction_msg = f"""
🔒 **ACCÈS BLOQUÉ - VERSION LIMITÉE**

🚫 **Le bot ne répond pas** sans premium.

{get_progress_bar()}

📊 **Progression :** {total}/5 groupes

🎁 **Ajoutez le bot à {5-total} groupe(s) pour débloquer !**
"""
        bot.reply_to(message, restriction_msg, parse_mode='Markdown', reply_markup=create_premium_menu())
        return
    
    # ✅ UTILISATEUR PREMIUM
    user_session = get_user_session(user_id)
    user_session['last_active'] = datetime.now()
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = [{"role": "system", "content": create_optimized_prompt()}]
        
        if user_session['conversation']:
            messages.extend(user_session['conversation'][-2:])
        
        user_message = message.text[:400]
        messages.append({"role": "user", "content": user_message})

        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": 800,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
            
            # Sauvegarde conversation
            user_session['conversation'].extend([
                {"role": "user", "content": user_message[:200]},
                {"role": "assistant", "content": answer[:500]}
            ])
            
            if len(user_session['conversation']) > 6:
                user_session['conversation'] = user_session['conversation'][-6:]
            
            # Détection code
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
                bot.reply_to(message, answer)
                
        else:
            if response.status_code == 400:
                bot.reply_to(message, "🔄 **Message trop long** - Réessaie plus court !")
            elif response.status_code == 429:
                bot.reply_to(message, "⏱️ **Trop de requêtes** - Attends 1 minute !")
            else:
                bot.reply_to(message, "❌ **Erreur** - Réessaie !")
            
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ **Timeout** - Question plus courte ?")
    except Exception as e:
        bot.reply_to(message, "🔧 **Erreur technique** - Réessaie !")

# ==================== CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "check_status":
        user_id = call.from_user.id
        if check_premium_access(user_id):
            bot.answer_callback_query(call.id, "✅ Vous avez la version PREMIUM !")
        else:
            total = get_group_stats()
            bot.answer_callback_query(call.id, f"📊 Progression: {total}/5 groupes")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    init_db()
    
    print(f"""
🎯 {BOT_NAME} - {VERSION}
👑 Créateur : {CREATOR}
🔒 Système Premium : 5 groupes requis
⚡ Modèle : {current_model}
🚀 Prêt à fonctionner !
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Arrêt : {e}")
