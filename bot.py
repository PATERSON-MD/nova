#!/data/data/com.termux/files/usr/bin/python3
# ==================== IMPORTS ====================
import telebot
import requests
import os
import sqlite3
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

# ==================== CONFIGURATION ====================
bot = telebot.TeleBot(os.getenv('TELEGRAM_TOKEN'))
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

CREATOR = "👑 Kervens"
BOT_NAME = "🚀 NovaAI Pro"
VERSION = "💎 Édition LÉGENDAIRE"
MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"

ADMIN_ID = 7908680781
AFFILIATE_LINK = "https://t.me/Kervensbug_bot"

# ==================== CORRECTION DATETIME ====================
import datetime

def adapt_datetime(dt):
    return dt.isoformat()

def convert_datetime(ts):
    if isinstance(ts, bytes):
        ts = ts.decode('utf-8')
    return datetime.datetime.fromisoformat(ts)

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter("TIMESTAMP", convert_datetime)

# ==================== BASE DE DONNÉES SÉCURISÉE ====================
def get_db_connection():
    """Crée une connexion sécurisée à la base de données"""
    conn = sqlite3.connect('bot_groups.db', timeout=30)
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn

def init_db():
    """Initialise la base de données"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''CREATE TABLE IF NOT EXISTS user_access
                     (user_id INTEGER PRIMARY KEY,
                      username TEXT,
                      first_name TEXT,
                      has_premium BOOLEAN DEFAULT FALSE,
                      premium_since TIMESTAMP,
                      referrals_count INTEGER DEFAULT 0,
                      message_count INTEGER DEFAULT 0,
                      total_tokens INTEGER DEFAULT 0,
                      added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                      last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS user_activity
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id INTEGER,
                      activity_date DATE DEFAULT CURRENT_DATE,
                      message_count INTEGER DEFAULT 1,
                      tokens_used INTEGER DEFAULT 0,
                      UNIQUE(user_id, activity_date))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                     (id INTEGER PRIMARY KEY CHECK (id = 1),
                      ai_enabled BOOLEAN DEFAULT TRUE,
                      premium_required BOOLEAN DEFAULT TRUE,
                      current_model TEXT DEFAULT "llama-3.1-8b-instant",
                      current_personality TEXT DEFAULT "default",
                      max_tokens INTEGER DEFAULT 4000,
                      temperature REAL DEFAULT 0.7)''')
        
        c.execute('''INSERT OR IGNORE INTO bot_settings 
                     (id, ai_enabled, premium_required, current_model, current_personality, max_tokens, temperature) 
                     VALUES (1, TRUE, TRUE, "llama-3.1-8b-instant", "default", 4000, 0.7)''')
        
        conn.commit()
        conn.close()
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur init DB: {e}")

# ==================== SYSTÈME DE COMPTEUR RÉEL ====================
COUNTER_FILE = "compteur.json"

def load_counter():
    """Charge le compteur depuis le fichier"""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('monthly_users', 0)
        return 0
    except:
        return 0

def save_counter(count):
    """Sauvegarde le compteur dans le fichier"""
    try:
        data = {
            'monthly_users': count,
            'last_update': datetime.now().isoformat()
        }
        with open(COUNTER_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"❌ Erreur sauvegarde compteur: {e}")

def get_monthly_users():
    """Récupère le nombre d'utilisateurs mensuels"""
    return load_counter()

def format_number(number):
    """Formate un nombre avec séparateurs"""
    return f"{number:,}".replace(",", " ")

# ==================== FONCTIONS UTILISATEURS ====================
def register_user(user_id, username, first_name):
    """Enregistre un utilisateur de manière sécurisée"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT user_id FROM user_access WHERE user_id = ?', (user_id,))
        existing_user = c.fetchone()
        
        if not existing_user:
            # Nouvel utilisateur - incrémenter le compteur
            c.execute('''INSERT INTO user_access 
                         (user_id, username, first_name, added_date, last_activity) 
                         VALUES (?, ?, ?, ?, ?)''', 
                         (user_id, username, first_name, datetime.now(), datetime.now()))
            
            # Incrémenter le compteur réel
            current_count = load_counter()
            new_count = current_count + 1
            save_counter(new_count)
            
            print(f"✅ Nouvel utilisateur: {user_id}")
            print(f"📈 Compteur: {current_count} → {new_count}")
        else:
            c.execute('UPDATE user_access SET last_activity = ? WHERE user_id = ?', 
                      (datetime.now(), user_id))
        
        # Mettre à jour l'activité quotidienne
        today = datetime.now().strftime('%Y-%m-%d')
        c.execute('''INSERT OR REPLACE INTO user_activity (user_id, activity_date, message_count)
                     VALUES (?, ?, COALESCE((SELECT message_count FROM user_activity WHERE user_id = ? AND activity_date = ?), 0) + 1)''',
                     (user_id, today, user_id, today))
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"⚠️ Erreur register_user: {e}")

def check_premium_access(user_id):
    """Vérifie si l'utilisateur a un accès premium"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT has_premium FROM user_access WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result and result[0]
    except:
        return False

def is_owner(user_id):
    return user_id == ADMIN_ID

def get_all_users():
    """Récupère tous les utilisateurs"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT user_id, username, first_name, has_premium, message_count FROM user_access')
        users = c.fetchall()
        conn.close()
        return users
    except:
        return []

def get_daily_stats():
    """Récupère les statistiques du jour"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        today = datetime.now().strftime('%Y-%m-%d')
        
        c.execute('SELECT SUM(message_count) FROM user_activity WHERE activity_date = ?', (today,))
        result = c.fetchone()
        today_messages = result[0] or 0 if result else 0
        
        c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date = ?', (today,))
        result = c.fetchone()
        today_users = result[0] or 0 if result else 0
        
        conn.close()
        return today_users, today_messages
    except:
        return 0, 0

# ==================== CONFIGURATION IA ====================
AI_ENABLED = True
PREMIUM_REQUIRED = True
current_model = "llama-3.1-8b-instant"
current_personality = "default"

def load_settings():
    """Charge les paramètres du bot"""
    global AI_ENABLED, PREMIUM_REQUIRED, current_model, current_personality
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT ai_enabled, premium_required, current_model, current_personality FROM bot_settings WHERE id = 1')
        result = c.fetchone()
        if result:
            AI_ENABLED = bool(result[0])
            PREMIUM_REQUIRED = bool(result[1])
            current_model = result[2] or "llama-3.1-8b-instant"
            current_personality = result[3] or "default"
        conn.close()
    except:
        pass

def save_settings():
    """Sauvegarde les paramètres du bot"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''UPDATE bot_settings SET 
                     ai_enabled = ?, premium_required = ?, current_model = ?, current_personality = ?
                     WHERE id = 1''',
                     (AI_ENABLED, PREMIUM_REQUIRED, current_model, current_personality))
        conn.commit()
        conn.close()
    except:
        pass

# ==================== INTERFACE ====================
def create_main_menu():
    keyboard = InlineKeyboardMarkup()
    support_button = InlineKeyboardButton("💝 Support Créateur", url="https://t.me/Soszoe")
    keyboard.add(support_button)
    return keyboard

def create_premium_menu(user_id=None):
    keyboard = InlineKeyboardMarkup()
    share_button = InlineKeyboardButton("📤 Partager", 
                                      url=f"https://t.me/share/url?url={AFFILIATE_LINK}?start={user_id}")
    status_button = InlineKeyboardButton("📊 Statut", callback_data="check_status")
    keyboard.add(share_button)
    keyboard.add(status_button)
    return keyboard

def create_owner_menu():
    keyboard = InlineKeyboardMarkup()
    
    stats_btn = InlineKeyboardButton("📊 Tableau de Bord", callback_data="admin_dashboard")
    users_btn = InlineKeyboardButton("👥 Utilisateurs", callback_data="admin_users")
    premium_btn = InlineKeyboardButton("⭐ Gérer Premium", callback_data="admin_premium")
    ai_btn = InlineKeyboardButton("🤖 Contrôle IA", callback_data="admin_ai")
    broadcast_btn = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
    system_btn = InlineKeyboardButton("⚙️ Système", callback_data="admin_system")
    
    keyboard.add(stats_btn)
    keyboard.add(users_btn, premium_btn)
    keyboard.add(ai_btn, broadcast_btn)
    keyboard.add(system_btn)
    
    return keyboard

def create_ai_control_menu():
    keyboard = InlineKeyboardMarkup()
    
    ai_status = "🟢 ON" if AI_ENABLED else "🔴 OFF"
    premium_status = "🔒 ON" if PREMIUM_REQUIRED else "🔓 OFF"
    
    ai_toggle = InlineKeyboardButton(f"IA: {ai_status}", callback_data="admin_toggle_ai")
    premium_toggle = InlineKeyboardButton(f"Premium: {premium_status}", callback_data="admin_toggle_premium")
    stats_btn = InlineKeyboardButton("📈 Statistiques IA", callback_data="admin_ai_stats")
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    
    keyboard.add(ai_toggle, premium_toggle)
    keyboard.add(stats_btn)
    keyboard.add(back_btn)
    
    return keyboard

def create_premium_control_menu():
    keyboard = InlineKeyboardMarkup()
    
    give_premium = InlineKeyboardButton("🎁 Donner Premium", callback_data="admin_give_premium")
    remove_premium = InlineKeyboardButton("🗑️ Retirer Premium", callback_data="admin_remove_premium")
    premium_all = InlineKeyboardButton("⭐ Premium à Tous", callback_data="admin_premium_all")
    remove_all = InlineKeyboardButton("🔓 Retirer à Tous", callback_data="admin_remove_all")
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    
    keyboard.add(give_premium, remove_premium)
    keyboard.add(premium_all, remove_all)
    keyboard.add(back_btn)
    
    return keyboard

def create_system_menu():
    keyboard = InlineKeyboardMarkup()
    
    reset_counter = InlineKeyboardButton("🔄 Reset Compteur", callback_data="admin_reset_counter")
    backup_btn = InlineKeyboardButton("💾 Sauvegarde", callback_data="admin_backup")
    restart_btn = InlineKeyboardButton("🔄 Redémarrer", callback_data="admin_restart")
    back_btn = InlineKeyboardButton("🔙 Retour", callback_data="admin_back")
    
    keyboard.add(reset_counter, backup_btn)
    keyboard.add(restart_btn)
    keyboard.add(back_btn)
    
    return keyboard

# ==================== MOTEUR IA SIMPLIFIÉ ====================
def advanced_ai_handler(user_id, user_message):
    if not AI_ENABLED:
        return "🤖 **IA TEMPORAIREMENT INDISPONIBLE**\n\nL'assistant IA est actuellement désactivé."
    
    if not GROQ_API_KEY:
        return "❌ **SERVICE IA INDISPONIBLE**\n\nConfiguration API manquante."
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": "user", "content": user_message}],
            "model": current_model,
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"❌ **Erreur de service**\n\nCode: {response.status_code}"
            
    except Exception as e:
        return f"🔧 **Erreur technique**\n\n{str(e)[:100]}"

# ==================== HANDLERS PRINCIPAUX ====================
@bot.message_handler(commands=['start'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        # Enregistrement sécurisé
        register_user(user_id, username, first_name)
        
        # Récupérer le compteur actuel
        user_count = get_monthly_users()
        
        if is_owner(user_id):
            # Interface propriétaire
            caption = f"""
# 🚀 NOVA-AI  
**{format_number(user_count)} utilisateurs mensuel**  

- **Premium**  
  **Édition Propriétaire**  

- **KervensAI Pro**  
  **Édition LÉGENDAIRE**  

- **BIENVENUE PROPRIÉTAIRE !**  

- Contrôles disponibles :  
  - Activer/Désactiver l'IA  
  - Gérer les premiums  
  - Broadcast massif  
  - Statistiques détaillées  

- Utilisez les boutons ci-dessous !  
"""
            bot.send_photo(
                message.chat.id,
                MAIN_PHOTO,
                caption=caption,
                parse_mode='Markdown',
                reply_markup=create_owner_menu()
            )
        else:
            if check_premium_access(user_id):
                # Utilisateur premium
                caption = f"""
# 🚀 NOVA-AI  
**{format_number(user_count)} utilisateurs mensuel**  

- **Premium**  
  **Activé** ✅  

- **KervensAI Pro**  
  **Édition LÉGENDAIRE**  

🎉 **ACCÈS COMPLET DÉBLOQUÉ !**

💡 **Envoyez n'importe quelle question !**
"""
                bot.send_photo(
                    message.chat.id,
                    MAIN_PHOTO,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=create_main_menu()
                )
            else:
                # Utilisateur non premium
                caption = f"""
# 🚀 NOVA-AI  
**{format_number(user_count)} utilisateurs mensuel**  

- **Premium**  
  **En attente** 🔒  

- **KervensAI Pro**  
  **Édition LÉGENDAIRE**  

🔒 **VERSION STANDARD**

💡 **Partagez le bot pour débloquer l'IA complète !**
"""
                bot.send_photo(
                    message.chat.id,
                    MAIN_PHOTO,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=create_premium_menu(user_id)
                )
            
    except Exception as e:
        print(f"❌ Erreur start: {e}")
        try:
            bot.reply_to(message, "🔄 Veuillez réessayer...")
        except:
            pass

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Commande pour voir les statistiques"""
    user_count = get_monthly_users()
    today_users, today_messages = get_daily_stats()
    
    stats_text = f"""
📊 **STATISTIQUES NOVA-AI**

👥 Utilisateurs mensuels: **{format_number(user_count)}**
📈 Actifs aujourd'hui: **{today_users}**
💬 Messages aujourd'hui: **{today_messages}**
🕐 Mis à jour: {datetime.now().strftime('%H:%M')}
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    """Commande broadcast pour le propriétaire"""
    if not is_owner(message.from_user.id):
        return
    
    if len(message.text.split()) > 1:
        broadcast_text = ' '.join(message.text.split()[1:])
        bot.reply_to(message, "🔄 Diffusion en cours...")
        
        users = get_all_users()
        success = 0
        for user in users[:50]:  # Limite pour éviter le spam
            try:
                bot.send_message(user[0], f"📢 **ANNONCE**\n\n{broadcast_text}", parse_mode='Markdown')
                success += 1
                time.sleep(0.1)  # Pause anti-spam
            except:
                pass
        
        bot.reply_to(message, f"✅ Diffusion terminée: {success}/{len(users)} utilisateurs")
    else:
        bot.reply_to(message, "❌ Usage: /broadcast <message>")

@bot.message_handler(commands=['premium'])
def premium_command(message):
    """Commande pour gérer les premiums"""
    if not is_owner(message.from_user.id):
        return
    
    parts = message.text.split()
    if len(parts) >= 3:
        action = parts[1]
        user_id = int(parts[2])
        
        try:
            conn = get_db_connection()
            c = conn.cursor()
            
            if action == "add":
                c.execute('UPDATE user_access SET has_premium = TRUE WHERE user_id = ?', (user_id,))
                bot.reply_to(message, f"✅ Premium ajouté à l'utilisateur {user_id}")
            elif action == "remove":
                c.execute('UPDATE user_access SET has_premium = FALSE WHERE user_id = ?', (user_id,))
                bot.reply_to(message, f"❌ Premium retiré à l'utilisateur {user_id}")
            
            conn.commit()
            conn.close()
        except Exception as e:
            bot.reply_to(message, f"❌ Erreur: {e}")
    else:
        bot.reply_to(message, "❌ Usage: /premium <add/remove> <user_id>")

@bot.message_handler(commands=['users'])
def users_command(message):
    """Commande pour lister les utilisateurs"""
    if not is_owner(message.from_user.id):
        return
    
    users = get_all_users()
    if not users:
        bot.reply_to(message, "📭 Aucun utilisateur enregistré.")
        return
    
    response = "👥 **UTILISATEURS**\n\n"
    for i, user in enumerate(users[:15], 1):
        user_id, username, first_name, has_premium, message_count = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "─"
        
        response += f"{i}. {premium_status} **{first_name}**\n"
        response += f"   👤 {username_display} • 🆔 `{user_id}`\n"
        response += f"   💬 {message_count} msg\n\n"
    
    if len(users) > 15:
        response += f"\n... et {len(users) - 15} autres utilisateurs"
    
    bot.send_message(message.chat.id, response, parse_mode='Markdown')

@bot.message_handler(commands=['reset_counter'])
def reset_counter_command(message):
    """Commande pour reset le compteur"""
    if not is_owner(message.from_user.id):
        return
    
    save_counter(0)
    bot.reply_to(message, "✅ Compteur reset à 0 utilisateurs")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gestion des messages normaux"""
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    if len(user_message) < 2:
        return
    
    if not check_premium_access(user_id):
        user_count = get_monthly_users()
        response = f"# 🚀 NOVA-AI  \n**{format_number(user_count)} utilisateurs mensuel**  \n\n🔒 **ACCÈS LIMITÉ**  \n\n💡 Partagez le bot pour débloquer l'IA complète !"
        bot.reply_to(message, response, reply_markup=create_premium_menu(user_id))
        return
    
    # Traitement IA pour les utilisateurs premium
    bot.send_chat_action(message.chat.id, 'typing')
    ai_response = advanced_ai_handler(user_id, user_message)
    bot.reply_to(message, ai_response)

# ==================== CALLBACKS POUR LE PROPRIÉTAIRE ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    if not is_owner(user_id):
        bot.answer_callback_query(call.id, "🔐 Accès réservé")
        return
    
    try:
        if call.data == "admin_dashboard":
            user_count = get_monthly_users()
            today_users, today_messages = get_daily_stats()
            total_users = len(get_all_users())
            
            dashboard_text = f"""
📊 **TABLEAU DE BORD PROPRIÉTAIRE**

👥 Utilisateurs mensuels: **{format_number(user_count)}**
📈 Actifs aujourd'hui: **{today_users}**
💬 Messages aujourd'hui: **{today_messages}**
👤 Total utilisateurs: **{total_users}**
🤖 IA: **{'🟢 ON' if AI_ENABLED else '🔴 OFF'}**
⭐ Premium: **{'🔒 REQUIS' if PREMIUM_REQUIRED else '🔓 GRATUIT'}**

🕐 Dernière MAJ: {datetime.now().strftime('%H:%M:%S')}
"""
            bot.edit_message_text(
                dashboard_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=create_owner_menu()
            )
            bot.answer_callback_query(call.id, "📊 Dashboard")
        
        elif call.data == "admin_users":
            users_command(call.message)
            bot.answer_callback_query(call.id, "👥 Utilisateurs")
        
        elif call.data == "admin_premium":
            bot.edit_message_text(
                "⭐ **GESTION DES PREMIUMS**\n\nChoisissez une action:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=create_premium_control_menu()
            )
            bot.answer_callback_query(call.id, "⭐ Premium")
        
        elif call.data == "admin_ai":
            bot.edit_message_text(
                "🤖 **CONTRÔLE IA**\n\nParamètres de l'assistant IA:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=create_ai_control_menu()
            )
            bot.answer_callback_query(call.id, "🤖 IA")
        
        elif call.data == "admin_system":
            bot.edit_message_text(
                "⚙️ **SYSTÈME**\n\nActions système:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=create_system_menu()
            )
            bot.answer_callback_query(call.id, "⚙️ Système")
        
        elif call.data == "admin_toggle_ai":
            global AI_ENABLED
            AI_ENABLED = not AI_ENABLED
            save_settings()
            status = "activée" if AI_ENABLED else "désactivée"
            bot.answer_callback_query(call.id, f"🤖 IA {status}")
            callback_handler(call)  # Refresh le menu
        
        elif call.data == "admin_toggle_premium":
            global PREMIUM_REQUIRED
            PREMIUM_REQUIRED = not PREMIUM_REQUIRED
            save_settings()
            status = "requis" if PREMIUM_REQUIRED else "gratuit"
            bot.answer_callback_query(call.id, f"⭐ Premium {status}")
            callback_handler(call)  # Refresh le menu
        
        elif call.data == "admin_reset_counter":
            save_counter(0)
            bot.answer_callback_query(call.id, "🔄 Compteur reset")
            callback_handler(call)  # Refresh le menu
        
        elif call.data == "admin_back":
            start_handler(call.message)
            bot.answer_callback_query(call.id, "🔙 Retour")
        
        elif call.data == "check_status":
            user_count = get_monthly_users()
            bot.answer_callback_query(call.id, f"👥 {user_count} utilisateurs")
                
    except Exception as e:
        print(f"❌ Erreur callback: {e}")
        bot.answer_callback_query(call.id, "❌ Erreur")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🚀 Initialisation de Nova-AI...")
    init_db()
    load_settings()
    
    user_count = get_monthly_users()
    print(f"✅ Compteur initial: {user_count} utilisateurs")
    print(f"🤖 IA: {'🟢 ACTIVÉE' if AI_ENABLED else '🔴 DÉSACTIVÉE'}")
    print(f"⭐ Premium: {'🔒 REQUIS' if PREMIUM_REQUIRED else '🔓 GRATUIT'}")
    print("🎛️  NOUVELLES COMMANDES PROPRIÉTAIRE:")
    print("   • /stats - Voir les statistiques")
    print("   • /users - Lister les utilisateurs") 
    print("   • /premium <add/remove> <user_id> - Gérer premium")
    print("   • /broadcast <message> - Diffusion massive")
    print("   • /reset_counter - Reset le compteur")
    print("🤖 En attente de messages...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
