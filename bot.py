#!/data/data/com.termux/files/usr/bin/python3
import telebot
import requests
import os
import random
import re
import time
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

# ==================== CONFIGURATION ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# 👑 IDENTITÉ
CREATOR = "👑 Kervens"
BOT_NAME = "🚀 KervensAI Pro"
VERSION = "💎 Édition LÉGENDAIRE"
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
current_model = "llama-3.1-8b-instant"

# 🔐 ADMIN - 7908680781 EST LE PROPRIÉTAIRE PERMANENT
ADMIN_ID = 7908680781

# LIEN AFFILIÉ UNIQUE DU BOT
AFFILIATE_LINK = "https://t.me/Kervensbug_bot"

# CONTRÔLES IA
AI_ENABLED = True
PREMIUM_REQUIRED = True

# Stockage
user_sessions = {}

# ==================== BASE DE DONNÉES ====================
def init_db():
    """Initialise la base de données avec vérification des colonnes"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Table des utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS user_access
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  has_premium BOOLEAN DEFAULT FALSE,
                  premium_since TIMESTAMP,
                  referrals_count INTEGER DEFAULT 0,
                  added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Table des parrainages
    c.execute('''CREATE TABLE IF NOT EXISTS referrals
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  referrer_id INTEGER,
                  referred_user_id INTEGER,
                  referral_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Table des statistiques d'usage
    c.execute('''CREATE TABLE IF NOT EXISTS user_activity
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  activity_date DATE DEFAULT CURRENT_DATE,
                  message_count INTEGER DEFAULT 1,
                  UNIQUE(user_id, activity_date))''')
    
    # Table des paramètres
    c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                 (id INTEGER PRIMARY KEY CHECK (id = 1),
                  ai_enabled BOOLEAN DEFAULT TRUE,
                  premium_required BOOLEAN DEFAULT TRUE)''')
    
    # Insérer les paramètres par défaut
    c.execute('''INSERT OR IGNORE INTO bot_settings (id, ai_enabled, premium_required) 
                 VALUES (1, TRUE, TRUE)''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

def load_settings():
    """Charge les paramètres du bot"""
    global AI_ENABLED, PREMIUM_REQUIRED
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT ai_enabled, premium_required FROM bot_settings WHERE id = 1')
    result = c.fetchone()
    conn.close()
    
    if result:
        AI_ENABLED = bool(result[0])
        PREMIUM_REQUIRED = bool(result[1])
    return AI_ENABLED, PREMIUM_REQUIRED

def save_settings(ai_enabled=None, premium_required=None):
    """Sauvegarde les paramètres du bot"""
    global AI_ENABLED, PREMIUM_REQUIRED
    
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    if ai_enabled is not None:
        AI_ENABLED = ai_enabled
        c.execute('UPDATE bot_settings SET ai_enabled = ? WHERE id = 1', (ai_enabled,))
    
    if premium_required is not None:
        PREMIUM_REQUIRED = premium_required
        c.execute('UPDATE bot_settings SET premium_required = ? WHERE id = 1', (premium_required,))
    
    conn.commit()
    conn.close()
    print(f"⚙️ Paramètres mis à jour - IA: {AI_ENABLED}, Premium requis: {PREMIUM_REQUIRED}")

def check_premium_access(user_id):
    if not PREMIUM_REQUIRED:
        return True
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT has_premium FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result and result[0]

def activate_user_premium(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, username, first_name, has_premium, premium_since, last_activity) 
                 VALUES (?, ?, ?, ?, ?, ?)''', 
                 (user_id, "user", "User", True, datetime.now(), datetime.now()))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium, referrals_count, added_date FROM user_access')
    users = c.fetchall()
    conn.close()
    return users

def get_user_referrals_count(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT referrals_count FROM user_access WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def increment_referral_count(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('UPDATE user_access SET referrals_count = referrals_count + 1 WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def register_user(user_id, username, first_name, referrer_id=None):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    c.execute('SELECT user_id FROM user_access WHERE user_id = ?', (user_id,))
    existing_user = c.fetchone()
    
    if not existing_user:
        c.execute('''INSERT INTO user_access 
                     (user_id, username, first_name, added_date, last_activity) 
                     VALUES (?, ?, ?, ?, ?)''', 
                     (user_id, username, first_name, datetime.now(), datetime.now()))
    else:
        c.execute('UPDATE user_access SET last_activity = ? WHERE user_id = ?', 
                  (datetime.now(), user_id))
    
    if referrer_id and referrer_id != user_id:
        c.execute('INSERT OR IGNORE INTO referrals (referrer_id, referred_user_id) VALUES (?, ?)', 
                 (referrer_id, user_id))
        increment_referral_count(referrer_id)
    
    conn.commit()
    conn.close()

def update_user_activity(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    c.execute('UPDATE user_access SET last_activity = ? WHERE user_id = ?', 
              (datetime.now(), user_id))
    
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('''INSERT OR REPLACE INTO user_activity (user_id, activity_date, message_count)
                 VALUES (?, ?, COALESCE(
                     (SELECT message_count FROM user_activity WHERE user_id = ? AND activity_date = ?),
                     0
                 ) + 1)''', (user_id, today, user_id, today))
    
    conn.commit()
    conn.close()

def get_monthly_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    first_day = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_day_str = first_day.strftime('%Y-%m-%d')
    
    c.execute('''SELECT COUNT(DISTINCT user_id) FROM user_activity 
                 WHERE activity_date >= ?''', (first_day_str,))
    
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else 0

def get_total_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_access')
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_active_users_last_30_days():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    c.execute('''SELECT COUNT(DISTINCT user_id) FROM user_activity 
                 WHERE activity_date >= ?''', (thirty_days_ago,))
    
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else 0

def get_daily_stats():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    today = datetime.now().strftime('%Y-%m-%d')
    
    c.execute('SELECT SUM(message_count) FROM user_activity WHERE activity_date = ?', (today,))
    result = c.fetchone()
    today_messages = result[0] if result and result[0] else 0
    
    c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date = ?', (today,))
    result = c.fetchone()
    today_users = result[0] if result else 0
    
    conn.close()
    
    return today_users, today_messages

# ==================== FONCTIONS ADMIN ====================
def is_owner(user_id):
    return user_id == ADMIN_ID

# ==================== FONCTIONS UTILISATEURS ====================
def get_progress_bar(referrals_count):
    filled = '█' * min(referrals_count, 5)
    empty = '░' * (5 - min(referrals_count, 5))
    return f"`[{filled}{empty}]` {referrals_count}/5"

def get_header_stats():
    monthly_users = get_monthly_users()
    total_users = get_total_users()
    today_users, today_messages = get_daily_stats()
    
    ai_status = "🟢" if AI_ENABLED else "🔴"
    premium_status = "🔒" if PREMIUM_REQUIRED else "🔓"
    
    return f"{ai_status} IA • {premium_status} Premium • 👥 {monthly_users} mensuels"

def create_main_menu():
    keyboard = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    keyboard.add(support_button)
    return keyboard

def create_premium_menu(user_id=None):
    keyboard = InlineKeyboardMarkup()
    
    share_button = InlineKeyboardButton("📤 Partager le Lien", 
                                      url=f"https://t.me/share/url?url={AFFILIATE_LINK}?start={user_id}&text=🚀 Découvrez KervensAI Pro - L'IA la plus puissante sur Telegram !")
    
    copy_button = InlineKeyboardButton("📋 Copier le Lien", callback_data="copy_link")
    status_button = InlineKeyboardButton("📊 Vérifier le statut", callback_data="check_status")
    premium_button = InlineKeyboardButton("🎁 Activer Premium", callback_data="activate_premium")
    
    keyboard.add(share_button)
    keyboard.add(copy_button)
    keyboard.add(status_button)
    keyboard.add(premium_button)
    
    return keyboard

def create_owner_menu():
    """Menu du propriétaire avec TOUS les contrôles"""
    keyboard = InlineKeyboardMarkup()
    
    # 📊 STATISTIQUES
    stats_btn = InlineKeyboardButton("📊 Statistiques", callback_data="admin_stats")
    users_btn = InlineKeyboardButton("👥 Utilisateurs", callback_data="admin_users")
    
    # ⭐ GESTION PREMIUM
    premium_btn = InlineKeyboardButton("⭐ Gérer Premium", callback_data="admin_premium")
    give_premium_btn = InlineKeyboardButton("🎁 Donner Premium", callback_data="admin_give_premium")
    premium_all_btn = InlineKeyboardButton("⚡ Premium à Tous", callback_data="admin_premium_all")
    remove_all_btn = InlineKeyboardButton("🗑️ Retirer à Tous", callback_data="admin_remove_all_premium")
    
    # 🤖 CONTRÔLE IA
    ai_on_btn = InlineKeyboardButton("🟢 IA ON", callback_data="admin_ai_on")
    ai_off_btn = InlineKeyboardButton("🔴 IA OFF", callback_data="admin_ai_off")
    premium_on_btn = InlineKeyboardButton("🔒 Premium ON", callback_data="admin_premium_on")
    premium_off_btn = InlineKeyboardButton("🔓 Premium OFF", callback_data="admin_premium_off")
    
    # 📢 COMMUNICATION
    broadcast_btn = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    
    # Organisation des boutons
    keyboard.add(stats_btn, users_btn)
    keyboard.add(premium_btn, give_premium_btn)
    keyboard.add(premium_all_btn, remove_all_btn)
    keyboard.add(ai_on_btn, ai_off_btn)
    keyboard.add(premium_on_btn, premium_off_btn)
    keyboard.add(broadcast_btn)
    
    return keyboard

def create_premium_management_menu():
    """Menu de gestion premium avancé"""
    keyboard = InlineKeyboardMarkup()
    
    give_btn = InlineKeyboardButton("🎁 Donner Premium", callback_data="admin_give_premium")
    remove_btn = InlineKeyboardButton("🔒 Retirer Premium", callback_data="admin_remove_premium")
    all_btn = InlineKeyboardButton("⚡ Premium à Tous", callback_data="admin_premium_all")
    remove_all_btn = InlineKeyboardButton("🗑️ Retirer à Tous", callback_data="admin_remove_all_premium")
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    
    keyboard.add(give_btn, remove_btn)
    keyboard.add(all_btn, remove_all_btn)
    keyboard.add(back_btn)
    
    return keyboard

# ==================== ENVOI DE PHOTO ====================
def send_legendary_photo(chat_id, caption, reply_markup=None):
    try:
        bot.send_photo(
            chat_id,
            MAIN_PHOTO,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return True
    except Exception as e:
        bot.send_message(
            chat_id,
            caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return False

# ==================== FONCTIONS ADMIN DIRECTES ====================
def show_stats(user_id):
    total_users = get_total_users()
    premium_users = len([u for u in get_all_users() if u[3]])
    monthly_users = get_monthly_users()
    active_30_days = get_active_users_last_30_days()
    today_users, today_messages = get_daily_stats()
    total_referrals = sum([u[4] for u in get_all_users()])
    
    ai_status = "🟢 ACTIVÉE" if AI_ENABLED else "🔴 DÉSACTIVÉE"
    premium_status = "🔒 REQUIS" if PREMIUM_REQUIRED else "🔓 GRATUIT"
    
    stats_text = f"""
📊 **STATISTIQUES RÉELLES - {BOT_NAME}**

🤖 **État IA :** {ai_status}
⭐ **Premium :** {premium_status}

👥 **Utilisateurs Totaux :** {total_users}
⭐ **Utilisateurs Premium :** {premium_users}
📈 **Utilisateurs Mensuels :** {monthly_users}
🔥 **Actifs (30j) :** {active_30_days}

📅 **Aujourd'hui :**
• 👤 Utilisateurs actifs: {today_users}
• 💬 Messages envoyés: {today_messages}

📤 **Parrainages Totaux :** {total_referrals}
🕐 **MAJ :** {datetime.now().strftime('%H:%M %d/%m/%Y')}
"""
    send_legendary_photo(user_id, stats_text)

def show_users(user_id):
    users = get_all_users()
    if not users:
        bot.send_message(user_id, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **LISTE DES UTILISATEURS**\n\n"
    for i, user in enumerate(users[:10], 1):
        user_id, username, first_name, has_premium, referrals_count, added_date = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "❌ Sans username"
        response += f"{i}. {premium_status} **{first_name}**\n"
        response += f"   👤 {username_display}\n"
        response += f"   🆔 `{user_id}`\n"
        response += f"   📊 Parrainages: {referrals_count}\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if len(users) > 10:
        response += f"\n... et {len(users) - 10} autres"
    
    send_legendary_photo(user_id, response)

def start_broadcast(user_id):
    msg = bot.send_message(user_id, "📢 **BROADCAST**\n\n💎 Envoyez le message à diffuser à tous les utilisateurs :")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    
    broadcast_text = message.text
    users = get_all_users()
    total_users = len(users)
    
    progress_msg = bot.send_message(message.chat.id, f"📤 **Envoi en cours...**\n0/{total_users} utilisateurs")
    
    success_count = 0
    fail_count = 0
    
    for i, user in enumerate(users):
        try:
            bot.send_message(user[0], f"📢 **Message de l'admin**\n\n{broadcast_text}")
            success_count += 1
        except:
            fail_count += 1
        
        if i % 5 == 0:
            try:
                bot.edit_message_text(
                    f"📤 **Envoi en cours...**\n{i+1}/{total_users} utilisateurs",
                    message.chat.id,
                    progress_msg.message_id
                )
            except:
                pass
        
        time.sleep(0.5)
    
    result_text = f"""
✅ **BROADCAST TERMINÉ !**

📊 **Résultats :**
• ✅ Messages délivrés : {success_count}
• ❌ Échecs : {fail_count}
• 📝 Total : {total_users}
"""
    send_legendary_photo(message.chat.id, result_text)

def give_premium_to_all(user_id):
    users = get_all_users()
    for user in users:
        activate_user_premium(user[0])
    
    response = f"⚡ **PREMIUM ACTIVÉ !**\n\n⭐ **Premium activé pour {len(users)} utilisateurs !**"
    send_legendary_photo(user_id, response)

def remove_premium_from_all(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('UPDATE user_access SET has_premium = FALSE, premium_since = NULL')
    conn.commit()
    conn.close()
    
    response = "🗑️ **PREMIUM RETIRÉ !**\n\n🔒 **Premium retiré pour tous les utilisateurs !**"
    send_legendary_photo(user_id, response)

def remove_premium_from_user(target_user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('UPDATE user_access SET has_premium = FALSE, premium_since = NULL WHERE user_id = ?', (target_user_id,))
    conn.commit()
    conn.close()
    
    return f"🔒 **Premium retiré pour l'utilisateur {target_user_id}**"

# ==================== FONCTIONS DE PROCESSUS ====================
def process_give_premium(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    
    try:
        target_user_id = int(message.text.strip())
        activate_user_premium(target_user_id)
        
        try:
            bot.send_message(target_user_id, "🎉 **FÉLICITATIONS !**\n\n⭐ **Vous avez reçu le PREMIUM !**")
        except:
            pass
        
        bot.send_message(message.chat.id, f"✅ **Premium donné à {target_user_id}**")
        
    except ValueError:
        bot.reply_to(message, "❌ ID invalide")

def process_remove_premium(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    
    try:
        target_user_id = int(message.text.strip())
        response = remove_premium_from_user(target_user_id)
        bot.send_message(message.chat.id, response)
        
    except ValueError:
        bot.reply_to(message, "❌ ID invalide")

# ==================== HANDLERS UTILISATEURS ====================
@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        referrer_id = None
        if len(message.text.split()) > 1:
            try:
                referrer_id = int(message.text.split()[1])
            except:
                pass
        
        register_user(user_id, username, first_name, referrer_id)
        update_user_activity(user_id)
        
        if is_owner(user_id):
            activate_user_premium(user_id)
            
            header_stats = get_header_stats()
            caption = f"""
{header_stats}

👑 **{BOT_NAME} - {VERSION}**

💎 **BIENVENUE PROPRIÉTAIRE !**

🎛️ **Contrôles disponibles :**
• 🤖 Activer/Désactiver l'IA
• ⭐ Gérer les premiums
• 📢 Broadcast massif
• 📊 Statistiques détaillées

🚀 **Utilisez les boutons ci-dessous !**
"""
            send_legendary_photo(message.chat.id, caption, create_owner_menu())
            return
        
        header_stats = get_header_stats()
        
        if check_premium_access(user_id):
            caption = f"""
{header_stats}

🎉 **{BOT_NAME} - {VERSION} PREMIUM**

⭐ **Version Premium Activée !**

💫 **Fonctionnalités débloquées :**
• 💻 Programmation & Code
• 🎨 Création & Rédaction  
• 📊 Analyse & Conseil
• 🌍 Traduction
• 💬 Conversation naturelle

✨ **Envoyez-moi un message pour commencer !**
"""
            send_legendary_photo(message.chat.id, caption, create_main_menu())
        else:
            referrals_count = get_user_referrals_count(user_id)
            
            if referrals_count >= 5:
                caption = f"""
{header_stats}

🎊 **{BOT_NAME} - PRÊT POUR LE PREMIUM !**

{get_progress_bar(referrals_count)}

✅ **Conditions remplies !** 
5/5 parrainages atteints !

🎁 **Cliquez sur "Activer Premium"**
pour débloquer toutes les fonctionnalités !
"""
            else:
                caption = f"""
{header_stats}

🔒 **{BOT_NAME} - {VERSION} LIMITÉE**

🚀 **Assistant IA optimisé pour Groq**

{get_progress_bar(referrals_count)}

📈 **Statut actuel :** {referrals_count}/5 parrainages

🔗 **Ton lien :** `{AFFILIATE_LINK}?start={user_id}`
"""
            send_legendary_photo(message.chat.id, caption, create_premium_menu(user_id))
            
    except Exception as e:
        print(f"❌ Erreur start: {e}")

# ==================== COMMANDES ADMIN ====================
@bot.message_handler(commands=['stats'])
def stats_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    show_stats(user_id)

@bot.message_handler(commands=['users'])
def users_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    show_users(user_id)

@bot.message_handler(commands=['premium_all'])
def premium_all_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    give_premium_to_all(user_id)

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    user_id = message.from_user.id
    if not is_owner(user_id):
        return
    start_broadcast(user_id)

# ==================== GESTION DES CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    # Callbacks utilisateurs normaux
    if call.data == "check_status":
        referrals_count = get_user_referrals_count(user_id)
        if check_premium_access(user_id):
            bot.answer_callback_query(call.id, "✅ Premium activé !")
        else:
            bot.answer_callback_query(call.id, f"📊 {referrals_count}/5 parrainages")
    
    elif call.data == "activate_premium":
        referrals_count = get_user_referrals_count(user_id)
        if referrals_count >= 5:
            activate_user_premium(user_id)
            bot.answer_callback_query(call.id, "🎉 Premium activé !")
            header_stats = get_header_stats()
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"{header_stats}\n\n🎉 **Premium activé avec succès !**\n\n✨ **Profitez de toutes les fonctionnalités IA !**",
                    parse_mode='Markdown',
                    reply_markup=create_main_menu()
                )
            except:
                bot.send_message(call.message.chat.id, "🎉 **Premium activé !**")
        else:
            bot.answer_callback_query(call.id, f"❌ {5-referrals_count} parrainages manquants")
    
    elif call.data == "copy_link":
        bot.answer_callback_query(call.id, "📋 Lien copié !")
        bot.send_message(call.message.chat.id, 
                        f"🔗 **Ton lien affilié :**\n\n`{AFFILIATE_LINK}?start={user_id}`\n\n📤 **Partage ce lien !**")
    
    # ==================== CALLBACKS ADMIN ====================
    elif call.data.startswith("admin_"):
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "🔐 Accès refusé")
            return
        
        # 📊 STATISTIQUES
        if call.data == "admin_stats":
            show_stats(user_id)
            bot.answer_callback_query(call.id, "📊 Statistiques")
        
        elif call.data == "admin_users":
            show_users(user_id)
            bot.answer_callback_query(call.id, "👥 Utilisateurs")
        
        # ⭐ GESTION PREMIUM
        elif call.data == "admin_premium":
            send_legendary_photo(
                call.message.chat.id,
                "⭐ **GESTION PREMIUM AVANCÉE**\n\nChoisissez une action :",
                create_premium_management_menu()
            )
            bot.answer_callback_query(call.id, "⭐ Gestion Premium")
        
        elif call.data == "admin_give_premium":
            msg = bot.send_message(call.message.chat.id, "🎁 **DONNER PREMIUM**\n\nEnvoyez l'ID utilisateur :")
            bot.register_next_step_handler(msg, process_give_premium)
            bot.answer_callback_query(call.id, "🎁 Donner Premium")
        
        elif call.data == "admin_remove_premium":
            msg = bot.send_message(call.message.chat.id, "🔒 **RETIRER PREMIUM**\n\nEnvoyez l'ID utilisateur :")
            bot.register_next_step_handler(msg, process_remove_premium)
            bot.answer_callback_query(call.id, "🔒 Retirer Premium")
        
        elif call.data == "admin_premium_all":
            give_premium_to_all(user_id)
            bot.answer_callback_query(call.id, "⚡ Premium à Tous")
        
        elif call.data == "admin_remove_all_premium":
            remove_premium_from_all(user_id)
            bot.answer_callback_query(call.id, "🗑️ Premium retiré à tous")
        
        # 🤖 CONTRÔLE IA
        elif call.data == "admin_ai_on":
            save_settings(ai_enabled=True)
            bot.answer_callback_query(call.id, "🟢 IA ACTIVÉE")
            header_stats = get_header_stats()
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{header_stats}\n\n🤖 **IA ACTIVÉE !**\n\nL'assistant IA est maintenant disponible pour tous les utilisateurs premium.",
                parse_mode='Markdown',
                reply_markup=create_owner_menu()
            )
        
        elif call.data == "admin_ai_off":
            save_settings(ai_enabled=False)
            bot.answer_callback_query(call.id, "🔴 IA DÉSACTIVÉE")
            header_stats = get_header_stats()
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{header_stats}\n\n🤖 **IA DÉSACTIVÉE !**\n\nL'assistant IA est temporairement indisponible.",
                parse_mode='Markdown',
                reply_markup=create_owner_menu()
            )
        
        elif call.data == "admin_premium_on":
            save_settings(premium_required=True)
            bot.answer_callback_query(call.id, "🔒 PREMIUM REQUIS")
            header_stats = get_header_stats()
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{header_stats}\n\n⭐ **PREMIUM REQUIS !**\n\nSeuls les utilisateurs premium peuvent utiliser l'IA.",
                parse_mode='Markdown',
                reply_markup=create_owner_menu()
            )
        
        elif call.data == "admin_premium_off":
            save_settings(premium_required=False)
            bot.answer_callback_query(call.id, "🔓 PREMIUM GRATUIT")
            header_stats = get_header_stats()
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"{header_stats}\n\n⭐ **PREMIUM GRATUIT !**\n\nTous les utilisateurs peuvent utiliser l'IA sans restriction.",
                parse_mode='Markdown',
                reply_markup=create_owner_menu()
            )
        
        elif call.data == "admin_back":
            header_stats = get_header_stats()
            send_legendary_photo(
                call.message.chat.id,
                f"{header_stats}\n\n👑 **PANEL DE CONTRÔLE**\n\nRetour au menu principal :",
                create_owner_menu()
            )
            bot.answer_callback_query(call.id, "🔙 Retour")
        
        # 📢 BROADCAST
        elif call.data == "admin_broadcast":
            start_broadcast(user_id)
            bot.answer_callback_query(call.id, "📢 Broadcast")

# ==================== MOTEUR IA ====================
def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {'conversation': []}
    return user_sessions[user_id]

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    
    update_user_activity(user_id)
    
    if not AI_ENABLED:
        bot.reply_to(message, "🤖 **IA TEMPORAIREMENT INDISPONIBLE**\n\nL'assistant IA est actuellement désactivé par l'administrateur.")
        return
    
    if not check_premium_access(user_id):
        referrals_count = get_user_referrals_count(user_id)
        header_stats = get_header_stats()
        if referrals_count >= 5:
            bot.reply_to(message, 
                       f"{header_stats}\n\n🎊 **PRÊT POUR LE PREMIUM !**\n\n✅ 5/5 parrainages !\n\n🎁 Cliquez sur 'Activer Premium' !",
                       reply_markup=create_premium_menu(user_id))
        else:
            bot.reply_to(message, 
                       f"{header_stats}\n\n🔒 **Version limitée**\n\n{get_progress_bar(referrals_count)}\n\nPartage ton lien !",
                       reply_markup=create_premium_menu(user_id))
        return
    
    # ✅ UTILISATEUR PREMIUM - Traitement IA
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        if not GROQ_API_KEY:
            bot.reply_to(message, "❌ Service IA indisponible.")
            return
            
        user_session = get_user_session(user_id)
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        messages = [{"role": "system", "content": f"Tu es {BOT_NAME}, assistant IA créé par {CREATOR}. Sois utile et naturel."}]
        if user_session['conversation']:
            messages.extend(user_session['conversation'][-2:])
        
        user_message = message.text[:500]
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
            
            user_session['conversation'].append({"role": "user", "content": user_message[:200]})
            user_session['conversation'].append({"role": "assistant", "content": answer[:500]})
            user_sessions[user_id] = user_session
            
            bot.reply_to(message, answer)
        else:
            bot.reply_to(message, "❌ Erreur de service. Réessayez.")
            
    except Exception as e:
        print(f"❌ Erreur IA: {e}")
        bot.reply_to(message, "🔧 Service indisponible. Réessayez.")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🗃️ Initialisation...")
    init_db()
    load_settings()
    print("✅ Base prête")
    print(f"🚀 {BOT_NAME} - {VERSION}")
    print(f"👑 Créateur: {CREATOR}")
    print("🎛️  CONTRÔLES ADMIN COMPLETS")
    print(f"   👑 Propriétaire: {ADMIN_ID}")
    print(f"   🤖 IA: {'🟢 ACTIVÉE' if AI_ENABLED else '🔴 DÉSACTIVÉE'}")
    print(f"   ⭐ Premium: {'🔒 REQUIS' if PREMIUM_REQUIRED else '🔓 GRATUIT'}")
    print("   📊 Statistiques réelles")
    print("🤖 En attente de messages...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
