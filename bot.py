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

# ==================== CONFIGURATION SÉCURISÉE ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ
CREATOR = "👑 Soszoe"
BOT_NAME = "🚀 KervensAI Pro"
VERSION = "💎 Édition Groq Optimisée"
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
current_model = "llama-3.1-8b-instant"

# 🔐 ACCÈS ADMIN SÉCURISÉ
ADMIN_ID = 7908680781  # Votre ID Telegram
ADMIN_PASSWORD = "KING1998"  # Mot de passe admin

# Stockage conversations
user_sessions = {}
admin_sessions = {}

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
                  username TEXT,
                  first_name TEXT,
                  has_premium BOOLEAN DEFAULT FALSE,
                  premium_since TIMESTAMP,
                  added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS broadcast_messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  message_text TEXT,
                  sent_date TIMESTAMP,
                  sent_by INTEGER)''')
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
    """Active le premium pour un utilisateur spécifique"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO user_access (user_id, has_premium, premium_since) VALUES (?, ?, ?)', 
              (user_id, True, datetime.now()))
    conn.commit()
    conn.close()

def deactivate_user_premium(user_id):
    """Désactive le premium pour un utilisateur spécifique"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('UPDATE user_access SET has_premium = FALSE, premium_since = NULL WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_user_info(user_id):
    """Récupère les infos d'un utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium, premium_since FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'user_id': result[0],
            'username': result[1],
            'first_name': result[2],
            'has_premium': result[3],
            'premium_since': result[4]
        }
    return None

def get_all_users():
    """Récupère tous les utilisateurs"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium, premium_since FROM user_access ORDER BY added_date DESC')
    users = c.fetchall()
    conn.close()
    return users

def get_premium_users():
    """Récupère seulement les utilisateurs premium"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, premium_since FROM user_access WHERE has_premium = TRUE ORDER BY premium_since DESC')
    users = c.fetchall()
    conn.close()
    return users

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

def add_group_to_db(group_id, group_name, member_count):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO groups 
                 (group_id, group_name, member_count, added_date)
                 VALUES (?, ?, ?, ?)''', 
                 (group_id, group_name, member_count, datetime.now()))
    conn.commit()
    conn.close()

def save_broadcast_message(message_text, sent_by):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('INSERT INTO broadcast_messages (message_text, sent_date, sent_by) VALUES (?, ?, ?)',
              (message_text, datetime.now(), sent_by))
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
    
    try:
        bot_user = bot.get_me()
        bot_username = bot_user.username
        if bot_username:
            add_button = InlineKeyboardButton(
                "📥 Ajouter à un groupe", 
                url=f"https://t.me/{bot_username}?startgroup=true"
            )
        else:
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
    
    premium_button = InlineKeyboardButton("🎁 Activer Premium", callback_data="activate_premium")
    keyboard.add(premium_button)
    
    return keyboard

def create_premium_unlocked_menu():
    keyboard = InlineKeyboardMarkup()
    premium_btn = InlineKeyboardButton("⭐ Premium Activé", callback_data="premium_active")
    support_btn = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    keyboard.add(premium_btn)
    keyboard.add(support_btn)
    return keyboard

def create_admin_menu():
    """Menu administrateur complet"""
    keyboard = InlineKeyboardMarkup()
    
    broadcast_btn = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    stats_btn = InlineKeyboardButton("📊 Statistiques", callback_data="admin_stats")
    keyboard.add(broadcast_btn, stats_btn)
    
    users_btn = InlineKeyboardButton("👥 Gérer Utilisateurs", callback_data="admin_users")
    premium_btn = InlineKeyboardButton("⭐ Gérer Premium", callback_data="admin_premium")
    keyboard.add(users_btn, premium_btn)
    
    return keyboard

def create_users_management_menu():
    """Menu de gestion des utilisateurs"""
    keyboard = InlineKeyboardMarkup()
    
    list_users_btn = InlineKeyboardButton("📋 Liste Utilisateurs", callback_data="admin_list_users")
    list_premium_btn = InlineKeyboardButton("⭐ Liste Premium", callback_data="admin_list_premium")
    keyboard.add(list_users_btn, list_premium_btn)
    
    search_user_btn = InlineKeyboardButton("🔍 Rechercher Utilisateur", callback_data="admin_search_user")
    keyboard.add(search_user_btn)
    
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    keyboard.add(back_btn)
    
    return keyboard

def create_premium_management_menu():
    """Menu de gestion du premium"""
    keyboard = InlineKeyboardMarkup()
    
    give_premium_btn = InlineKeyboardButton("➕ Donner Premium", callback_data="admin_give_premium")
    remove_premium_btn = InlineKeyboardButton("➖ Retirer Premium", callback_data="admin_remove_premium")
    keyboard.add(give_premium_btn, remove_premium_btn)
    
    activate_all_btn = InlineKeyboardButton("⭐ Premium à Tous", callback_data="admin_premium_all")
    deactivate_all_btn = InlineKeyboardButton("🔒 Retirer à Tous", callback_data="admin_remove_all_premium")
    keyboard.add(activate_all_btn, deactivate_all_btn)
    
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    keyboard.add(back_btn)
    
    return keyboard

def create_optimized_prompt():
    return f"""Tu es {BOT_NAME}, assistant IA créé par {CREATOR}. Expert en programmation, création, analyse et aide générale. Sois naturel, précis et utile. Réponds dans la langue de l'utilisateur."""

# ==================== COMMANDES PRINCIPALES ====================
@bot.message_handler(commands=['start', 'aide'])
def start_handler(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Enregistrer/mettre à jour l'utilisateur
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, username, first_name, added_date) 
                 VALUES (?, ?, ?, ?)''', 
                 (user_id, username, first_name, datetime.now()))
    conn.commit()
    conn.close()
    
    # ✅ PROPRIÉTAIRE - Premium immédiat + Panel Admin
    if is_admin(user_id):
        activate_user_premium(user_id)
        bot.send_message(
            message.chat.id,
            "👑 **Mode Propriétaire Activé**\n\n⭐ **Premium activé pour vous !**\n📢 Accès au panel administrateur complet.",
            reply_markup=create_admin_menu(),
            parse_mode='Markdown'
        )
    
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
        owner_status = " 👑 **Propriétaire**" if is_admin(user_id) else ""
        menu = f"""
🎉 **{BOT_NAME}** - {VERSION} **PREMIUM**{owner_status}

⭐ **Version Premium Activée !**

💫 **Fonctionnalités débloquées :**
• 💻 Programmation & Code
• 🎨 Création & Rédaction  
• 📊 Analyse & Conseil
• 🌍 Traduction
• 💬 Conversation naturelle

✨ **Envoyez-moi un message pour commencer !**
"""
        reply_markup = create_admin_menu() if is_admin(user_id) else create_premium_unlocked_menu()
        bot.send_message(message.chat.id, menu, parse_mode='Markdown', reply_markup=reply_markup)
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

# ==================== COMMANDES ADMIN ====================
@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Commande admin sécurisée"""
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Accès réservé au propriétaire du bot.")
        return
    
    msg = bot.reply_to(message, "🔐 **Accès Administrateur**\n\nVeuillez entrer le mot de passe :")
    bot.register_next_step_handler(msg, process_admin_password)

def process_admin_password(message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if verify_admin_password(message.text.strip()):
        admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
        
        total_users = len(get_all_users())
        premium_users = len(get_premium_users())
        groups_count = get_group_stats()
        
        stats_text = f"""
👑 **PANEL ADMINISTRATEUR - ACCÈS AUTORISÉ**

📊 **Statistiques Complètes :**
• 👥 Utilisateurs totaux : {total_users}
• ⭐ Utilisateurs premium : {premium_users}
• 📁 Groupes : {groups_count}/5
• 📈 Taux premium : {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%

🛠 **Outils de Gestion :**
• 📢 Broadcast messages
• 👥 Gestion utilisateurs
• ⭐ Contrôle premium
• 📊 Statistiques détaillées

👇 **Utilisez les boutons ci-dessous :**
"""
        bot.send_message(message.chat.id, stats_text, parse_mode='Markdown', reply_markup=create_admin_menu())
    else:
        bot.reply_to(message, "❌ **Mot de passe incorrect.** Accès refusé.")

@bot.message_handler(commands=['users'])
def users_command(message):
    """Commande pour lister les utilisateurs"""
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise. Utilisez /admin d'abord.")
        return
    
    users = get_all_users()
    if not users:
        bot.reply_to(message, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **LISTE DES UTILISATEURS**\n\n"
    for i, user in enumerate(users[:50], 1):  # Limite à 50 users
        user_id, username, first_name, has_premium, premium_since = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "Sans username"
        response += f"{i}. {premium_status} {first_name} ({username_display})\n"
    
    if len(users) > 50:
        response += f"\n... et {len(users) - 50} autres utilisateurs"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['premium_users'])
def premium_users_command(message):
    """Commande pour lister les utilisateurs premium"""
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
        user_id, username, first_name, premium_since = user
        username_display = f"@{username}" if username else "Sans username"
        since = premium_since.split()[0] if premium_since else "Date inconnue"
        response += f"{i}. {first_name} ({username_display}) - Depuis: {since}\n"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['give_premium'])
def give_premium_command(message):
    """Donner le premium à un utilisateur"""
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
        
        # Essayer de notifier l'utilisateur
        try:
            bot.send_message(target_user_id, 
                           "🎉 **FÉLICITATIONS !**\n\n⭐ **Le propriétaire vous a accordé l'accès PREMIUM !**\n\n✨ Profitez de toutes les fonctionnalités IA !")
        except:
            pass
        
        bot.reply_to(message, f"✅ **Premium accordé à l'utilisateur {target_user_id}**")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['remove_premium'])
def remove_premium_command(message):
    """Retirer le premium à un utilisateur"""
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
        
        # Ne pas notifier l'utilisateur (discrétion)
        bot.reply_to(message, f"✅ **Premium retiré à l'utilisateur {target_user_id}**")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['user_info'])
def user_info_command(message):
    """Informations sur un utilisateur"""
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
            premium_status = "⭐ PREMIUM" if user_info['has_premium'] else "🔒 STANDARD"
            since = user_info['premium_since'] or "Non premium"
            username = f"@{user_info['username']}" if user_info['username'] else "Aucun"
            
            response = f"""
👤 **INFORMATIONS UTILISATEUR**

🆔 ID: `{user_info['user_id']}`
📛 Nom: {user_info['first_name']}
👤 Username: {username}
🎯 Statut: {premium_status}
📅 Premium depuis: {since}
"""
            bot.reply_to(message, response, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Utilisateur non trouvé.")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

# ==================== CALLBACKS ADMIN COMPLETS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    # Callbacks utilisateur normaux
    if call.data == "check_status":
        total = get_group_stats()
        if check_premium_access(user_id):
            bot.answer_callback_query(call.id, "✅ Premium activé !")
        else:
            bot.answer_callback_query(call.id, f"📊 {total}/5 groupes - {'Prêt pour premium!' if total >= 5 else 'En progression...'}")
    
    elif call.data == "activate_premium":
        total = get_group_stats()
        if check_premium_access(user_id):
            bot.answer_callback_query(call.id, "✅ Premium déjà activé !")
        elif total >= 5:
            activate_user_premium(user_id)  # ✅ Premium SEULEMENT pour cet utilisateur
            bot.answer_callback_query(call.id, "🎉 Premium activé !")
            bot.send_message(call.message.chat.id, "🎉 **Premium activé avec succès !**\n\n✨ **Profitez de toutes les fonctionnalités IA !**", parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id, f"❌ {5-total} groupe(s) manquant(s)")
    
    # Callbacks Admin
    elif call.data.startswith("admin_"):
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Accès réservé")
            return
        
        if not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            msg = bot.send_message(call.message.chat.id, "🔐 **Authentification requise.**\n\nVeuillez entrer le mot de passe admin :")
            bot.register_next_step_handler(msg, process_admin_password_callback, call.data)
            return
        
        # Gestion des callbacks admin authentifiés
        if call.data == "admin_broadcast":
            msg = bot.send_message(call.message.chat.id, "📢 **Mode Broadcast**\n\nEnvoyez le message à diffuser :")
            bot.register_next_step_handler(msg, process_broadcast_message)
        
        elif call.data == "admin_stats":
            total_users = len(get_all_users())
            premium_users = len(get_premium_users())
            groups_count = get_group_stats()
            
            stats_text = f"""
📊 **STATISTIQUES DÉTAILLÉES**

👥 **Utilisateurs :**
• Total: {total_users}
• Premium: {premium_users}
• Standard: {total_users - premium_users}
• Taux: {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%

📁 **Groupes :** {groups_count}/5
🕐 **Dernière MAJ :** {datetime.now().strftime('%H:%M %d/%m/%Y')}
"""
            bot.answer_callback_query(call.id, "📊 Statistiques affichées")
            bot.send_message(call.message.chat.id, stats_text, parse_mode='Markdown')
        
        elif call.data == "admin_users":
            bot.answer_callback_query(call.id, "👥 Gestion utilisateurs")
            bot.send_message(call.message.chat.id, "👥 **GESTION DES UTILISATEURS**", reply_markup=create_users_management_menu())
        
        elif call.data == "admin_premium":
            bot.answer_callback_query(call.id, "⭐ Gestion premium")
            bot.send_message(call.message.chat.id, "⭐ **GESTION DU PREMIUM**", reply_markup=create_premium_management_menu())
        
        elif call.data == "admin_list_users":
            users = get_all_users()
            if not users:
                bot.answer_callback_query(call.id, "📭 Aucun utilisateur")
                bot.send_message(call.message.chat.id, "📭 Aucun utilisateur enregistré.")
                return
            
            response = "👥 **LISTE DES UTILISATEURS**\n\n"
            for i, user in enumerate(users[:20], 1):
                user_id, username, first_name, has_premium, premium_since = user
                premium_status = "⭐" if has_premium else "🔒"
                username_display = f"@{username}" if username else "Sans username"
                response += f"{i}. {premium_status} {first_name} ({username_display}) - ID: `{user_id}`\n"
            
            if len(users) > 20:
                response += f"\n... et {len(users) - 20} autres utilisateurs"
            
            bot.answer_callback_query(call.id, "📋 Liste utilisateurs")
            bot.send_message(call.message.chat.id, response, parse_mode='Markdown')
        
        elif call.data == "admin_list_premium":
            premium_users = get_premium_users()
            if not premium_users:
                bot.answer_callback_query(call.id, "⭐ Aucun premium")
                bot.send_message(call.message.chat.id, "⭐ Aucun utilisateur premium.")
                return
            
            response = "⭐ **UTILISATEURS PREMIUM**\n\n"
            for i, user in enumerate(premium_users, 1):
                user_id, username, first_name, premium_since = user
                username_display = f"@{username}" if username else "Sans username"
                since = premium_since.split()[0] if premium_since else "Date inconnue"
                response += f"{i}. {first_name} ({username_display}) - ID: `{user_id}`\n   Depuis: {since}\n"
            
            bot.answer_callback_query(call.id, "⭐ Liste premium")
            bot.send_message(call.message.chat.id, response, parse_mode='Markdown')
        
        elif call.data == "admin_search_user":
            msg = bot.send_message(call.message.chat.id, "🔍 **RECHERCHER UTILISATEUR**\n\nEnvoyez l'ID de l'utilisateur :")
            bot.register_next_step_handler(msg, process_user_info)
        
        elif call.data == "admin_give_premium":
            msg = bot.send_message(call.message.chat.id, "⭐ **DONNER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
            bot.register_next_step_handler(msg, process_give_premium)
        
        elif call.data == "admin_remove_premium":
            msg = bot.send_message(call.message.chat.id, "🔒 **RETIRER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
            bot.register_next_step_handler(msg, process_remove_premium)
        
        elif call.data == "admin_premium_all":
            users = get_all_users()
            for user in users:
                activate_user_premium(user[0])
            bot.answer_callback_query(call.id, "✅ Premium à tous")
            bot.send_message(call.message.chat.id, f"⭐ **Premium activé pour tous les {len(users)} utilisateurs !**")
        
        elif call.data == "admin_remove_all_premium":
            users = get_all_users()
            for user in users:
                if user[0] != ADMIN_ID:  # Ne pas se retirer à soi-même
                    deactivate_user_premium(user[0])
            bot.answer_callback_query(call.id, "🔒 Premium retiré à tous")
            bot.send_message(call.message.chat.id, f"🔒 **Premium retiré à tous les utilisateurs sauf vous !**")
        
        elif call.data == "admin_back":
            bot.answer_callback_query(call.id, "🔙 Retour")
            bot.send_message(call.message.chat.id, "👑 **PANEL ADMINISTRATEUR**", reply_markup=create_admin_menu())

def process_admin_password_callback(message, action):
    """Gère l'authentification par callback"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if verify_admin_password(message.text.strip()):
        admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
        bot.send_message(message.chat.id, "✅ **Authentification réussie !**")
        
        # Rappeler l'action originale
        if action == "admin_broadcast":
            msg = bot.send_message(message.chat.id, "📢 **Mode Broadcast**\n\nEnvoyez le message à diffuser :")
            bot.register_next_step_handler(msg, process_broadcast_message)
        elif action == "admin_users":
            bot.send_message(message.chat.id, "👥 **GESTION DES UTILISATEURS**", reply_markup=create_users_management_menu())
        elif action == "admin_premium":
            bot.send_message(message.chat.id, "⭐ **GESTION DU PREMIUM**", reply_markup=create_premium_management_menu())
    else:
        bot.send_message(message.chat.id, "❌ **Mot de passe incorrect.**")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    init_db()
    
    print(f"""
🎯 {BOT_NAME} - {VERSION}
👑 Créateur : {CREATOR}
🔐 Sécurité renforcée avec mot de passe
⭐ Premium individuel pour chaque utilisateur
👥 Commandes admin complètes
📊 Gestion utilisateurs avancée
⚡ Modèle : {current_model}

🚀 Bot professionnel et sécurisé !
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Arrêt : {e}")
