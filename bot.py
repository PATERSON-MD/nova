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

# 🔐 ADMIN
ADMIN_ID = 7908680781
ADMIN_PASSWORD = "KING1998"

# Stockage
user_sessions = {}
admin_sessions = {}

# ==================== BASE DE DONNÉES ====================
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
                  username TEXT,
                  first_name TEXT,
                  has_premium BOOLEAN DEFAULT FALSE,
                  premium_since TIMESTAMP,
                  added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
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

def activate_user_premium(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO user_access (user_id, has_premium, premium_since) VALUES (?, ?, ?)', 
              (user_id, True, datetime.now()))
    conn.commit()
    conn.close()

def deactivate_user_premium(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('UPDATE user_access SET has_premium = FALSE, premium_since = NULL WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium FROM user_access')
    users = c.fetchall()
    conn.close()
    return users

def get_premium_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name FROM user_access WHERE has_premium = TRUE')
    users = c.fetchall()
    conn.close()
    return users

def get_user_info(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium, premium_since FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_group_stats():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM groups')
    total = c.fetchone()[0]
    conn.close()
    return total

def add_group_to_db(group_id, group_name, member_count):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO groups 
                 (group_id, group_name, member_count, added_date)
                 VALUES (?, ?, ?, ?)''', 
                 (group_id, group_name, member_count, datetime.now()))
    conn.commit()
    conn.close()

def is_admin(user_id):
    return user_id == ADMIN_ID

def verify_admin_password(password):
    return password == ADMIN_PASSWORD

def is_admin_authenticated(user_id):
    if user_id not in admin_sessions:
        return False
    session = admin_sessions[user_id]
    if (datetime.now() - session['auth_time']).total_seconds() > 1800:
        del admin_sessions[user_id]
        return False
    return session['authenticated']

# ==================== FONCTIONS UTILISATEURS ====================
def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'conversation': [],
            'last_active': datetime.now()
        }
    return user_sessions[user_id]

def get_progress_bar():
    total = get_group_stats()
    filled = '█' * min(total, 5)
    empty = '░' * (5 - min(total, 5))
    return f"`[{filled}{empty}]` {total}/5"

def create_main_menu():
    keyboard = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    keyboard.add(support_button)
    return keyboard

def create_premium_menu():
    keyboard = InlineKeyboardMarkup()
    
    try:
        bot_user = bot.get_me()
        bot_username = bot_user.username
        add_button = InlineKeyboardButton(
            "📥 Ajouter à un groupe", 
            url=f"https://t.me/{bot_username}?startgroup=true" if bot_username else f"https://t.me/{bot_user.id}?startgroup=true"
        )
    except:
        add_button = InlineKeyboardButton("📥 Ajouter à un groupe", url="https://t.me/")
    
    status_button = InlineKeyboardButton("📊 Vérifier le statut", callback_data="check_status")
    premium_button = InlineKeyboardButton("🎁 Activer Premium", callback_data="activate_premium")
    
    keyboard.add(add_button)
    keyboard.add(status_button)
    keyboard.add(premium_button)
    
    return keyboard

def create_admin_menu():
    keyboard = InlineKeyboardMarkup()
    stats_btn = InlineKeyboardButton("📊 Statistiques", callback_data="admin_stats")
    users_btn = InlineKeyboardButton("👥 Utilisateurs", callback_data="admin_users")
    premium_btn = InlineKeyboardButton("⭐ Gérer Premium", callback_data="admin_premium")
    broadcast_btn = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    
    keyboard.add(stats_btn, users_btn)
    keyboard.add(premium_btn, broadcast_btn)
    
    return keyboard

def create_optimized_prompt():
    return f"""Tu es {BOT_NAME}, assistant IA créé par {CREATOR}. Expert en programmation, création, analyse et aide générale. Sois naturel, précis et utile. Réponds dans la langue de l'utilisateur."""

# ==================== HANDLERS UTILISATEURS ====================
@bot.message_handler(commands=['start', 'aide'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        
        # Enregistrer l'utilisateur
        conn = sqlite3.connect('bot_groups.db')
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO user_access 
                     (user_id, username, first_name, added_date) 
                     VALUES (?, ?, ?, ?)''', 
                     (user_id, username, first_name, datetime.now()))
        conn.commit()
        conn.close()
        
        # ✅ PROPRIÉTAIRE - Premium immédiat
        if is_admin(user_id):
            activate_user_premium(user_id)
            bot.send_message(
                message.chat.id,
                "👑 **Mode Propriétaire Activé**\n\n⭐ **Premium activé pour vous !**\n📢 Accès au panel administrateur.",
                reply_markup=create_admin_menu(),
                parse_mode='Markdown'
            )
            return
        
        try:
            bot.send_photo(
                message.chat.id, 
                MAIN_PHOTO,
                caption=f"📸 **{CREATOR}** - Créateur du bot\n*Votre expert en IA* 👑",
                parse_mode='Markdown'
            )
            time.sleep(0.5)
        except:
            pass
        
        if check_premium_access(user_id):
            menu = f"""
🎉 **{BOT_NAME}** - {VERSION} **PREMIUM**

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
            
            if total >= 5:
                menu = f"""
🎊 **{BOT_NAME}** - PRÊT POUR LE PREMIUM !

{get_progress_bar()}

✅ **Conditions remplies !** 
5/5 groupes atteints !

🎁 **Cliquez sur "Activer Premium" ci-dessous**
pour débloquer toutes les fonctionnalités !

🚀 **L'IA vous attend !**
"""
            else:
                menu = f"""
🔒 **{BOT_NAME}** - {VERSION} **LIMITÉE**

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
"""
            
            bot.send_message(message.chat.id, menu, parse_mode='Markdown', reply_markup=create_premium_menu())
            
    except Exception as e:
        print(f"❌ Erreur start: {e}")
        bot.reply_to(message, "❌ Erreur temporaire. Réessayez.")

@bot.message_handler(commands=['test'])
def test_command(message):
    bot.reply_to(message, "✅ **Bot actif !**")

@bot.message_handler(commands=['reset'])
def reset_handler(message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions[user_id]['conversation'] = []
    bot.reply_to(message, "🔄 **Conversation réinitialisée !**")

# ==================== GESTION GROUPES ====================
@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    try:
        if bot.get_me().id in [user.id for user in message.new_chat_members]:
            group_id = message.chat.id
            group_name = message.chat.title
            
            try:
                member_count = bot.get_chat_members_count(group_id)
            except:
                member_count = 0
            
            add_group_to_db(group_id, group_name, member_count)
            
            welcome_msg = f"""
🤖 **{BOT_NAME}** - Merci de m'avoir ajouté !

👑 Créé par {CREATOR}
🚀 Assistant IA optimisé

📊 **Ce groupe compte pour le déblocage du premium gratuit !**
"""
            bot.send_message(group_id, welcome_msg, parse_mode='Markdown')
            
    except Exception as e:
        print(f"❌ Erreur nouveau groupe: {e}")

# ==================== MOTEUR IA ====================
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    
    if not check_premium_access(user_id):
        total = get_group_stats()
        if total >= 5:
            bot.reply_to(message, 
                       "🎊 **PRÊT POUR LE PREMIUM !**\n\n✅ 5/5 groupes atteints !\n\n🎁 Cliquez sur 'Activer Premium' pour débloquer l'IA !",
                       reply_markup=create_premium_menu())
        else:
            bot.reply_to(message, 
                       f"🔒 **Version limitée**\n\n{get_progress_bar()}\n\nAjoutez le bot à {5-total} groupe(s) pour débloquer l'IA.",
                       reply_markup=create_premium_menu())
        return
    
    # ✅ UTILISATEUR PREMIUM
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        if not GROQ_API_KEY:
            bot.reply_to(message, "❌ Service IA temporairement indisponible.")
            return
            
        user_session = get_user_session(user_id)
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        messages = [{"role": "system", "content": create_optimized_prompt()}]
        if user_session['conversation']:
            messages.extend(user_session['conversation'][-2:])
        
        user_message = message.text[:400]
        messages.append({"role": "user", "content": user_message})

        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": 800,
            "temperature": 0.7
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            
            user_session['conversation'].extend([
                {"role": "user", "content": user_message[:200]},
                {"role": "assistant", "content": answer[:500]}
            ])
            
            if len(user_session['conversation']) > 6:
                user_session['conversation'] = user_session['conversation'][-6:]
            
            bot.reply_to(message, answer)
        else:
            bot.reply_to(message, "❌ Erreur de service. Réessayez.")
            
    except Exception as e:
        print(f"❌ Erreur IA: {e}")
        bot.reply_to(message, "⏰ Service temporairement indisponible.")

# ==================== COMMANDES ADMIN ====================
@bot.message_handler(commands=['admin'])
def admin_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Accès réservé au propriétaire.")
        return
    
    msg = bot.reply_to(message, "🔐 **Accès Administrateur**\n\nVeuillez entrer le mot de passe :")
    bot.register_next_step_handler(msg, process_admin_password)

def process_admin_password(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if verify_admin_password(message.text.strip()):
        admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
        bot.send_message(message.chat.id, "✅ **Authentification réussie !**", reply_markup=create_admin_menu())
    else:
        bot.reply_to(message, "❌ **Mot de passe incorrect.**")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise. Utilisez /admin d'abord.")
        return
    
    total_users = len(get_all_users())
    premium_users = len(get_premium_users())
    groups_count = get_group_stats()
    
    stats_text = f"""
📊 **STATISTIQUES DU BOT**

👥 **Utilisateurs :**
• Total : {total_users}
• Premium : {premium_users}
• Standard : {total_users - premium_users}
• Taux premium : {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%

📁 **Groupes :** {groups_count}/5
🕐 **Dernière MAJ :** {datetime.now().strftime('%H:%M %d/%m/%Y')}
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['users'])
def users_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    users = get_all_users()
    if not users:
        bot.reply_to(message, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **LISTE DES UTILISATEURS**\n\n"
    for i, user in enumerate(users[:30], 1):
        user_id, username, first_name, has_premium = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "Sans username"
        response += f"{i}. {premium_status} {first_name} ({username_display}) - ID: `{user_id}`\n"
    
    if len(users) > 30:
        response += f"\n... et {len(users) - 30} autres utilisateurs"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['premium_users'])
def premium_users_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    premium_users = get_premium_users()
    if not premium_users:
        bot.reply_to(message, "⭐ Aucun utilisateur premium.")
        return
    
    response = "⭐ **UTILISATEURS PREMIUM**\n\n"
    for i, user in enumerate(premium_users, 1):
        user_id, username, first_name = user
        username_display = f"@{username}" if username else "Sans username"
        response += f"{i}. {first_name} ({username_display}) - ID: `{user_id}`\n"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['give_premium'])
def give_premium_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    msg = bot.reply_to(message, "⭐ **DONNER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_give_premium)

def process_give_premium(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        return
    
    try:
        target_user_id = int(message.text.strip())
        activate_user_premium(target_user_id)
        
        try:
            bot.send_message(target_user_id, "🎉 **FÉLICITATIONS !**\n\n⭐ **Premium activé !**\n✨ Profitez de l'IA !")
        except:
            pass
        
        bot.reply_to(message, f"✅ **Premium accordé à l'utilisateur {target_user_id}**")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['remove_premium'])
def remove_premium_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    msg = bot.reply_to(message, "🔒 **RETIRER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_remove_premium)

def process_remove_premium(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        return
    
    try:
        target_user_id = int(message.text.strip())
        deactivate_user_premium(target_user_id)
        bot.reply_to(message, f"✅ **Premium retiré à l'utilisateur {target_user_id}**")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['user_info'])
def user_info_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    msg = bot.reply_to(message, "🔍 **INFORMATIONS UTILISATEUR**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_user_info)

def process_user_info(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        return
    
    try:
        target_user_id = int(message.text.strip())
        user_info = get_user_info(target_user_id)
        
        if user_info:
            user_id, username, first_name, has_premium, premium_since = user_info
            premium_status = "⭐ PREMIUM" if has_premium else "🔒 STANDARD"
            since = premium_since or "Non premium"
            username_display = f"@{username}" if username else "Aucun"
            
            response = f"""
👤 **INFORMATIONS UTILISATEUR**

🆔 ID: `{user_id}`
📛 Nom: {first_name}
👤 Username: {username_display}
🎯 Statut: {premium_status}
📅 Premium depuis: {since}
"""
            bot.reply_to(message, response, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Utilisateur non trouvé.")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    msg = bot.reply_to(message, "📢 **BROADCAST**\n\nEnvoyez le message à diffuser :")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        return
    
    broadcast_text = message.text
    users = get_all_users()
    total_users = len(users)
    
    progress_msg = bot.send_message(message.chat.id, f"📤 **Diffusion en cours...**\n0/{total_users} utilisateurs")
    
    success_count = 0
    fail_count = 0
    
    for i, user in enumerate(users):
        try:
            bot.send_message(user[0], f"📢 **Message de {CREATOR}**\n\n{broadcast_text}")
            success_count += 1
        except:
            fail_count += 1
        
        if i % 10 == 0:
            try:
                bot.edit_message_text(
                    f"📤 **Diffusion en cours...**\n{i+1}/{total_users} utilisateurs",
                    message.chat.id,
                    progress_msg.message_id
                )
            except:
                pass
        
        time.sleep(0.1)
    
    result_text = f"""
✅ **BROADCAST TERMINÉ**

📊 **Résultats :**
• ✅ Envoyés : {success_count}
• ❌ Échecs : {fail_count}
• 📝 Total : {total_users}
"""
    bot.send_message(message.chat.id, result_text, parse_mode='Markdown')

@bot.message_handler(commands=['premium_all'])
def premium_all_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    users = get_all_users()
    for user in users:
        activate_user_premium(user[0])
    
    bot.reply_to(message, f"⭐ **Premium activé pour tous les {len(users)} utilisateurs !**")

@bot.message_handler(commands=['remove_all_premium'])
def remove_all_premium_command(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    users = get_all_users()
    for user in users:
        if user[0] != ADMIN_ID:
            deactivate_user_premium(user[0])
    
    bot.reply_to(message, f"🔒 **Premium retiré à tous les utilisateurs sauf vous !**")

# ==================== CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if call.data == "check_status":
        total = get_group_stats()
        if check_premium_access(user_id):
            bot.answer_callback_query(call.id, "✅ Premium activé !")
        else:
            bot.answer_callback_query(call.id, f"📊 {total}/5 groupes")
    
    elif call.data == "activate_premium":
        total = get_group_stats()
        if total >= 5:
            if activate_user_premium(user_id):
                bot.answer_callback_query(call.id, "🎉 Premium activé !")
                bot.send_message(call.message.chat.id, "🎉 **Premium activé avec succès !**\n\n✨ **Profitez de toutes les fonctionnalités IA !**")
            else:
                bot.answer_callback_query(call.id, "❌ Erreur activation")
        else:
            bot.answer_callback_query(call.id, f"❌ {5-total} groupe(s) manquant(s)")
    
    elif call.data == "admin_stats":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        total_users = len(get_all_users())
        premium_users = len(get_premium_users())
        groups_count = get_group_stats()
        
        stats_text = f"📊 **STATISTIQUES**\n\n👥 Utilisateurs: {total_users}\n⭐ Premium: {premium_users}\n📁 Groupes: {groups_count}/5"
        bot.answer_callback_query(call.id, "📊 Statistiques")
        bot.send_message(call.message.chat.id, stats_text, parse_mode='Markdown')
    
    elif call.data == "admin_users":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        users = get_all_users()
        response = "👥 **UTILISATEURS**\n\n"
        for i, user in enumerate(users[:10], 1):
            user_id, username, first_name, has_premium = user
            status = "⭐" if has_premium else "🔒"
            response += f"{i}. {status} {first_name} - ID: `{user_id}`\n"
        
        bot.answer_callback_query(call.id, "👥 Utilisateurs")
        bot.send_message(call.message.chat.id, response, parse_mode='Markdown')
    
    elif call.data == "admin_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        keyboard = InlineKeyboardMarkup()
        give_btn = InlineKeyboardButton("➕ Donner Premium", callback_data="admin_give_premium_menu")
        remove_btn = InlineKeyboardButton("➖ Retirer Premium", callback_data="admin_remove_premium_menu")
        all_btn = InlineKeyboardButton("⭐ À Tous", callback_data="admin_premium_all_menu")
        
        keyboard.add(give_btn, remove_btn)
        keyboard.add(all_btn)
        
        bot.answer_callback_query(call.id, "⭐ Gestion Premium")
        bot.send_message(call.message.chat.id, "⭐ **GESTION PREMIUM**", reply_markup=keyboard)
    
    elif call.data == "admin_broadcast":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        msg = bot.send_message(call.message.chat.id, "📢 **BROADCAST**\n\nEnvoyez le message :")
        bot.register_next_step_handler(msg, process_broadcast)
        bot.answer_callback_query(call.id, "📢 Broadcast")
    
    elif call.data == "admin_give_premium_menu":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        msg = bot.send_message(call.message.chat.id, "⭐ **DONNER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
        bot.register_next_step_handler(msg, process_give_premium)
        bot.answer_callback_query(call.id, "➕ Donner Premium")
    
    elif call.data == "admin_remove_premium_menu":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        msg = bot.send_message(call.message.chat.id, "🔒 **RETIRER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
        bot.register_next_step_handler(msg, process_remove_premium)
        bot.answer_callback_query(call.id, "➖ Retirer Premium")
    
    elif call.data == "admin_premium_all_menu":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        users = get_all_users()
        for user in users:
            activate_user_premium(user[0])
        
        bot.answer_callback_query(call.id, "✅ Premium à tous")
        bot.send_message(call.message.chat.id, f"⭐ **Premium activé pour tous les {len(users)} utilisateurs !**")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    init_db()
    print("🚀 Bot démarré avec succès!")
    print("👑 Commandes admin disponibles")
    print("🤖 En attente de messages...")
    bot.infinity_polling()
