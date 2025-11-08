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
VERSION = "💎 Édition version 1.0 Optimisée"
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
current_model = "llama-3.1-8b-instant"

# 🔐 ADMIN
ADMIN_ID = 7908680781
ADMIN_USERNAME = "@soszoe"
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
    
    # Table des logs d'actions admin
    c.execute('''CREATE TABLE IF NOT EXISTS admin_logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  admin_id INTEGER,
                  action TEXT,
                  target_user_id INTEGER,
                  details TEXT,
                  log_date TIMESTAMP)''')
    
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

def log_admin_action(admin_id, action, target_user_id=None, details=""):
    """Log les actions admin"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT INTO admin_logs 
                 (admin_id, action, target_user_id, details, log_date)
                 VALUES (?, ?, ?, ?, ?)''', 
                 (admin_id, action, target_user_id, details, datetime.now()))
    conn.commit()
    conn.close()

def get_admin_logs(limit=50):
    """Récupère les logs admin"""
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''SELECT * FROM admin_logs 
                 ORDER BY log_date DESC LIMIT ?''', (limit,))
    logs = c.fetchall()
    conn.close()
    return logs

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

def create_admin_menu(user_id=None):
    keyboard = InlineKeyboardMarkup()
    
    if user_id and is_admin_authenticated(user_id):
        stats_btn = InlineKeyboardButton("📊 Statistiques", callback_data="admin_stats")
        users_btn = InlineKeyboardButton("👥 Utilisateurs", callback_data="admin_users")
        premium_btn = InlineKeyboardButton("⭐ Gérer Premium", callback_data="admin_premium")
        broadcast_btn = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
        mail_btn = InlineKeyboardButton("📨 Mail Historique", callback_data="admin_mail")
        commands_btn = InlineKeyboardButton("🛠️ Commandes", callback_data="admin_commands")
        logs_btn = InlineKeyboardButton("📋 Logs Admin", callback_data="admin_logs")
        advanced_btn = InlineKeyboardButton("⚙️ Avancé", callback_data="admin_advanced")
        help_btn = InlineKeyboardButton("❓ Aide Admin", callback_data="admin_help")
        
        keyboard.add(stats_btn, users_btn)
        keyboard.add(premium_btn, broadcast_btn)
        keyboard.add(mail_btn, logs_btn)
        keyboard.add(commands_btn, advanced_btn)
        keyboard.add(help_btn)
    else:
        auth_btn = InlineKeyboardButton("🔐 Authentification Admin", callback_data="admin_auth")
        keyboard.add(auth_btn)
    
    return keyboard

def create_advanced_admin_menu():
    """Menu admin avancé"""
    keyboard = InlineKeyboardMarkup()
    
    delete_user_btn = InlineKeyboardButton("🗑️ Supprimer Utilisateur", callback_data="admin_delete_user")
    user_stats_btn = InlineKeyboardButton("📈 Stats Détaillées", callback_data="admin_user_stats")
    export_btn = InlineKeyboardButton("📤 Exporter Données", callback_data="admin_export")
    cleanup_btn = InlineKeyboardButton("🧹 Nettoyage", callback_data="admin_cleanup")
    system_btn = InlineKeyboardButton("🖥️ Système", callback_data="admin_system")
    search_btn = InlineKeyboardButton("🔍 Rechercher User", callback_data="admin_search_user")
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    
    keyboard.add(delete_user_btn, user_stats_btn)
    keyboard.add(export_btn, cleanup_btn)
    keyboard.add(system_btn, search_btn)
    keyboard.add(back_btn)
    
    return keyboard

def create_optimized_prompt():
    return f"""Tu es {BOT_NAME}, assistant IA créé par {CREATOR}. Expert en programmation, création, analyse et aide générale. Sois naturel, précis et utile. Réponds dans la langue de l'utilisateur."""

# ==================== HANDLERS UTILISATEURS ====================
@bot.message_handler(commands=['start', 'aide', 'help'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        register_user(user_id, username, first_name)
        
        if is_admin(user_id):
            activate_user_premium(user_id)
            
            if is_admin_authenticated(user_id):
                menu_text = "👑 **Mode Propriétaire Activé**\n\n⭐ **Premium activé pour vous !**\n🔓 **Session admin active** - Accès complet débloqué !"
            else:
                menu_text = "👑 **Mode Propriétaire Activé**\n\n⭐ **Premium activé pour vous !**\n🔐 **Authentification requise** - Cliquez sur 'Auth' pour débloquer le panel admin."
            
            bot.send_message(
                message.chat.id,
                menu_text,
                reply_markup=create_admin_menu(user_id),
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
    """Commande test"""
    bot.reply_to(message, "✅ **Bot actif !**\n🚀 Fonctionne parfaitement !")

@bot.message_handler(commands=['reset'])
def reset_handler(message):
    """Réinitialise la conversation"""
    user_id = message.from_user.id
    if user_id in user_sessions:
        user_sessions[user_id]['conversation'] = []
    bot.reply_to(message, "🔄 **Conversation réinitialisée !**\nNouveau départ !")

@bot.message_handler(commands=['status'])
def status_handler(message):
    """Vérifie le statut"""
    user_id = message.from_user.id
    total = get_group_stats()
    
    if check_premium_access(user_id):
        bot.reply_to(message, "⭐ **Statut : PREMIUM ACTIVÉ**\n✨ Profitez de l'IA complète !")
    else:
        bot.reply_to(message, 
                   f"🔒 **Statut : VERSION LIMITÉE**\n\n{get_progress_bar()}\n\nAjoutez le bot à {5-total} groupe(s) pour débloquer le premium.",
                   reply_markup=create_premium_menu())

@bot.message_handler(commands=['commentaire', 'comment'])
def comment_command(message):
    """Commande pour envoyer un commentaire au créateur"""
    msg = bot.reply_to(message, "📝 **ENVOYER UN COMMENTAIRE**\n\nÉcrivez votre message pour le créateur :")
    bot.register_next_step_handler(msg, process_comment)

def process_comment(message):
    """Traite l'envoi d'un commentaire"""
    user_id = message.from_user.id
    username = message.from_user.username or "Sans username"
    first_name = message.from_user.first_name or "Utilisateur"
    comment_text = message.text
    
    # Sauvegarder le message dans la base de données
    save_user_message(user_id, username, first_name, comment_text)
    
    # Notifier l'admin
    try:
        admin_message = f"📨 **NOUVEAU COMMENTAIRE**\n\n👤 De: {first_name} (@{username})\n🆔 ID: `{user_id}`\n💬 Message:\n{comment_text}"
        bot.send_message(ADMIN_ID, admin_message, parse_mode='Markdown')
    except Exception as e:
        print(f"❌ Erreur envoi admin: {e}")
    
    bot.reply_to(message, "✅ **Commentaire envoyé !**\n\nMerci pour votre feedback ! Le créateur le recevra rapidement.")

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
🚀 Assistant IA optimisé

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

# ==================== DÉCORATEUR AUTH ====================
def require_admin_auth(func):
    """Décorateur pour exiger l'authentification admin"""
    def wrapper(message):
        user_id = message.from_user.id
        if not is_admin(user_id):
            bot.reply_to(message, "❌ Accès réservé au propriétaire.")
            return
        
        if not is_admin_authenticated(user_id):
            msg = bot.reply_to(message, "🔐 **Authentification requise**\n\nVeuillez entrer le mot de passe admin :")
            bot.register_next_step_handler(msg, process_admin_auth_for_command, func, message)
            return
        
        func(message)
    
    return wrapper

def process_admin_auth_for_command(message, original_func, original_message):
    """Traite l'authentification pour une commande spécifique"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if verify_admin_password(message.text.strip()):
        admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
        bot.send_message(message.chat.id, "✅ **Authentification réussie !**")
        original_func(original_message)
    else:
        bot.reply_to(message, "❌ **Mot de passe incorrect.**\n\nUtilisez à nouveau la commande admin.")

# ==================== COMMANDES ADMIN ====================
@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Panel admin principal"""
    user_id = message.from_user.id
    if not is_admin(user_id):
        bot.reply_to(message, "❌ Accès réservé au propriétaire.")
        return
    
    bot.send_message(
        message.chat.id,
        "👑 **Panel Administrateur**\n\nSélectionnez une option :",
        reply_markup=create_admin_menu(user_id),
        parse_mode='Markdown'
    )

@bot.message_handler(commands=['stats'])
@require_admin_auth
def stats_command(message):
    """Statistiques du bot"""
    total_users = len(get_all_users())
    premium_users = len(get_premium_users())
    groups_count = get_group_stats()
    total_messages = len(get_user_messages())
    
    stats_text = f"""
📊 **STATISTIQUES DU BOT**

👥 **Utilisateurs :**
• Total : {total_users}
• Premium : {premium_users}
• Standard : {total_users - premium_users}
• Taux premium : {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%

📁 **Groupes :** {groups_count}/5
📨 **Messages reçus :** {total_messages}
🕐 **Dernière MAJ :** {datetime.now().strftime('%H:%M %d/%m/%Y')}

👑 **Admin :** {CREATOR}
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['users'])
@require_admin_auth
def users_command(message):
    """Lister tous les utilisateurs"""
    users = get_all_users()
    if not users:
        bot.reply_to(message, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **LISTE DES UTILISATEURS**\n\n"
    for i, user in enumerate(users[:20], 1):
        user_id, username, first_name, has_premium, added_date = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "❌ Sans username"
        response += f"{i}. {premium_status} **{first_name}**\n"
        response += f"   👤 {username_display}\n"
        response += f"   🆔 `{user_id}`\n"
        response += f"   📅 {added_date.split()[0] if isinstance(added_date, str) else added_date.strftime('%d/%m/%Y')}\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if len(users) > 20:
        response += f"\n... et {len(users) - 20} autres utilisateurs"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['premium_users'])
@require_admin_auth
def premium_users_command(message):
    """Lister les utilisateurs premium"""
    premium_users = get_premium_users()
    if not premium_users:
        bot.reply_to(message, "⭐ Aucun utilisateur premium.")
        return
    
    response = "⭐ **UTILISATEURS PREMIUM**\n\n"
    for i, user in enumerate(premium_users, 1):
        user_id, username, first_name, premium_since = user
        username_display = f"@{username}" if username else "❌ Sans username"
        since = premium_since.split()[0] if isinstance(premium_since, str) else premium_since.strftime("%d/%m/%Y")
        response += f"{i}. **{first_name}**\n"
        response += f"   👤 {username_display}\n"
        response += f"   🆔 `{user_id}`\n"
        response += f"   ⭐ Depuis: {since}\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['give_premium'])
@require_admin_auth
def give_premium_command(message):
    """Donner le premium à un utilisateur"""
    msg = bot.reply_to(message, "⭐ **DONNER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_give_premium)

def process_give_premium(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        activate_user_premium(target_user_id)
        
        # Logger l'action
        log_admin_action(user_id, "GIVE_PREMIUM", target_user_id, "Premium accordé manuellement")
        
        try:
            bot.send_message(target_user_id, 
                           "🎉 **FÉLICITATIONS !**\n\n⭐ **Premium activé !**\n\n✨ Profitez de toutes les fonctionnalités IA !\n💬 Envoyez-moi un message pour commencer !")
        except:
            pass
        
        bot.reply_to(message, f"✅ **Premium accordé à l'utilisateur {target_user_id}**")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['remove_premium'])
@require_admin_auth
def remove_premium_command(message):
    """Retirer le premium à un utilisateur"""
    msg = bot.reply_to(message, "🔒 **RETIRER PREMIUM**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_remove_premium)

def process_remove_premium(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        deactivate_user_premium(target_user_id)
        
        # Logger l'action
        log_admin_action(user_id, "REMOVE_PREMIUM", target_user_id, "Premium retiré manuellement")
        
        bot.reply_to(message, f"✅ **Premium retiré à l'utilisateur {target_user_id}**")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['user_info'])
@require_admin_auth
def user_info_command(message):
    """Informations sur un utilisateur"""
    msg = bot.reply_to(message, "🔍 **INFORMATIONS UTILISATEUR**\n\nEnvoyez l'ID de l'utilisateur :")
    bot.register_next_step_handler(msg, process_user_info)

def process_user_info(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        user_info = get_user_info(target_user_id)
        
        if user_info:
            user_id, username, first_name, has_premium, premium_since, added_date = user_info
            premium_status = "⭐ PREMIUM" if has_premium else "🔒 STANDARD"
            since = premium_since.strftime("%d/%m/%Y %H:%M") if premium_since else "Non premium"
            username_display = f"@{username}" if username else "❌ Sans username"
            
            user_messages = get_user_messages(target_user_id)
            
            response = f"""
👤 **INFORMATIONS UTILISATEUR**

🆔 ID: `{user_id}`
📛 Nom: {first_name}
👤 Username: {username_display}
🎯 Statut: {premium_status}
📅 Premium depuis: {since}
📅 Inscrit le: {added_date.strftime("%d/%m/%Y %H:%M")}
📨 Messages envoyés: {len(user_messages)}
"""
            bot.reply_to(message, response, parse_mode='Markdown')
        else:
            bot.reply_to(message, "❌ Utilisateur non trouvé.")
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['broadcast'])
@require_admin_auth
def broadcast_command(message):
    """Envoyer un message à tous les utilisateurs"""
    msg = bot.reply_to(message, "📢 **BROADCAST**\n\nEnvoyez le message à diffuser :")
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
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
    
    # Logger l'action
    log_admin_action(user_id, "BROADCAST", None, f"Message envoyé à {success_count}/{total_users} utilisateurs")

@bot.message_handler(commands=['mail'])
@require_admin_auth
def mail_command(message):
    """Commande pour voir l'historique des messages"""
    show_mail_history(message)

def show_mail_history(message, page=1):
    messages = get_recent_messages(limit=50)
    
    if not messages:
        bot.reply_to(message, "📭 **Aucun message reçu**\n\nAucun utilisateur n'a encore envoyé de commentaire.")
        return
    
    items_per_page = 10
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_messages = messages[start_idx:end_idx]
    
    response = f"📨 **HISTORIQUE DES MESSAGES**\n\n"
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

@bot.message_handler(commands=['premium_all'])
@require_admin_auth
def premium_all_command(message):
    """Activer le premium pour tous"""
    users = get_all_users()
    for user in users:
        activate_user_premium(user[0])
    
    # Logger l'action
    log_admin_action(message.from_user.id, "PREMIUM_ALL", None, f"Premium activé pour {len(users)} utilisateurs")
    
    bot.reply_to(message, f"⭐ **Premium activé pour tous les {len(users)} utilisateurs !**")

@bot.message_handler(commands=['remove_all_premium'])
@require_admin_auth
def remove_all_premium_command(message):
    """Retirer le premium à tous (sauf admin)"""
    users = get_all_users()
    count = 0
    for user in users:
        if user[0] != ADMIN_ID:
            deactivate_user_premium(user[0])
            count += 1
    
    # Logger l'action
    log_admin_action(message.from_user.id, "REMOVE_ALL_PREMIUM", None, f"Premium retiré pour {count} utilisateurs")
    
    bot.reply_to(message, f"🔒 **Premium retiré à {count} utilisateurs !**")

@bot.message_handler(commands=['commands', 'cmd'])
@require_admin_auth
def admin_commands_command(message):
    """Affiche toutes les commandes admin"""
    commands_text = """
🛠️ **TOUTES LES COMMANDES ADMIN**

📊 **STATISTIQUES :**
`/stats` - Statistiques complètes du bot
`/users` - Liste tous les utilisateurs
`/premium_users` - Liste les utilisateurs premium
`/user_stats` - Statistiques détaillées utilisateurs

👤 **GESTION UTILISATEURS :**
`/user_info` - Infos détaillées sur un utilisateur
`/mail` - Historique des messages reçus
`/search_user` - Rechercher un utilisateur

⭐ **GESTION PREMIUM :**
`/give_premium` - Donner premium à un utilisateur
`/remove_premium` - Retirer premium à un utilisateur
`/premium_all` - Premium pour TOUS les utilisateurs
`/remove_all_premium` - Retirer premium à tous (sauf vous)

📢 **COMMUNICATION :**
`/broadcast` - Envoyer un message à tous

🔧 **UTILITAIRES AVANCÉS :**
`/admin` - Panel d'authentification
`/commands` - Ce menu des commandes
`/logs` - Voir les logs admin
`/cleanup` - Nettoyer la base de données
`/system` - Informations système
`/delete_user` - Supprimer un utilisateur

💡 **ASTUCE :** Utilisez le panel `/admin` pour une navigation facile !
"""
    
    bot.reply_to(message, commands_text, parse_mode='Markdown')

# ==================== NOUVELLES COMMANDES ADMIN ====================
@bot.message_handler(commands=['logs'])
@require_admin_auth
def logs_command(message):
    """Affiche les logs admin"""
    logs = get_admin_logs(limit=30)
    
    if not logs:
        bot.reply_to(message, "📋 **Aucun log admin trouvé**")
        return
    
    response = "📋 **LOGS ADMINISTRATEUR**\n\n"
    
    for log in logs[:20]:
        log_id, admin_id, action, target_user_id, details, log_date = log
        date_str = log_date.split('.')[0] if isinstance(log_date, str) else log_date.strftime("%d/%m %H:%M")
        
        response += f"**{action}** - {date_str}\n"
        if target_user_id:
            response += f"👤 Cible: `{target_user_id}`\n"
        if details:
            response += f"📝 {details[:50]}{'...' if len(details) > 50 else ''}\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n"
    
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['user_stats'])
@require_admin_auth
def user_stats_command(message):
    """Statistiques détaillées des utilisateurs"""
    stats = get_user_stats()
    total_users = len(get_all_users())
    premium_users = len(get_premium_users())
    groups_count = get_group_stats()
    
    response = f"""
📈 **STATISTIQUES DÉTAILLÉES UTILISATEURS**

👥 **Utilisateurs :**
• Total : {stats['total_users']}
• Premium : {premium_users}
• Standard : {total_users - premium_users}
• Avec username : {stats['with_username']}
• Sans username : {stats['without_username']}
• Nouveaux aujourd'hui : {stats['new_today']}

📊 **Pourcentages :**
• Taux premium : {(premium_users/total_users*100) if total_users > 0 else 0:.1f}%
• Avec username : {(stats['with_username']/total_users*100) if total_users > 0 else 0:.1f}%

📁 **Groupes :** {groups_count}/5
📨 **Messages reçus :** {len(get_user_messages())}
"""
    bot.reply_to(message, response, parse_mode='Markdown')

@bot.message_handler(commands=['delete_user'])
@require_admin_auth
def delete_user_command(message):
    """Supprimer un utilisateur et ses données"""
    msg = bot.reply_to(message, "🗑️ **SUPPRIMER UTILISATEUR**\n\nEnvoyez l'ID de l'utilisateur à supprimer :")
    bot.register_next_step_handler(msg, process_delete_user)

def process_delete_user(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    try:
        target_user_id = int(message.text.strip())
        
        user_info = get_user_info(target_user_id)
        if not user_info:
            bot.reply_to(message, "❌ Utilisateur non trouvé.")
            return
        
        delete_user_data(target_user_id)
        
        log_admin_action(user_id, "DELETE_USER", target_user_id, f"Suppression utilisateur {target_user_id}")
        
        bot.reply_to(message, f"✅ **Utilisateur {target_user_id} supprimé !**\n\nToutes ses données ont été effacées.")
        
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")

@bot.message_handler(commands=['cleanup'])
@require_admin_auth
def cleanup_command(message):
    """Nettoyage de la base de données"""
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

✅ Base de données optimisée
"""
    bot.reply_to(message, response, parse_mode='Markdown')
    
    log_admin_action(message.from_user.id, "CLEANUP", None, f"Supprimé {deleted_messages} messages")

@bot.message_handler(commands=['system'])
@require_admin_auth
def system_command(message):
    """Informations système"""
    import psutil
    import platform
    
    system_info = f"""
🖥️ **INFORMATIONS SYSTÈME**

💻 **Système :**
• OS : {platform.system()} {platform.release()}
• Processeur : {platform.processor()}
• Architecture : {platform.architecture()[0]}

📊 **Utilisation :**
• CPU : {psutil.cpu_percent()}%
• RAM : {psutil.virtual_memory().percent}%
• Disk : {psutil.disk_usage('/').percent}%

🤖 **Bot :**
• Utilisateurs : {len(get_all_users())}
• Groupes : {get_group_stats()}
• Messages : {len(get_user_messages())}
• Version : {VERSION}
"""
    bot.reply_to(message, system_info, parse_mode='Markdown')

@bot.message_handler(commands=['search_user'])
@require_admin_auth
def search_user_command(message):
    """Rechercher un utilisateur par username ou nom"""
    msg = bot.reply_to(message, "🔍 **RECHERCHER UTILISATEUR**\n\nEnvoyez le username, nom ou ID à rechercher :")
    bot.register_next_step_handler(msg, process_search_user)

def process_search_user(message):
    user_id = message.from_user.id
    if not is_admin(user_id) or not is_admin_authenticated(user_id):
        bot.reply_to(message, "🔐 Authentification requise.")
        return
    
    search_term = message.text.strip().lower()
    users = get_all_users()
    
    results = []
    for user in users:
        user_id, username, first_name, has_premium, added_date = user
        
        if (username and search_term in username.lower()) or \
           (first_name and search_term in first_name.lower()) or \
           search_term == str(user_id):
            results.append(user)
    
    if not results:
        bot.reply_to(message, f"❌ Aucun utilisateur trouvé pour : {search_term}")
        return
    
    response = f"🔍 **RÉSULTATS DE RECHERCHE**\n\nTerme : `{search_term}`\nTrouvé(s) : {len(results)}\n\n"
    
    for i, user in enumerate(results[:10], 1):
        user_id, username, first_name, has_premium, added_date = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "❌ Sans username"
        date_str = added_date.split()[0] if isinstance(added_date, str) else added_date.strftime("%d/%m/%Y")
        
        response += f"{i}. {premium_status} **{first_name}**\n"
        response += f"   👤 {username_display}\n"
        response += f"   🆔 `{user_id}`\n"
        response += f"   📅 {date_str}\n"
        response += "━━━━━━━━━━━━━━━━━━━━\n"
    
    if len(results) > 10:
        response += f"\n... et {len(results) - 10} autres résultats"
    
    bot.reply_to(message, response, parse_mode='Markdown')

# ==================== CALLBACKS COMPLETS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
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
    
    elif call.data == "admin_auth":
        if not is_admin(user_id):
            bot.answer_callback_query(call.id, "❌ Accès réservé")
            return
        
        msg = bot.send_message(call.message.chat.id, "🔐 **AUTHENTIFICATION ADMIN**\n\nVeuillez entrer le mot de passe :")
        bot.register_next_step_handler(msg, process_admin_auth_callback, call.message)
        bot.answer_callback_query(call.id, "🔐 Authentification")
    
    elif call.data == "admin_stats":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        stats_command(call.message)
        bot.answer_callback_query(call.id, "📊 Statistiques")
    
    elif call.data == "admin_users":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        users_command(call.message)
        bot.answer_callback_query(call.id, "👥 Utilisateurs")
    
    elif call.data == "admin_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        keyboard = InlineKeyboardMarkup()
        give_btn = InlineKeyboardButton("➕ Donner Premium", callback_data="admin_give_premium")
        remove_btn = InlineKeyboardButton("➖ Retirer Premium", callback_data="admin_remove_premium")
        all_btn = InlineKeyboardButton("⭐ À Tous", callback_data="admin_premium_all")
        remove_all_btn = InlineKeyboardButton("🔒 Retirer à Tous", callback_data="admin_remove_all_premium")
        
        keyboard.add(give_btn, remove_btn)
        keyboard.add(all_btn, remove_all_btn)
        
        bot.answer_callback_query(call.id, "⭐ Gestion Premium")
        bot.send_message(call.message.chat.id, "⭐ **GESTION PREMIUM**", reply_markup=keyboard)
    
    elif call.data == "admin_broadcast":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        broadcast_command(call.message)
        bot.answer_callback_query(call.id, "📢 Broadcast")
    
    elif call.data == "admin_mail":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        mail_command(call.message)
        bot.answer_callback_query(call.id, "📨 Mail Historique")
    
    elif call.data == "admin_commands":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        admin_commands_command(call.message)
        bot.answer_callback_query(call.id, "🛠️ Commandes")
    
    elif call.data == "admin_logs":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        logs_command(call.message)
        bot.answer_callback_query(call.id, "📋 Logs Admin")
    
    elif call.data == "admin_user_stats":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        user_stats_command(call.message)
        bot.answer_callback_query(call.id, "📈 Stats Utilisateurs")
    
    elif call.data == "admin_advanced":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        bot.send_message(
            call.message.chat.id,
            "⚙️ **MENU ADMIN AVANCÉ**\n\nOutils de gestion avancée :",
            reply_markup=create_advanced_admin_menu(),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "⚙️ Menu Avancé")
    
    elif call.data == "admin_delete_user":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        delete_user_command(call.message)
        bot.answer_callback_query(call.id, "🗑️ Supprimer Utilisateur")
    
    elif call.data == "admin_cleanup":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        cleanup_command(call.message)
        bot.answer_callback_query(call.id, "🧹 Nettoyage")
    
    elif call.data == "admin_system":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        system_command(call.message)
        bot.answer_callback_query(call.id, "🖥️ Système")
    
    elif call.data == "admin_search_user":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        search_user_command(call.message)
        bot.answer_callback_query(call.id, "🔍 Rechercher User")
    
    elif call.data == "admin_export":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        users = get_all_users()
        export_text = "📊 **EXPORT UTILISATEURS**\n\n"
        
        for user in users[:50]:
            user_id, username, first_name, has_premium, added_date = user
            status = "PREMIUM" if has_premium else "STANDARD"
            username_display = f"@{username}" if username else "SANS_USERNAME"
            export_text += f"{user_id},{username_display},{first_name},{status},{added_date}\n"
        
        bot.send_message(call.message.chat.id, f"```\n{export_text}\n```", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "📤 Données exportées")
    
    elif call.data == "admin_give_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        give_premium_command(call.message)
        bot.answer_callback_query(call.id, "➕ Donner Premium")
    
    elif call.data == "admin_remove_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        remove_premium_command(call.message)
        bot.answer_callback_query(call.id, "➖ Retirer Premium")
    
    elif call.data == "admin_premium_all":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        premium_all_command(call.message)
        bot.answer_callback_query(call.id, "✅ Premium à tous")
    
    elif call.data == "admin_remove_all_premium":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        remove_all_premium_command(call.message)
        bot.answer_callback_query(call.id, "🔒 Premium retiré")
    
    elif call.data == "admin_help":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        help_text = """
❓ **AIDE ADMINISTRATEUR**

💡 **Conseils d'utilisation :**

🔐 **Authentification :**
- Cliquez sur "Auth" pour vous authentifier
- Session valide 30 minutes
- Une fois authentifié, tous les boutons sont débloqués

📊 **Pour les statistiques :**
- Utilisez "Statistiques" pour un aperçu général
- "Utilisateurs" pour voir tous les utilisateurs
- "Stats Détaillées" pour des analyses avancées

⭐ **Gestion du premium :**
- "Gérer Premium" pour le menu complet
- Donner/retirer premium individuellement ou en masse

📨 **Système de messages :**
- Les utilisateurs utilisent `/commentaire`
- Vous consultez avec "Mail Historique"
- Notifications en temps réel

🔧 **Outils avancés :**
- "Avancé" pour les outils professionnels
- Logs, nettoyage, recherche, suppression
- Export de données

📢 **Communication :**
- "Broadcast" pour messages massifs
- Utilisez avec modération

🆘 **Support :** Contactez @Soszoe pour assistance
"""
        bot.send_message(call.message.chat.id, help_text, parse_mode='Markdown')
        bot.answer_callback_query(call.id, "❓ Aide Admin")
    
    elif call.data.startswith("mail_page_"):
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        page = int(call.data.split("_")[2])
        show_mail_history(call.message, page)
        bot.answer_callback_query(call.id, f"📄 Page {page}")
    
    elif call.data == "admin_back":
        if not is_admin(user_id) or not is_admin_authenticated(user_id):
            bot.answer_callback_query(call.id, "🔐 Authentification requise")
            return
        
        bot.send_message(
            call.message.chat.id,
            "👑 **Panel Administrateur**\n\nMenu principal :",
            reply_markup=create_admin_menu(user_id),
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id, "🔙 Retour")

def process_admin_auth_callback(message, original_message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return
    
    if verify_admin_password(message.text.strip()):
        admin_sessions[user_id] = {'authenticated': True, 'auth_time': datetime.now()}
        
        try:
            bot.edit_message_text(
                chat_id=original_message.chat.id,
                message_id=original_message.message_id,
                text="👑 **Panel Administrateur**\n\n✅ **Authentification réussie !**\n🔓 **Tous les boutons sont maintenant débloqués !**",
                parse_mode='Markdown',
                reply_markup=create_admin_menu(user_id)
            )
        except:
            bot.send_message(
                original_message.chat.id,
                "✅ **Authentification réussie !**\n🔓 **Tous les boutons sont maintenant débloqués !**",
                reply_markup=create_admin_menu(user_id),
                parse_mode='Markdown'
            )
    else:
        bot.reply_to(message, "❌ **Mot de passe incorrect.**\n\nUtilisez à nouveau le bouton Auth.")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🗃️ Initialisation de la base de données...")
    init_db()
    repair_database()
    print("✅ Base de données prête")
    print(f"🚀 {BOT_NAME} - {VERSION}")
    print(f"👑 Créateur: {CREATOR}")
    print("🆕 NOUVEAUTÉS ADMIN COMPLÈTES :")
    print("   📋 Logs d'actions admin")
    print("   📈 Statistiques détaillées utilisateurs") 
    print("   🔍 Recherche d'utilisateurs")
    print("   🗑️ Suppression d'utilisateurs")
    print("   🧹 Nettoyage base de données")
    print("   🖥️ Informations système")
    print("   📤 Export de données")
    print("   ⚙️ Menu avancé complet")
    print("🤖 En attente de messages...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
