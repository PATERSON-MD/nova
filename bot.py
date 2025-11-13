#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 NOVA-AI ULTIMATE - STATISTIQUES RÉELLES
💎 Édition ULTIME avec données en temps réel
👑 Créé par Kervens
"""

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
class Config:
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    CREATOR = "👑 Kervens"
    BOT_NAME = "🚀 NovaAI ULTIMATE"
    VERSION = "💎 Édition COSMIC"
    MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
    
    ADMIN_ID = 7908680781
    AFFILIATE_LINK = "https://t.me/Kervensbug_bot"
    
    COUNTER_FILE = "compteur.json"
    DB_FILE = "bot_ultimate.db"

bot = telebot.TeleBot(Config.TOKEN)

# ==================== SYSTÈME DE STATISTIQUES RÉELLES ====================
class RealStats:
    """Système de statistiques en temps réel"""
    
    @staticmethod
    def get_db_connection():
        conn = sqlite3.connect(Config.DB_FILE, timeout=30)
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn
    
    @staticmethod
    def init_database():
        """Initialise la base de données avec les vraies tables"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            # Table utilisateurs principale
            c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    has_premium BOOLEAN DEFAULT FALSE,
                    premium_since TIMESTAMP,
                    total_messages INTEGER DEFAULT 0,
                    current_level INTEGER DEFAULT 1,
                    personality TEXT DEFAULT "default",
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table activité réelle
            c.execute('''
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    activity_date DATE DEFAULT CURRENT_DATE,
                    message_count INTEGER DEFAULT 0,
                    tokens_used INTEGER DEFAULT 0,
                    UNIQUE(user_id, activity_date)
                )
            ''')
            
            # Table paramètres
            c.execute('''
                CREATE TABLE IF NOT EXISTS bot_settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    ai_enabled BOOLEAN DEFAULT TRUE,
                    premium_required BOOLEAN DEFAULT TRUE
                )
            ''')
            
            c.execute('INSERT OR IGNORE INTO bot_settings (id, ai_enabled, premium_required) VALUES (1, TRUE, TRUE)')
            
            conn.commit()
            conn.close()
            print("✅ BASE DE DONNÉES RÉELLE INITIALISÉE")
        except Exception as e:
            print(f"❌ ERREUR DB: {e}")
    
    @staticmethod
    def get_monthly_users():
        """Utilisateurs mensuels RÉELS"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date >= ?', (first_day,))
            result = c.fetchone()
            conn.close()
            return result[0] if result else 0
        except:
            return 0
    
    @staticmethod
    def get_total_users():
        """Total utilisateurs RÉELS"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM users')
            result = c.fetchone()
            conn.close()
            return result[0] if result else 0
        except:
            return 0
    
    @staticmethod
    def get_today_stats():
        """Statistiques du jour RÉELLES"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Messages aujourd'hui
            c.execute('SELECT SUM(message_count) FROM user_activity WHERE activity_date = ?', (today,))
            result = c.fetchone()
            today_messages = result[0] if result and result[0] else 0
            
            # Utilisateurs actifs aujourd'hui
            c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date = ?', (today,))
            result = c.fetchone()
            today_users = result[0] if result and result[0] else 0
            
            conn.close()
            return today_users, today_messages
        except:
            return 0, 0
    
    @staticmethod
    def get_24h_stats():
        """Statistiques 24h RÉELLES"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            last_24h = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
            
            c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE datetime(activity_date) >= ?', (last_24h,))
            result = c.fetchone()
            active_24h = result[0] if result and result[0] else 0
            
            c.execute('SELECT SUM(message_count) FROM user_activity WHERE datetime(activity_date) >= ?', (last_24h,))
            result = c.fetchone()
            messages_24h = result[0] if result and result[0] else 0
            
            conn.close()
            return active_24h, messages_24h
        except:
            return 0, 0
    
    @staticmethod
    def get_premium_stats():
        """Statistiques premium RÉELLES"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            c.execute('SELECT COUNT(*) FROM users WHERE has_premium = TRUE')
            result = c.fetchone()
            premium_users = result[0] if result and result[0] else 0
            
            c.execute('SELECT COUNT(*) FROM users')
            result = c.fetchone()
            total_users = result[0] if result and result[0] else 0
            
            conn.close()
            
            premium_percentage = (premium_users / total_users * 100) if total_users > 0 else 0
            return premium_users, total_users, round(premium_percentage, 1)
        except:
            return 0, 0, 0
    
    @staticmethod
    def get_growth_rate():
        """Taux de croissance RÉEL"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            # Utilisateurs ce mois
            first_day = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date >= ?', (first_day,))
            result = c.fetchone()
            current_month = result[0] if result and result[0] else 0
            
            # Utilisateurs mois dernier
            last_month = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
            first_day_last_month = last_month.strftime('%Y-%m-%d')
            last_day_last_month = (last_month.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
            
            c.execute('SELECT COUNT(DISTINCT user_id) FROM user_activity WHERE activity_date BETWEEN ? AND ?', 
                     (first_day_last_month, last_day_last_month.strftime('%Y-%m-%d')))
            result = c.fetchone()
            previous_month = result[0] if result and result[0] else 0
            
            conn.close()
            
            if previous_month == 0:
                return 100.0 if current_month > 0 else 0.0
            
            growth = ((current_month - previous_month) / previous_month) * 100
            return round(growth, 1)
        except:
            return 0.0
    
    @staticmethod
    def get_average_messages():
        """Moyenne de messages par utilisateur RÉELLE"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            c.execute('SELECT AVG(total_messages) FROM users WHERE total_messages > 0')
            result = c.fetchone()
            conn.close()
            
            avg_messages = result[0] if result and result[0] else 0
            return round(avg_messages, 1)
        except:
            return 0.0

# ==================== SYSTÈME DE COMPTEUR RÉEL ====================
class RealCounter:
    """Compteur d'utilisateurs réel"""
    
    @staticmethod
    def load_counter():
        try:
            if os.path.exists(Config.COUNTER_FILE):
                with open(Config.COUNTER_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('monthly_users', 0)
            return 0
        except:
            return 0
    
    @staticmethod
    def save_counter(count):
        try:
            data = {
                'monthly_users': count,
                'last_update': datetime.now().isoformat(),
                'bot_name': Config.BOT_NAME
            }
            with open(Config.COUNTER_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ ERREUR SAUVEGARDE COMPTEUR: {e}")
    
    @staticmethod
    def get_monthly_users():
        return RealCounter.load_counter()
    
    @staticmethod
    def format_number(number):
        return f"{number:,}".replace(",", " ")

# ==================== GESTION UTILISATEURS RÉELLE ====================
class UserManager:
    """Gestion réelle des utilisateurs"""
    
    @staticmethod
    def register_user(user_id, username, first_name):
        """Enregistre un utilisateur avec des statistiques réelles"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            # Vérifier si l'utilisateur existe
            c.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            existing_user = c.fetchone()
            
            if not existing_user:
                # NOUVEL UTILISATEUR - Incrémenter le compteur
                current_count = RealCounter.load_counter()
                RealCounter.save_counter(current_count + 1)
                
                # Ajouter à la base
                c.execute('''
                    INSERT INTO users (user_id, username, first_name, total_messages) 
                    VALUES (?, ?, ?, 1)
                ''', (user_id, username, first_name))
                print(f"✅ NOUVEL UTILISATEUR: {user_id}")
            else:
                # Mettre à jour l'activité
                c.execute('UPDATE users SET total_messages = total_messages + 1, last_activity = ? WHERE user_id = ?', 
                         (datetime.now(), user_id))
            
            # Mettre à jour l'activité du jour
            today = datetime.now().strftime('%Y-%m-%d')
            c.execute('''
                INSERT OR REPLACE INTO user_activity (user_id, activity_date, message_count)
                VALUES (?, ?, COALESCE((SELECT message_count FROM user_activity WHERE user_id = ? AND activity_date = ?), 0) + 1)
            ''', (user_id, today, user_id, today))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ ERREUR ENREGISTREMENT: {e}")
    
    @staticmethod
    def is_owner(user_id):
        return user_id == Config.ADMIN_ID
    
    @staticmethod
    def is_premium(user_id):
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            c.execute('SELECT has_premium FROM users WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            conn.close()
            return result and result[0]
        except:
            return False

# ==================== TABLEAU DE BORD RÉEL ====================
class RealDashboard:
    """Tableau de bord avec statistiques réelles"""
    
    @staticmethod
    def create_owner_dashboard():
        """Crée le tableau de bord propriétaire avec données réelles"""
        
        # Récupérer toutes les stats RÉELLES
        monthly_users = RealStats.get_monthly_users()
        total_users = RealStats.get_total_users()
        today_users, today_messages = RealStats.get_today_stats()
        active_24h, messages_24h = RealStats.get_24h_stats()
        premium_users, total_users_premium, premium_percentage = RealStats.get_premium_stats()
        growth_rate = RealStats.get_growth_rate()
        avg_messages = RealStats.get_average_messages()
        
        # Formater les nombres
        monthly_formatted = RealCounter.format_number(monthly_users)
        total_formatted = RealCounter.format_number(total_users)
        today_users_formatted = RealCounter.format_number(today_users)
        today_messages_formatted = RealCounter.format_number(today_messages)
        premium_formatted = RealCounter.format_number(premium_users)
        
        dashboard_text = f"""
📊 **DASHBOARD ULTIME - PROPRIÉTAIRE**

┌──────────────────────────────┐
│  🚀 NOVA-AI ULTIMATE         │
│  👥 {monthly_formatted:>16} mensuels │
└──────────────────────────────┘

📈 **STATISTIQUES RÉELLES :**
• Utilisateurs totaux: **{total_formatted}**
• Actifs aujourd'hui: **{today_users_formatted}**
• Messages aujourd'hui: **{today_messages_formatted}**
• Actifs (24h): **{active_24h}**
• Messages (24h): **{messages_24h}**

💰 **PREMIUM :**
• Abonnés: **{premium_formatted}** ({premium_percentage}%)
• Croissance: **{growth_rate}%** ce mois
• Messages/user: **{avg_messages}**

🎯 **SYSTÈME :**
• IA: 🟢 ACTIVÉE
• Base de données: 🟢 OPÉRATIONNELLE
• Compteur: 🟢 ACTIF

🕐 **Dernière MAJ:** {datetime.now().strftime('%H:%M:%S')}
"""
        return dashboard_text
    
    @staticmethod
    def create_user_stats(user_id):
        """Statistiques personnelles de l'utilisateur"""
        try:
            conn = RealStats.get_db_connection()
            c = conn.cursor()
            
            c.execute('SELECT total_messages, has_premium FROM users WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            
            if result:
                total_messages, has_premium = result
                premium_status = "✅ ACTIVÉ" if has_premium else "🔒 STANDARD"
                
                monthly_users = RealStats.get_monthly_users()
                monthly_formatted = RealCounter.format_number(monthly_users)
                
                stats_text = f"""
📊 **TES STATISTIQUES**

┌──────────────────────────────┐
│  👤 {Config.BOT_NAME:<16} │
│  👥 {monthly_formatted:>16} membres │
└──────────────────────────────┘

🎯 **TON PROFIL :**
• Messages envoyés: **{total_messages}**
• Statut: **{premium_status}**
• Niveau: **{min(total_messages // 10 + 1, 10)}/10**

💎 **COMMUNAUTÉ :**
• Utilisateurs mensuels: **{monthly_formatted}**
• Croissance active: **{RealStats.get_growth_rate()}%**

🚀 **Continue à discuter pour monter en niveau !**
"""
                return stats_text
            
            conn.close()
        except:
            pass
        
        return "📊 **Aucune statistique disponible pour le moment.**"

# ==================== INTERFACE ====================
class Interface:
    """Interface utilisateur"""
    
    @staticmethod
    def create_owner_menu():
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            ("📊 Dashboard Live", "admin_dashboard"),
            ("👥 Utilisateurs", "admin_users"), 
            ("⭐ Premium", "admin_premium"),
            ("🤖 Contrôle IA", "admin_ai"),
            ("📢 Broadcast", "admin_broadcast"),
            ("⚙️ Système", "admin_system")
        ]
        
        for i in range(0, len(buttons), 2):
            row = []
            for j in range(2):
                if i + j < len(buttons):
                    text, callback = buttons[i + j]
                    row.append(InlineKeyboardButton(text, callback_data=callback))
            keyboard.add(*row)
        
        return keyboard
    
    @staticmethod
    def create_user_menu():
        keyboard = InlineKeyboardMarkup()
        stats_btn = InlineKeyboardButton("📊 Mes Stats", callback_data="user_stats")
        support_btn = InlineKeyboardButton("💝 Support", url="https://t.me/Soszoe")
        keyboard.add(stats_btn, support_btn)
        return keyboard

# ==================== HANDLERS PRINCIPAUX ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        # Enregistrement RÉEL
        UserManager.register_user(user_id, username, first_name)
        
        # Récupérer les stats RÉELLES
        monthly_users = RealCounter.get_monthly_users()
        monthly_formatted = RealCounter.format_number(monthly_users)
        
        if UserManager.is_owner(user_id):
            caption = f"""
🏰 **BIENVENUE PROPRIÉTAIRE !**

┌──────────────────────────────┐
│  🚀 NOVA-AI ULTIMATE         │
│  👥 {monthly_formatted:>16} utilisateurs  │
└──────────────────────────────┘

📊 **STATISTIQUES RÉELLES :**
• Utilisateurs mensuels: **{monthly_formatted}**
• Croissance: **{RealStats.get_growth_rate()}%**
• Système: 🟢 OPÉRATIONNEL

🎛️ **Utilisez le tableau de bord pour tout contrôler !**
"""
            menu = Interface.create_owner_menu()
        else:
            caption = f"""
🎉 **BIENVENUE SUR NOVA-AI ULTIMATE !**

┌──────────────────────────────┐
│  🚀 NOVA-AI ULTIMATE         │
│  👥 {monthly_formatted:>16} membres   │
└──────────────────────────────┘

💎 **Rejoignez notre communauté de {monthly_formatted} membres !**

✨ **Fonctionnalités :**
• IA avancée avec Groq
• Réponses personnalisées
• Support 24/7

🚀 **Envoyez un message pour commencer !**
"""
            menu = Interface.create_user_menu()
        
        bot.send_photo(
            message.chat.id,
            Config.MAIN_PHOTO,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=menu
        )
        
    except Exception as e:
        print(f"❌ ERREUR /start: {e}")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Commande /stats avec données réelles"""
    user_id = message.from_user.id
    
    if UserManager.is_owner(user_id):
        # Tableau de bord propriétaire
        dashboard_text = RealDashboard.create_owner_dashboard()
        bot.reply_to(message, dashboard_text, parse_mode='Markdown')
    else:
        # Stats utilisateur
        user_stats = RealDashboard.create_user_stats(user_id)
        bot.reply_to(message, user_stats, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gestion des messages normaux"""
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    if len(user_message) < 2:
        return
    
    # Mettre à jour les stats
    UserManager.register_user(user_id, 
                             message.from_user.username or "User", 
                             message.from_user.first_name or "User")
    
    # Vérifier premium
    if not UserManager.is_premium(user_id) and not UserManager.is_owner(user_id):
        monthly_users = RealCounter.get_monthly_users()
        monthly_formatted = RealCounter.format_number(monthly_users)
        
        response = f"""
🔒 **VERSION STANDARD**

Rejoignez nos **{monthly_formatted}** membres en premium !
Fonctionnalités débloquées : IA avancée, réponses illimitées.

💎 **Passez premium pour utiliser l'IA complète !**
"""
        bot.reply_to(message, response, parse_mode='Markdown')
        return
    
    # Traitement IA
    bot.send_chat_action(message.chat.id, 'typing')
    
    if not Config.GROQ_API_KEY:
        bot.reply_to(message, "❌ **Service IA temporairement indisponible**")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {Config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messages": [{"role": "user", "content": user_message}],
            "model": "llama-3.1-70b-versatile",
            "max_tokens": 4000,
            "temperature": 0.7
        }
        
        response = requests.post(Config.GROQ_API_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            bot.reply_to(message, ai_response)
        else:
            bot.reply_to(message, f"❌ **Erreur de service**\n\nCode: {response.status_code}")
            
    except Exception as e:
        bot.reply_to(message, f"🔧 **Erreur technique**\n\n{str(e)[:100]}")

# ==================== CALLBACKS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    
    try:
        if call.data == "admin_dashboard":
            if not UserManager.is_owner(user_id):
                bot.answer_callback_query(call.id, "🔐 Accès réservé")
                return
            
            dashboard_text = RealDashboard.create_owner_dashboard()
            bot.edit_message_text(
                dashboard_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=Interface.create_owner_menu()
            )
            bot.answer_callback_query(call.id, "📊 Dashboard MAJ")
        
        elif call.data == "user_stats":
            user_stats = RealDashboard.create_user_stats(user_id)
            bot.edit_message_text(
                user_stats,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=Interface.create_user_menu()
            )
            bot.answer_callback_query(call.id, "📊 Tes stats")
                
    except Exception as e:
        print(f"❌ ERREUR CALLBACK: {e}")
        bot.answer_callback_query(call.id, "❌ Erreur")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🚀 INITIALISATION DE NOVA-AI ULTIMATE...")
    
    # Initialiser la base de données RÉELLE
    RealStats.init_database()
    
    # Charger les stats initiales
    monthly_users = RealStats.get_monthly_users()
    total_users = RealStats.get_total_users()
    
    print(f"""
✅ SYSTÈME ULTIME OPÉRATIONNEL

📊 STATISTIQUES RÉELLES :
   • Utilisateurs mensuels: {monthly_users}
   • Utilisateurs totaux: {total_users}
   • Croissance: {RealStats.get_growth_rate()}%
   • Premium: {RealStats.get_premium_stats()[2]}%

🎛️  COMMANDES DISPONIBLES :
   • /start - Menu principal
   • /stats - Statistiques réelles

🤖 BOT EN LIGNE - EN ATTENTE DE MESSAGES...
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        time.sleep(5)
