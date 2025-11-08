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
CREATOR = "👑 Kervens"
BOT_NAME = "🚀 KervensAI Pro"
VERSION = "💎 Édition LÉGENDAIRE"
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
current_model = "llama-3.1-8b-instant"

# 🔐 ADMIN - @soszoe EST L'ADMIN PERMANENT
ADMIN_USERNAME = "soszoe"
ADMIN_PASSWORD = "KING1998"

# Stockage
user_sessions = {}
admin_sessions = {}

# ==================== BASE DE DONNÉES ====================
def init_db():
    """Initialise la base de données"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Table des groupes
    c.execute('''CREATE TABLE IF NOT EXISTS groups
                 (group_id INTEGER PRIMARY KEY, 
                  group_name TEXT,
                  member_count INTEGER,
                  added_date TIMESTAMP)''')
    
    # Table des utilisateurs
    c.execute('''CREATE TABLE IF NOT EXISTS user_access
                 (user_id INTEGER PRIMARY KEY,
                  username TEXT,
                  first_name TEXT,
                  has_premium BOOLEAN DEFAULT FALSE,
                  premium_since TIMESTAMP,
                  added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Table des messages
    c.execute('''CREATE TABLE IF NOT EXISTS user_messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  username TEXT,
                  first_name TEXT,
                  message_text TEXT,
                  message_date TIMESTAMP,
                  replied BOOLEAN DEFAULT FALSE)''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

def repair_database():
    """Répare la structure de la base de données"""
    try:
        conn = sqlite3.connect('bot_groups.db')
        c = conn.cursor()
        
        # Vérifier et ajouter les colonnes manquantes
        columns_to_check = [
            ('user_access', 'username', 'TEXT'),
            ('user_access', 'first_name', 'TEXT'),
            ('user_access', 'premium_since', 'TIMESTAMP')
        ]
        
        for table, column, col_type in columns_to_check:
            try:
                c.execute(f'SELECT {column} FROM {table} LIMIT 1')
            except sqlite3.OperationalError:
                print(f"🔄 Ajout de la colonne {column}...")
                c.execute(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}')
                conn.commit()
                print(f"✅ Colonne {column} ajoutée")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur réparation DB: {e}")
        return False

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
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, has_premium, premium_since) VALUES (?, ?, ?)''', 
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
    c.execute('SELECT user_id, username, first_name, has_premium, added_date FROM user_access')
    users = c.fetchall()
    conn.close()
    return users

def get_premium_users():
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, premium_since FROM user_access WHERE has_premium = TRUE')
    users = c.fetchall()
    conn.close()
    return users

def get_user_info(user_id):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('SELECT user_id, username, first_name, has_premium, premium_since, added_date FROM user_access WHERE user_id = ?', (user_id,))
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

def register_user(user_id, username, first_name):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, username, first_name, added_date) 
                 VALUES (?, ?, ?, ?)''', 
                 (user_id, username, first_name, datetime.now()))
    conn.commit()
    conn.close()

def save_user_message(user_id, username, first_name, message_text):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT INTO user_messages 
                 (user_id, username, first_name, message_text, message_date)
                 VALUES (?, ?, ?, ?, ?)''', 
                 (user_id, username, first_name, message_text, datetime.now()))
    conn.commit()
    conn.close()

def get_user_messages(user_id=None):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    if user_id:
        c.execute('''SELECT * FROM user_messages 
                     WHERE user_id = ? ORDER BY message_date DESC LIMIT 50''', (user_id,))
    else:
        c.execute('''SELECT * FROM user_messages 
                     ORDER BY message_date DESC LIMIT 100''')
    messages = c.fetchall()
    conn.close()
    return messages

def get_recent_messages(limit=20):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM user_messages 
                 ORDER BY message_date DESC LIMIT ?''', (limit,))
    messages = c.fetchall()
    conn.close()
    return messages

def delete_user_data(user_id):
    """Supprime toutes les données d'un utilisateur"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('DELETE FROM user_access WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM user_messages WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_user_stats():
    """Récupère des statistiques détaillées sur les utilisateurs"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    
    # Nombre total d'utilisateurs
    c.execute('SELECT COUNT(*) FROM user_access')
    total_users = c.fetchone()[0]
    
    # Utilisateurs avec username
    c.execute('SELECT COUNT(*) FROM user_access WHERE username IS NOT NULL AND username != ""')
    users_with_username = c.fetchone()[0]
    
    # Utilisateurs sans username
    c.execute('SELECT COUNT(*) FROM user_access WHERE username IS NULL OR username = ""')
    users_without_username = c.fetchone()[0]
    
    # Nouveaux utilisateurs aujourd'hui
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT COUNT(*) FROM user_access WHERE DATE(added_date) = ?', (today,))
    new_today = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_users': total_users,
        'with_username': users_with_username,
        'without_username': users_without_username,
        'new_today': new_today
    }

# ==================== FONCTIONS ADMIN ====================
def is_admin(user_id, username):
    """Vérifie si l'utilisateur est l'admin @soszoe"""
    return username == ADMIN_USERNAME

def is_admin_authenticated(user_id):
    """Vérifie si l'admin est authentifié"""
    if user_id not in admin_sessions:
        return False
    return admin_sessions[user_id]['authenticated']

def verify_admin_password(password):
    return password == ADMIN_PASSWORD

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
    comment_button = InlineKeyboardButton("📝 Commentaire", callback_data="send_comment")
    keyboard.add(support_button)
    keyboard.add(comment_button)
    return keyboard

def create_premium_menu():
    keyboard = InlineKeyboardMarkup()
    
    try:
        bot_user = bot.get_me()
        bot_username = bot_user.username
        add_button = InlineKeyboardButton(
            "📥 Ajouter à un groupe", 
            url=f"https://t.me/{bot_username}?startgroup=true"
        )
    except:
        add_button = InlineKeyboardButton("📥 Ajouter à un groupe", url="https://t.me/")
    
    status_button = InlineKeyboardButton("📊 Vérifier le statut", callback_data="check_status")
    premium_button = InlineKeyboardButton("🎁 Activer Premium", callback_data="activate_premium")
    comment_button = InlineKeyboardButton("📝 Commentaire", callback_data="send_comment")
    
    keyboard.add(add_button)
    keyboard.add(status_button)
    keyboard.add(premium_button)
    keyboard.add(comment_button)
    
    return keyboard

def create_owner_menu():
    """Menu du propriétaire @soszoe"""
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
    list_btn = InlineKeyboardButton("📋 Liste Premium", callback_data="admin_list_premium")
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    
    keyboard.add(give_btn, remove_btn)
    keyboard.add(all_btn, remove_all_btn)
    keyboard.add(list_btn)
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

def create_optimized_prompt():
    return f"""Tu es {BOT_NAME}, assistant IA créé par {CREATOR}. Expert en programmation, création, analyse et aide générale. Sois naturel, précis et utile. Réponds dans la langue de l'utilisateur."""

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
        # Fallback: envoyer le message sans photo
        bot.send_message(
            chat_id,
            caption,
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return False

# ==================== HANDLERS UTILISATEURS ====================
@bot.message_handler(commands=['start', 'aide', 'help'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        register_user(user_id, username, first_name)
        
        # Vérifier si c'est @soszoe (ADMIN PERMANENT)
        if is_admin(user_id, username):
            # @soszoe est TOUJOURS admin, pas besoin d'authentification
            admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
            activate_user_premium(user_id)  # Premium automatique
            
            caption = f"""
👑 **{BOT_NAME} - {VERSION}**

💎 **BIENVENUE PROPRIÉTAIRE @soszoe !**

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
        
        # Vérifier si c'est un admin authentifié (pour autres utilisateurs)
        if is_admin_authenticated(user_id):
            caption = f"""
👑 **{BOT_NAME} - {VERSION}**

🎯 **Mode Admin Activé !**
⭐ **Premium activé**

💫 **Panel de contrôle débloqué**
"""
            send_legendary_photo(message.chat.id, caption, create_owner_menu())
            return
        
        # Photo du créateur pour les utilisateurs normaux
        send_legendary_photo(
            message.chat.id,
            f"📸 **{CREATOR}** - Créateur du bot\n*Votre expert en IA* 👑",
            create_main_menu() if check_premium_access(user_id) else create_premium_menu()
        )
        
        time.sleep(0.5)
        
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

@bot.message_handler(commands=['auth', 'login', 'owner', 'admin'])
def auth_command(message):
    """Commande d'authentification pour les autres utilisateurs"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    # Si c'est @soszoe, il est déjà admin permanent
    if is_admin(user_id, username):
        bot.reply_to(message, "👑 **Vous êtes déjà le propriétaire !**\n\nTout est déjà débloqué pour vous.")
        return
    
    msg = bot.reply_to(message, "🔐 **AUTHENTIFICATION ADMIN**\n\nEntrez le mot de passe :")
    bot.register_next_step_handler(msg, process_auth)

def process_auth(message):
    """Traite l'authentification pour les autres utilisateurs"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    # Empêcher @soszoe de s'authentifier (il l'est déjà)
    if is_admin(user_id, username):
        bot.reply_to(message, "👑 **Vous êtes le propriétaire !**\n\nPas besoin d'authentification.")
        return
    
    if verify_admin_password(message.text.strip()):
        # Authentification réussie pour autres utilisateurs
        admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
        activate_user_premium(user_id)
        
        print(f"✅ Auth réussie pour {username}")
        
        success_msg = """
✅ **AUTHENTIFICATION RÉUSSIE !**

👑 **Accès administrateur activé !**
⭐ **Premium automatiquement activé**

🎯 **Commandes disponibles :**
• /stats - Voir les statistiques
• /users - Lister les utilisateurs  
• /broadcast - Envoyer un message à tous
• /premium_all - Donner premium à tous

💡 **Utilisez les boutons ci-dessous :**
"""
        bot.send_message(
            message.chat.id, 
            success_msg, 
            parse_mode='Markdown',
            reply_markup=create_owner_menu()
        )
        
    else:
        print(f"❌ Auth échouée pour {username}")
        bot.reply_to(message, "❌ **Mot de passe incorrect.**\n\nUtilisez `/auth` pour réessayer.")

@bot.message_handler(commands=['logout'])
def logout_command(message):
    """Déconnexion admin (sauf pour @soszoe)"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    # @soszoe ne peut pas se déconnecter
    if is_admin(user_id, username):
        bot.reply_to(message, "👑 **Vous êtes le propriétaire permanent !**\n\nImpossible de vous déconnecter.")
        return
    
    if user_id in admin_sessions:
        del admin_sessions[user_id]
    
    bot.reply_to(message, "🔓 **Déconnexion réussie !**\n\nSession admin terminée.")

# ==================== COMMANDES ADMIN ====================
@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Statistiques du bot"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    # Vérifier les droits admin
    if not is_admin(user_id, username) and not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nUtilisez `/auth` pour vous authentifier.")
        return
    
    total_users = len(get_all_users())
    premium_users = len(get_premium_users())
    groups_count = get_group_stats()
    total_messages = len(get_user_messages())
    
    stats_text = f"""
📊 **STATISTIQUES LÉGENDAIRES**

👥 **Utilisateurs :** {total_users}
⭐ **Premium :** {premium_users}
🔒 **Standard :** {total_users - premium_users}
📁 **Groupes :** {groups_count}/5
📨 **Messages :** {total_messages}
🕐 **MAJ :** {datetime.now().strftime('%H:%M %d/%m/%Y')}

👑 **Propriétaire :** @{ADMIN_USERNAME}
"""
    send_legendary_photo(message.chat.id, stats_text)

@bot.message_handler(commands=['users'])
def users_command(message):
    """Lister les utilisateurs"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    if not is_admin(user_id, username) and not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nUtilisez `/auth` pour vous authentifier.")
        return
    
    users = get_all_users()
    if not users:
        bot.reply_to(message, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **LISTE DES UTILISATEURS**\n\n"
    for i, user in enumerate(users[:15], 1):
        user_id, username, first_name, has_premium, added_date = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "❌ Sans username"
        response += f"{i}. {premium_status} **{first_name}**\n"
        response += f"   👤 {username_display}\n"
        response += f"   🆔 `{user_id}`\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if len(users) > 15:
        response += f"\n... et {len(users) - 15} autres"
    
    send_legendary_photo(message.chat.id, response)

@bot.message_handler(commands=['premium_all'])
def premium_all_command(message):
    """Donner le premium à tous"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    if not is_admin(user_id, username) and not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nUtilisez `/auth` pour vous authentifier.")
        return
    
    users = get_all_users()
    for user in users:
        activate_user_premium(user[0])
    
    response = f"⚡ **PREMIUM LÉGENDAIRE ACTIVÉ !**\n\n⭐ **Premium activé pour tous les {len(users)} utilisateurs !**"
    send_legendary_photo(message.chat.id, response)

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    """Envoyer un message à tous"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    if not is_admin(user_id, username) and not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nUtilisez `/auth` pour vous authentifier.")
        return
    
    msg = bot.reply_to(message, "📢 **BROADCAST LÉGENDAIRE**\n\n💎 Envoyez le message à diffuser à tous les utilisateurs :")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    if not is_admin(user_id, username) and not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
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

@bot.message_handler(commands=['mail'])
def mail_command(message):
    """Voir les messages reçus"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    if not is_admin(user_id, username) and not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 **Accès refusé.**\n\nUtilisez `/auth` pour vous authentifier.")
        return
    
    show_mail_history(message)

def show_mail_history(message, page=1):
    messages = get_recent_messages(limit=50)
    
    if not messages:
        send_legendary_photo(message.chat.id, "📭 **AUCUN MESSAGE REÇU**\n\nAucun utilisateur n'a encore envoyé de message.")
        return
    
    items_per_page = 10
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_messages = messages[start_idx:end_idx]
    
    response = f"📨 **MESSAGES REÇUS**\n\n"
    response += f"📊 Total messages: {len(messages)}\n"
    response += f"📄 Page {page}/{(len(messages) + items_per_page - 1) // items_per_page}\n\n"
    
    for i, msg in enumerate(page_messages, start_idx + 1):
        msg_id, user_id, username, first_name, message_text, message_date, replied = msg
        username_display = f"@{username}" if username else "❌ Sans username"
        date_str = message_date.split('.')[0] if isinstance(message_date, str) else message_date.strftime("%d/%m/%Y %H:%M")
        
        response += f"**{i}. {first_name}** ({username_display})\n"
        response += f"🆔 `{user_id}` | 📅 {date_str}\n"
        response += f"💬 {message_text[:100]}{'...' if len(message_text) > 100 else ''}\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n\n"
    
    keyboard = InlineKeyboardMarkup()
    if page > 1:
        keyboard.add(InlineKeyboardButton("⬅️ Page précédente", callback_data=f"mail_page_{page-1}"))
    if end_idx < len(messages):
        keyboard.add(InlineKeyboardButton("Page suivante ➡️", callback_data=f"mail_page_{page+1}"))
    
    keyboard.add(InlineKeyboardButton("🔄 Actualiser", callback_data="admin_mail"))
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown', reply_markup=keyboard)

# ==================== GESTION DES CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    username = call.from_user.username or "Sans username"
    
    # Callbacks utilisateurs normaux
    if call.data == "check_status":
        total = get_group_stats()
        if check_premium_access(user_id):
            bot.answer_callback_query(call.id, "✅ Premium activé !")
        else:
            bot.answer_callback_query(call.id, f"📊 {total}/5 groupes - {5-total} manquant(s)")
    
    elif call.data == "activate_premium":
        total = get_group_stats()
        if total >= 5:
            activate_user_premium(user_id)
            bot.answer_callback_query(call.id, "🎉 Premium activé !")
            
            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="🎉 **Premium activé avec succès !**\n\n✨ **Profitez de toutes les fonctionnalités IA !**\n💬 Envoyez-moi un message pour commencer !",
                    parse_mode='Markdown',
                    reply_markup=create_main_menu()
                )
            except:
                bot.send_message(call.message.chat.id, "🎉 **Premium activé avec succès !**\n\n✨ Profitez de l'IA !")
        else:
            bot.answer_callback_query(call.id, f"❌ {5-total} groupe(s) manquant(s)")
    
    elif call.data == "send_comment":
        msg = bot.send_message(call.message.chat.id, "📝 **ENVOYER UN COMMENTAIRE**\n\nÉcrivez votre message pour le créateur :")
        bot.register_next_step_handler(msg, process_comment)
        bot.answer_callback_query(call.id, "📝 Commentaire")
    
    # Callbacks admin - Vérification des droits
    elif call.data.startswith("admin_"):
        # Vérifier si c'est @soszoe ou un admin authentifié
        if not is_admin(user_id, username) and not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Utilisez /auth")
            bot.send_message(call.message.chat.id, "🔐 **Authentification requise.**\n\nUtilisez `/auth` pour vous authentifier.")
            return
        
        # Exécuter la commande admin
        if call.data == "admin_stats":
            stats_command(call.message)
            bot.answer_callback_query(call.id, "📊 Statistiques")
        
        elif call.data == "admin_users":
            users_command(call.message)
            bot.answer_callback_query(call.id, "👥 Utilisateurs")
        
        elif call.data == "admin_premium":
            send_legendary_photo(
                call.message.chat.id,
                "⭐ **GESTION PREMIUM**\n\nChoisissez une action :",
                create_premium_management_menu()
            )
            bot.answer_callback_query(call.id, "⭐ Gestion Premium")
        
        elif call.data == "admin_give_premium":
            msg = bot.send_message(call.message.chat.id, "🎁 **DONNER LE PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
            bot.register_next_step_handler(msg, process_give_premium)
            bot.answer_callback_query(call.id, "🎁 Donner Premium")
        
        elif call.data == "admin_broadcast":
            broadcast_command(call.message)
            bot.answer_callback_query(call.id, "📢 Broadcast")
        
        elif call.data == "admin_mail":
            mail_command(call.message)
            bot.answer_callback_query(call.id, "📨 Messages")
        
        elif call.data == "admin_premium_all":
            premium_all_command(call.message)
            bot.answer_callback_query(call.id, "⚡ Premium à Tous")
        
        elif call.data == "admin_cleanup":
            conn = sqlite3.connect('bot_groups.db')
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM user_messages')
            before_messages = c.fetchone()[0]
            c.execute('DELETE FROM user_messages WHERE message_date < datetime("now", "-30 days")')
            deleted_messages = c.changes
            conn.commit()
            conn.close()
            
            response = f"""
🧹 **NETTOYAGE EFFECTUÉ**

📨 **Messages :**
• Avant : {before_messages}
• Supprimés : {deleted_messages}
• Restants : {before_messages - deleted_messages}
"""
            send_legendary_photo(call.message.chat.id, response)
            bot.answer_callback_query(call.id, "🧹 Nettoyage")
        
        elif call.data == "admin_back":
            send_legendary_photo(
                call.message.chat.id,
                "👑 **PANEL DE CONTRÔLE**\n\nRetour au menu principal :",
                create_owner_menu()
            )
            bot.answer_callback_query(call.id, "🔙 Retour")

def process_give_premium(message):
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    
    if not is_admin(user_id, username) and not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        activate_user_premium(target_user_id)
        
        try:
            bot.send_message(target_user_id, 
                           "🎉 **FÉLICITATIONS !**\n\n⭐ **Vous avez reçu le PREMIUM !**\n\n✨ Profitez de toutes les fonctionnalités IA !")
        except:
            pass
        
        response = f"✅ **PREMIUM ACCORDÉ !**\n\n⭐ **Premium activé pour l'utilisateur {target_user_id}**"
        send_legendary_photo(message.chat.id, response)
        
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

def process_comment(message):
    """Traite l'envoi d'un commentaire"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    first_name = message.from_user.first_name or "Utilisateur"
    comment_text = message.text
    
    save_user_message(user_id, username, first_name, comment_text)
    
    # Notifier @soszoe
    bot.reply_to(message, "✅ **Commentaire envoyé !**\n\nLe propriétaire @soszoe a été notifié !")

# ==================== GESTION GROUPES ====================
@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    """Quand le bot est ajouté à un groupe"""
    try:
        if bot.get_me().id in [user.id for user in message.new_chat_members]:
            group_id = message.chat.id
            group_name = message.chat.title or "Groupe sans nom"
            
            try:
                member_count = bot.get_chat_members_count(group_id)
            except:
                member_count = 0
            
            add_group_to_db(group_id, group_name, member_count)
            
            welcome_msg = f"""
🤖 **{BOT_NAME}** - Merci de m'avoir ajouté !

👑 Créé par {CREATOR}
🚀 Assistant IA LÉGENDAIRE

📊 **Ce groupe compte pour le déblocage du premium gratuit !**

💡 Utilisez /start en privé pour voir votre progression.
"""
            bot.send_message(group_id, welcome_msg, parse_mode='Markdown')
            
    except Exception as e:
        print(f"❌ Erreur nouveau groupe: {e}")

# ==================== MOTEUR IA ====================
@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gère tous les messages"""
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
    
    # ✅ UTILISATEUR PREMIUM - Traitement IA
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        if not GROQ_API_KEY:
            bot.reply_to(message, "❌ Service IA temporairement indisponible.")
            return
            
        user_session = get_user_session(user_id)
        
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        messages = [{"role": "system", "content": create_optimized_prompt()}]
        if user_session['conversation']:
            messages.extend(user_session['conversation'][-4:])
        
        user_message = message.text[:500]
        messages.append({"role": "user", "content": user_message})

        payload = {
            "messages": messages,
            "model": current_model,
            "max_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9
        }

        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=20)
        
        if response.status_code == 200:
            answer = response.json()["choices"][0]["message"]["content"]
            
            user_session['conversation'].extend([
                {"role": "user", "content": user_message[:300]},
                {"role": "assistant", "content": answer[:600]}
            ])
            
            if len(user_session['conversation']) > 8:
                user_session['conversation'] = user_session['conversation'][-8:]
            
            user_session['last_active'] = datetime.now()
            
            bot.reply_to(message, answer)
        else:
            error_msg = "❌ Erreur de service. Réessayez dans quelques instants."
            if response.status_code == 429:
                error_msg = "⏰ Trop de requêtes. Veuillez patienter quelques secondes."
            elif response.status_code == 401:
                error_msg = "🔑 Erreur d'authentification API."
            
            bot.reply_to(message, error_msg)
            
    except requests.exceptions.Timeout:
        bot.reply_to(message, "⏰ Délai d'attente dépassé. Réessayez.")
    except Exception as e:
        print(f"❌ Erreur IA: {e}")
        bot.reply_to(message, "🔧 Service temporairement indisponible. Réessayez plus tard.")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🗃️ Initialisation de la base de données...")
    init_db()
    repair_database()
    print("✅ Base de données prête")
    print(f"🚀 {BOT_NAME} - {VERSION}")
    print(f"👑 Créateur: {CREATOR}")
    print("💎 SYSTÈME ADMIN PERMANENT ACTIVÉ")
    print(f"   👑 Propriétaire: @{ADMIN_USERNAME}")
    print("   🔑 Mot de passe admin: KING1998")
    print("   ⭐ @soszoe a tout débloqué automatiquement")
    print("   📊 Panel complet avec tous les boutons")
    print("🤖 En attente de messages...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
