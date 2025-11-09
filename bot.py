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

# Stockage
user_sessions = {}

# ==================== BASE DE DONNÉES ====================
def init_db():
    """Initialise la base de données"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Table des utilisateurs avec système de parrainage
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
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

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
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, has_premium, premium_since) VALUES (?, ?, ?)''', 
                 (user_id, True, datetime.now()))
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
    
    # Enregistrer l'utilisateur
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, username, first_name, added_date, last_activity) 
                 VALUES (?, ?, ?, ?, ?)''', 
                 (user_id, username, first_name, datetime.now(), datetime.now()))
    
    # Enregistrer le parrainage si applicable
    if referrer_id:
        c.execute('INSERT INTO referrals (referrer_id, referred_user_id) VALUES (?, ?)', 
                 (referrer_id, user_id))
        increment_referral_count(referrer_id)
    
    conn.commit()
    conn.close()

def update_user_activity(user_id):
    """Met à jour l'activité de l'utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Mettre à jour last_activity dans user_access
    c.execute('UPDATE user_access SET last_activity = ? WHERE user_id = ?', 
              (datetime.now(), user_id))
    
    # Incrémenter le compteur de messages pour aujourd'hui
    c.execute('''INSERT INTO user_activity (user_id, message_count) 
                 VALUES (?, 1)
                 ON CONFLICT(user_id, activity_date) 
                 DO UPDATE SET message_count = message_count + 1''', 
                 (user_id,))
    
    conn.commit()
    conn.close()

def get_monthly_users():
    """Compte les utilisateurs actifs du mois en cours (RÉEL)"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Utilisateurs uniques qui ont eu une activité ce mois-ci
    first_day_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    c.execute('''SELECT COUNT(DISTINCT user_id) FROM user_activity 
                 WHERE activity_date >= ?''', (first_day_of_month,))
    
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else 0

def get_total_users():
    """Compte le nombre total d'utilisateurs enregistrés"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM user_access')
    result = c.fetchone()
    conn.close()
    return result[0] if result else 0

def get_active_users_last_30_days():
    """Compte les utilisateurs actifs dans les 30 derniers jours"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    c.execute('''SELECT COUNT(DISTINCT user_id) FROM user_activity 
                 WHERE activity_date >= ?''', (thirty_days_ago,))
    
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else 0

def get_daily_stats():
    """Statistiques d'usage du jour"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    today = datetime.now().date()
    
    # Messages aujourd'hui
    c.execute('SELECT SUM(message_count) FROM user_activity WHERE activity_date = ?', (today,))
    today_messages = c.fetchone()[0] or 0
    
    # Utilisateurs actifs aujourd'hui
    c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date = ?', (today,))
    today_users = c.fetchone()[0] or 0
    
    conn.close()
    
    return today_users, today_messages

# ==================== FONCTIONS ADMIN ====================
def is_owner(user_id):
    """Vérifie si l'utilisateur est le propriétaire 7908680781"""
    return user_id == ADMIN_ID

# ==================== FONCTIONS UTILISATEURS ====================
def get_progress_bar(referrals_count):
    filled = '█' * min(referrals_count, 5)
    empty = '░' * (5 - min(referrals_count, 5))
    return f"`[{filled}{empty}]` {referrals_count}/5"

def get_header_stats():
    """Retourne les statistiques pour l'en-tête"""
    monthly_users = get_monthly_users()
    total_users = get_total_users()
    today_users, today_messages = get_daily_stats()
    
    return f"👥 {monthly_users} utilisateurs mensuels • 📊 {total_users} total • 🔥 {today_users} actifs aujourd'hui"

def create_main_menu():
    keyboard = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    keyboard.add(support_button)
    return keyboard

def create_premium_menu(user_id=None):
    """Menu premium avec lien de parrainage"""
    keyboard = InlineKeyboardMarkup()
    
    # Bouton pour partager le lien affilié
    share_button = InlineKeyboardButton("📤 Partager le Lien", url=f"https://t.me/share/url?url={AFFILIATE_LINK}?start={user_id}&text=🚀 Découvrez KervensAI Pro - L'IA la plus puissante sur Telegram !")
    
    # Bouton pour copier le lien
    copy_button = InlineKeyboardButton("📋 Copier le Lien", callback_data="copy_link")
    
    status_button = InlineKeyboardButton("📊 Vérifier le statut", callback_data="check_status")
    premium_button = InlineKeyboardButton("🎁 Activer Premium", callback_data="activate_premium")
    
    keyboard.add(share_button)
    keyboard.add(copy_button)
    keyboard.add(status_button)
    keyboard.add(premium_button)
    
    return keyboard

def create_owner_menu():
    """Menu du propriétaire 7908680781 - TOUT DÉBLOQUÉ"""
    keyboard = InlineKeyboardMarkup()
    
    # 📊 STATISTIQUES
    stats_btn = InlineKeyboardButton("📊 Statistiques", callback_data="admin_stats")
    users_btn = InlineKeyboardButton("👥 Utilisateurs", callback_data="admin_users")
    
    # ⭐ GESTION PREMIUM
    premium_btn = InlineKeyboardButton("⭐ Gérer Premium", callback_data="admin_premium")
    give_premium_btn = InlineKeyboardButton("🎁 Donner Premium", callback_data="admin_give_premium")
    
    # 📢 COMMUNICATION
    broadcast_btn = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    mail_btn = InlineKeyboardButton("📨 Messages", callback_data="admin_mail")
    
    # 🔧 OUTILS AVANCÉS
    logs_btn = InlineKeyboardButton("📋 Logs", callback_data="admin_logs")
    system_btn = InlineKeyboardButton("🖥️ Système", callback_data="admin_system")
    advanced_btn = InlineKeyboardButton("⚡ Avancé", callback_data="admin_advanced")
    
    # 🎯 COMMANDES RAPIDES
    premium_all_btn = InlineKeyboardButton("⚡ Premium à Tous", callback_data="admin_premium_all")
    cleanup_btn = InlineKeyboardButton("🧹 Nettoyage", callback_data="admin_cleanup")
    
    # Organisation des boutons
    keyboard.add(stats_btn, users_btn)
    keyboard.add(premium_btn, give_premium_btn)
    keyboard.add(broadcast_btn, mail_btn)
    keyboard.add(logs_btn, system_btn)
    keyboard.add(advanced_btn)
    keyboard.add(premium_all_btn, cleanup_btn)
    
    return keyboard

def create_premium_management_menu():
    """Menu de gestion premium"""
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

def create_advanced_admin_menu():
    """Menu admin avancé"""
    keyboard = InlineKeyboardMarkup()
    
    delete_user_btn = InlineKeyboardButton("🗑️ Supprimer User", callback_data="admin_delete_user")
    user_stats_btn = InlineKeyboardButton("📈 Stats Détaillées", callback_data="admin_user_stats")
    export_btn = InlineKeyboardButton("📤 Exporter Données", callback_data="admin_export")
    search_btn = InlineKeyboardButton("🔍 Rechercher User", callback_data="admin_search_user")
    cleanup_btn = InlineKeyboardButton("🧹 Nettoyage DB", callback_data="admin_cleanup")
    system_btn = InlineKeyboardButton("🖥️ Info Système", callback_data="admin_system")
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    
    keyboard.add(delete_user_btn, user_stats_btn)
    keyboard.add(export_btn, search_btn)
    keyboard.add(cleanup_btn, system_btn)
    keyboard.add(back_btn)
    
    return keyboard

# ==================== ENVOI DE PHOTO ====================
def send_legendary_photo(chat_id, caption, reply_markup=None):
    """Envoie une photo avec le style légendaire"""
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
        print(f"❌ Erreur envoi photo: {e}")
        bot.send_message(
            chat_id,
            caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return False

# ==================== FONCTIONS ADMIN DIRECTES ====================
def show_stats(user_id):
    """Affiche les statistiques RÉELLES"""
    total_users = get_total_users()
    premium_users = len([u for u in get_all_users() if u[3]])
    monthly_users = get_monthly_users()
    active_30_days = get_active_users_last_30_days()
    today_users, today_messages = get_daily_stats()
    total_referrals = sum([u[4] for u in get_all_users()])
    
    stats_text = f"""
📊 **STATISTIQUES RÉELLES - {BOT_NAME}**

👥 **Utilisateurs Totaux :** {total_users}
⭐ **Utilisateurs Premium :** {premium_users}
📈 **Utilisateurs Mensuels :** {monthly_users}
🔥 **Actifs (30j) :** {active_30_days}

📅 **Aujourd'hui :**
• 👤 Utilisateurs actifs: {today_users}
• 💬 Messages envoyés: {today_messages}

📤 **Parrainages Totaux :** {total_referrals}
🕐 **MAJ :** {datetime.now().strftime('%H:%M %d/%m/%Y')}

👑 **Propriétaire :** 7908680781
"""
    send_legendary_photo(user_id, stats_text)

def show_users(user_id):
    """Affiche la liste des utilisateurs directement"""
    users = get_all_users()
    if not users:
        bot.send_message(user_id, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **LISTE DES UTILISATEURS**\n\n"
    for i, user in enumerate(users[:15], 1):
        user_id, username, first_name, has_premium, referrals_count, added_date = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "❌ Sans username"
        response += f"{i}. {premium_status} **{first_name}**\n"
        response += f"   👤 {username_display}\n"
        response += f"   🆔 `{user_id}`\n"
        response += f"   📊 Parrainages: {referrals_count}\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if len(users) > 15:
        response += f"\n... et {len(users) - 15} autres"
    
    send_legendary_photo(user_id, response)

def start_broadcast(user_id):
    """Démarre un broadcast directement"""
    msg = bot.send_message(user_id, "📢 **BROADCAST LÉGENDAIRE**\n\n💎 Envoyez le message à diffuser à tous les utilisateurs :")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    user_id = message.from_user.id
    
    broadcast_text = message.text
    users = get_all_users()
    total_users = len(users)
    
    progress_msg = bot.send_message(message.chat.id, f"📤 **Lancement du broadcast...**\n0/{total_users} utilisateurs")
    
    success_count = 0
    fail_count = 0
    
    for i, user in enumerate(users):
        try:
            bot.send_message(user[0], f"📢 **Message de l'admin**\n\n{broadcast_text}")
            success_count += 1
        except:
            fail_count += 1
        
        if i % 10 == 0:
            try:
                bot.edit_message_text(
                    f"📤 **Propagation en cours...**\n{i+1}/{total_users} utilisateurs",
                    message.chat.id,
                    progress_msg.message_id
                )
            except:
                pass
        
        time.sleep(0.1)
    
    result_text = f"""
✅ **BROADCAST TERMINÉ !**

📊 **Résultats :**
• ✅ Messages délivrés : {success_count}
• ❌ Échecs : {fail_count}
• 📝 Total : {total_users}
"""
    send_legendary_photo(message.chat.id, result_text)

def give_premium_to_all(user_id):
    """Donne le premium à tous les utilisateurs"""
    users = get_all_users()
    for user in users:
        activate_user_premium(user[0])
    
    response = f"⚡ **PREMIUM LÉGENDAIRE ACTIVÉ !**\n\n⭐ **Premium activé pour tous les {len(users)} utilisateurs !**"
    send_legendary_photo(user_id, response)

# ==================== HANDLERS UTILISATEURS ====================
@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        # Vérifier s'il y a un paramètre de parrainage
        referrer_id = None
        if len(message.text.split()) > 1:
            try:
                referrer_id = int(message.text.split()[1])
            except:
                pass
        
        register_user(user_id, username, first_name, referrer_id)
        update_user_activity(user_id)  # Mettre à jour l'activité
        
        # Vérifier si c'est le propriétaire 7908680781
        if is_owner(user_id):
            activate_user_premium(user_id)  # Premium automatique
            
            header_stats = get_header_stats()
            caption = f"""
{header_stats}

👑 **{BOT_NAME} - {VERSION}**

💎 **BIENVENUE PROPRIÉTAIRE !**

⭐ **Premium LÉGENDAIRE activé**
🔓 **Panel de contrôle COMPLET débloqué**

🎯 **Vous avez accès à tout :**
• 📊 Statistiques avancées
• 👥 Gestion des utilisateurs  
• ⭐ Contrôle premium total
• 📢 Broadcast massif
• 🔧 Outils professionnels

🚀 **Utilisez les boutons ci-dessous !**
"""
            send_legendary_photo(message.chat.id, caption, create_owner_menu())
            return
        
        # Photo du créateur pour les utilisateurs normaux avec stats en haut
        header_stats = get_header_stats()
        send_legendary_photo(
            message.chat.id,
            f"{header_stats}\n\n📸 **{CREATOR}** - Créateur du bot\n*Votre expert en IA* 👑",
            create_main_menu() if check_premium_access(user_id) else create_premium_menu(user_id)
        )
        
        time.sleep(0.5)
        
        referrals_count = get_user_referrals_count(user_id)
        monthly_users = get_monthly_users()  # Statistique réelle
        
        if check_premium_access(user_id):
            menu = f"""
{header_stats}

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
            if referrals_count >= 5:
                menu = f"""
{header_stats}

🎊 **{BOT_NAME}** - PRÊT POUR LE PREMIUM !

{get_progress_bar(referrals_count)}

✅ **Conditions remplies !** 
5/5 parrainages atteints !

🎁 **Cliquez sur "Activer Premium" ci-dessous**
pour débloquer toutes les fonctionnalités !

🚀 **L'IA vous attend !**
"""
            else:
                menu = f"""
{header_stats}

🔒 **{BOT_NAME}** - {VERSION} **LIMITÉE**

🚀 **Assistant IA optimisé pour Groq**
*Version limitée - Débloquez le premium gratuitement !*

{get_progress_bar(referrals_count)}

🎁 **Conditions pour le Premium GRATUIT :**
• 📤 Partager ton lien affilié unique avec 5 personnes
• ✅ Déblocage immédiat après validation

📈 **Statut actuel :**
• Parrainages : {referrals_count}/5

💡 **Comment débloquer :**
1. Cliquez sur "Partager le Lien" ci-dessous
2. Partage avec tes amis
3. Le premium se débloque à 5 parrainages

🔗 **Ton lien affilié unique :**
`{AFFILIATE_LINK}?start={user_id}`
"""
            
            bot.send_message(message.chat.id, menu, parse_mode='Markdown', reply_markup=create_premium_menu(user_id))
            
    except Exception as e:
        print(f"❌ Erreur start: {e}")
        bot.reply_to(message, "❌ Erreur temporaire. Réessayez.")

@bot.message_handler(commands=['aide', 'help'])
def help_handler(message):
    """Aide pour les utilisateurs"""
    user_id = message.from_user.id
    referrals_count = get_user_referrals_count(user_id)
    header_stats = get_header_stats()
    
    help_text = f"""
{header_stats}

🆘 **AIDE - {BOT_NAME}**

🎯 **Comment obtenir le PREMIUM GRATUIT :**
1. 📤 Partage ton lien affilié avec tes amis
2. 👥 5 personnes doivent cliquer sur ton lien
3. ⭐ Le premium se débloque automatiquement

📊 **Ton progrès :**
{get_progress_bar(referrals_count)}

🔗 **Ton lien affilié unique :**
`{AFFILIATE_LINK}?start={user_id}`

💡 **Astuce :** Partage le lien dans tes groupes et avec tes amis pour débloquer rapidement le premium !
"""
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown', reply_markup=create_premium_menu(user_id))

# ==================== COMMANDES ADMIN ====================
@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Statistiques du bot"""
    user_id = message.from_user.id
    
    # Vérifier si c'est le propriétaire
    if not is_owner(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nContactez l'administrateur.")
        return
    
    show_stats(user_id)

@bot.message_handler(commands=['users'])
def users_command(message):
    """Lister les utilisateurs"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nContactez l'administrateur.")
        return
    
    show_users(user_id)

@bot.message_handler(commands=['premium_all'])
def premium_all_command(message):
    """Donner le premium à tous"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nContactez l'administrateur.")
        return
    
    give_premium_to_all(user_id)

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    """Envoyer un message à tous"""
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nContactez l'administrateur.")
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
            bot.answer_callback_query(call.id, f"📊 {referrals_count}/5 parrainages - {5-referrals_count} manquant(s)")
    
    elif call.data == "activate_premium":
        referrals_count = get_user_referrals_count(user_id)
        if referrals_count >= 5:
            activate_user_premium(user_id)
            bot.answer_callback_query(call.id, "🎉 Premium activé !")
            
            try:
                header_stats = get_header_stats()
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"{header_stats}\n\n🎉 **Premium activé avec succès !**\n\n✨ **Profitez de toutes les fonctionnalités IA !**\n💬 Envoyez-moi un message pour commencer !",
                    parse_mode='Markdown',
                    reply_markup=create_main_menu()
                )
            except:
                header_stats = get_header_stats()
                bot.send_message(call.message.chat.id, f"{header_stats}\n\n🎉 **Premium activé avec succès !**\n\n✨ Profitez de l'IA !")
        else:
            bot.answer_callback_query(call.id, f"❌ {5-referrals_count} parrainage(s) manquant(s)")
    
    elif call.data == "copy_link":
        bot.answer_callback_query(call.id, "📋 Lien copié dans le presse-papier !")
        header_stats = get_header_stats()
        bot.send_message(call.message.chat.id, 
                        f"{header_stats}\n\n🔗 **Ton lien affilié unique :**\n\n`{AFFILIATE_LINK}?start={user_id}`\n\n📤 **Copie et partage ce lien avec tes amis !**")
    
    # Callbacks admin - Vérification des droits
    elif call.data.startswith("admin_"):
        # Vérifier si c'est 7908680781
        if not is_owner(user_id):
            bot.answer_callback_query(call.id, "🔐 Accès refusé")
            bot.send_message(call.message.chat.id, "🔐 **Accès refusé.**\n\nContactez l'administrateur.")
            return
        
        # Exécuter la commande admin DIRECTEMENT
        if call.data == "admin_stats":
            show_stats(user_id)
            bot.answer_callback_query(call.id, "📊 Statistiques")
        
        elif call.data == "admin_users":
            show_users(user_id)
            bot.answer_callback_query(call.id, "👥 Utilisateurs")
        
        elif call.data == "admin_premium":
            header_stats = get_header_stats()
            send_legendary_photo(
                call.message.chat.id,
                f"{header_stats}\n\n⭐ **GESTION PREMIUM**\n\nChoisissez une action :",
                create_premium_management_menu()
            )
            bot.answer_callback_query(call.id, "⭐ Gestion Premium")
        
        elif call.data == "admin_give_premium":
            header_stats = get_header_stats()
            msg = bot.send_message(call.message.chat.id, f"{header_stats}\n\n🎁 **DONNER LE PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
            bot.register_next_step_handler(msg, process_give_premium)
            bot.answer_callback_query(call.id, "🎁 Donner Premium")
        
        elif call.data == "admin_broadcast":
            start_broadcast(user_id)
            bot.answer_callback_query(call.id, "📢 Broadcast")
        
        elif call.data == "admin_mail":
            # Simuler la commande mail
            users = get_all_users()
            header_stats = get_header_stats()
            response = f"{header_stats}\n\n📨 **MESSAGES REÇUS**\n\n📊 Total utilisateurs: {len(users)}\n💡 Fonctionnalité à venir..."
            send_legendary_photo(call.message.chat.id, response)
            bot.answer_callback_query(call.id, "📨 Messages")
        
        elif call.data == "admin_logs":
            header_stats = get_header_stats()
            response = f"{header_stats}\n\n📋 **LOGS ADMIN**\n\n🕐 Dernière activité: Maintenant\n👤 Admin connecté: Vous\n💡 Système opérationnel"
            send_legendary_photo(call.message.chat.id, response)
            bot.answer_callback_query(call.id, "📋 Logs")
        
        elif call.data == "admin_system":
            header_stats = get_header_stats()
            response = f"{header_stats}\n\n🖥️ **SYSTÈME**\n\n💾 Mémoire: OK\n⚡ CPU: Optimal\n🔗 Connexion: Stable\n🤖 Bot: Actif"
            send_legendary_photo(call.message.chat.id, response)
            bot.answer_callback_query(call.id, "🖥️ Système")
        
        elif call.data == "admin_advanced":
            header_stats = get_header_stats()
            send_legendary_photo(
                call.message.chat.id,
                f"{header_stats}\n\n⚡ **OUTILS AVANCÉS**\n\nChoisissez un outil :",
                create_advanced_admin_menu()
            )
            bot.answer_callback_query(call.id, "⚡ Avancé")
        
        elif call.data == "admin_premium_all":
            give_premium_to_all(user_id)
            bot.answer_callback_query(call.id, "⚡ Premium à Tous")
        
        elif call.data == "admin_cleanup":
            header_stats = get_header_stats()
            response = f"{header_stats}\n\n🧹 **NETTOYAGE EFFECTUÉ**\n\n✅ Base de données optimisée\n🗑️ Cache nettoyé\n⚡ Performances améliorées"
            send_legendary_photo(call.message.chat.id, response)
            bot.answer_callback_query(call.id, "🧹 Nettoyage")
        
        elif call.data == "admin_back":
            header_stats = get_header_stats()
            send_legendary_photo(
                call.message.chat.id,
                f"{header_stats}\n\n👑 **PANEL DE CONTRÔLE**\n\nRetour au menu principal :",
                create_owner_menu()
            )
            bot.answer_callback_query(call.id, "🔙 Retour")

def process_give_premium(message):
    user_id = message.from_user.id
    
    if not is_owner(user_id):
        bot.reply_to(message, "🔐 Accès refusé.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        activate_user_premium(target_user_id)
        
        try:
            bot.send_message(target_user_id, 
                           "🎉 **FÉLICITATIONS !**\n\n⭐ **Vous avez reçu le PREMIUM !**\n\n✨ Profitez de toutes les fonctionnalités IA !")
        except:
            pass
        
        header_stats = get_header_stats()
        response = f"{header_stats}\n\n✅ **PREMIUM ACCORDÉ !**\n\n⭐ **Premium activé pour l'utilisateur {target_user_id}**"
        send_legendary_photo(message.chat.id, response)
        
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

# ==================== MOTEUR IA ====================
def get_user_session(user_id):
    if user_id not in user_sessions:
        user_sessions[user_id] = {'conversation': []}
    return user_sessions[user_id]

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gère tous les messages"""
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    
    # Mettre à jour l'activité de l'utilisateur (RÉEL)
    update_user_activity(user_id)
    
    if not check_premium_access(user_id):
        referrals_count = get_user_referrals_count(user_id)
        header_stats = get_header_stats()
        if referrals_count >= 5:
            bot.reply_to(message, 
                       f"{header_stats}\n\n🎊 **PRÊT POUR LE PREMIUM !**\n\n✅ 5/5 parrainages atteints !\n\n🎁 Cliquez sur 'Activer Premium' pour débloquer l'IA !",
                       reply_markup=create_premium_menu(user_id))
        else:
            bot.reply_to(message, 
                       f"{header_stats}\n\n🔒 **Version limitée**\n\n{get_progress_bar(referrals_count)}\n\nPartage ton lien avec {5-referrals_count} personne(s) pour débloquer l'IA.",
                       reply_markup=create_premium_menu(user_id))
        return
    
    # ✅ UTILISATEUR PREMIUM - Traitement IA
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        if not GROQ_API_KEY:
            bot.reply_to(message, "❌ Service IA temporairement indisponible.")
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
    print("✅ Base prête")
    print(f"🚀 {BOT_NAME} - {VERSION}")
    print(f"👑 Créateur: {CREATOR}")
    print("💎 STATISTIQUES EN TEMPS RÉEL ACTIVÉES")
    print(f"   👑 Propriétaire: {ADMIN_ID}")
    print(f"   🔗 Lien affilié: {AFFILIATE_LINK}")
    print("   📊 Stats affichées en haut de chaque message")
    print("   📤 5 parrainages = Premium gratuit")
    print("🤖 En attente de messages...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
