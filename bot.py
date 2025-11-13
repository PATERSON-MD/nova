#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 NOVA-AI ULTIMATE - VERSION CHALEUREUSE
💖 Édition Premium avec gestion complète
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

# ==================== CONFIGURATION CHALEUREUSE ====================
class Config:
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    CREATOR = "👑 Kervens"
    BOT_NAME = "💖 NovaAI Pro"
    VERSION = "✨ Édition Familiale"
    MAIN_PHOTO = "https://files.catbox.moe/601u5z.jpg"
    
    ADMIN_ID = 7908680781

bot = telebot.TeleBot(Config.TOKEN)

# ==================== SYSTÈME DE BASE DE DONNÉES ====================
class Database:
    def __init__(self):
        self.init_db()
    
    def init_db(self):
        """Initialise la base de données"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        # Table utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                is_premium INTEGER DEFAULT 0,
                premium_until TEXT,
                message_count INTEGER DEFAULT 0,
                join_date TEXT,
                last_active TEXT
            )
        ''')
        
        # Table statistiques
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY,
                total_users INTEGER DEFAULT 0,
                premium_users INTEGER DEFAULT 0,
                total_messages INTEGER DEFAULT 0
            )
        ''')
        
        # Insérer les stats initiales si elles n'existent pas
        cursor.execute('INSERT OR IGNORE INTO stats (id, total_users, premium_users, total_messages) VALUES (1, 0, 0, 0)')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name):
        """Ajoute un utilisateur à la base de données"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        join_date = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, join_date, last_active) 
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, join_date, join_date))
        
        # Mettre à jour les statistiques seulement si nouvel utilisateur
        cursor.execute('SELECT COUNT(*) FROM users WHERE user_id = ?', (user_id,))
        if cursor.fetchone()[0] == 1:  # Nouvel utilisateur
            cursor.execute('UPDATE stats SET total_users = total_users + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
    
    def get_user(self, user_id):
        """Récupère les informations d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        
        conn.close()
        return user
    
    def set_premium(self, user_id, days=30):
        """Définit un utilisateur comme premium"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        # Vérifier si l'utilisateur était déjà premium
        cursor.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        was_premium = result and result[0] == 1
        
        cursor.execute('''
            UPDATE users 
            SET is_premium = 1, premium_until = ?
            WHERE user_id = ?
        ''', (premium_until, user_id))
        
        # Mettre à jour les statistiques premium seulement si nouveau premium
        if not was_premium:
            cursor.execute('UPDATE stats SET premium_users = premium_users + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
        
        return premium_until
    
    def remove_premium(self, user_id):
        """Retire le statut premium d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur était premium
        cursor.execute('SELECT is_premium FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        was_premium = result and result[0] == 1
        
        cursor.execute('''
            UPDATE users 
            SET is_premium = 0, premium_until = NULL
            WHERE user_id = ?
        ''', (user_id,))
        
        # Mettre à jour les statistiques seulement si l'utilisateur était premium
        if was_premium:
            cursor.execute('UPDATE stats SET premium_users = premium_users - 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
        return was_premium
    
    def set_all_premium(self, days=30):
        """Donne le premium à tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        premium_until = (datetime.now() + timedelta(days=days)).isoformat()
        
        # Compter combien d'utilisateurs deviennent premium
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 0')
        new_premium_count = cursor.fetchone()[0]
        
        # Mettre à jour tous les utilisateurs
        cursor.execute('''
            UPDATE users 
            SET is_premium = 1, premium_until = ?
        ''', (premium_until,))
        
        # Mettre à jour les statistiques
        cursor.execute('UPDATE stats SET premium_users = (SELECT COUNT(*) FROM users) WHERE id = 1')
        
        conn.commit()
        conn.close()
        
        return new_premium_count
    
    def remove_all_premium(self):
        """Retire le premium de tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        # Compter combien d'utilisateurs perdaient le premium
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_premium = 1')
        removed_premium_count = cursor.fetchone()[0]
        
        # Mettre à jour tous les utilisateurs
        cursor.execute('''
            UPDATE users 
            SET is_premium = 0, premium_until = NULL
        ''')
        
        # Mettre à jour les statistiques
        cursor.execute('UPDATE stats SET premium_users = 0 WHERE id = 1')
        
        conn.commit()
        conn.close()
        
        return removed_premium_count
    
    def get_all_users(self):
        """Récupère tous les utilisateurs"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY join_date DESC')
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def get_premium_users(self):
        """Récupère les utilisateurs premium"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE is_premium = 1 ORDER BY premium_until DESC')
        users = cursor.fetchall()
        
        conn.close()
        return users
    
    def get_stats(self):
        """Récupère les statistiques"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM stats WHERE id = 1')
        stats = cursor.fetchone()
        
        conn.close()
        return stats
    
    def increment_message_count(self, user_id):
        """Incrémente le compteur de messages"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET message_count = message_count + 1, last_active = ? WHERE user_id = ?', 
                      (datetime.now().isoformat(), user_id))
        cursor.execute('UPDATE stats SET total_messages = total_messages + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()

# ==================== SYSTÈME DE COMPTEUR RÉEL ====================
class CounterSystem:
    """Système de compteur d'utilisateurs"""
    
    COUNTER_FILE = "compteur.json"
    
    @staticmethod
    def load():
        try:
            if os.path.exists(CounterSystem.COUNTER_FILE):
                with open(CounterSystem.COUNTER_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('monthly_users', 0)
            return 0
        except:
            return 0
    
    @staticmethod
    def save(count):
        try:
            data = {
                'monthly_users': count,
                'last_update': datetime.now().isoformat()
            }
            with open(CounterSystem.COUNTER_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ Erreur sauvegarde compteur: {e}")
    
    @staticmethod
    def increment():
        current = CounterSystem.load()
        new_count = current + 1
        CounterSystem.save(new_count)
        return new_count
    
    @staticmethod
    def format_number(number):
        return f"{number:,}".replace(",", " ")

# ==================== MOTEUR IA CHALEUREUX ====================
class WarmAIEngine:
    """Moteur IA avec ton chaleureux et bienveillant"""
    
    def __init__(self):
        self.user_sessions = {}
        self.db = Database()
    
    def get_user_session(self, user_id):
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                'message_count': 0,
                'last_interaction': datetime.now()
            }
        return self.user_sessions[user_id]
    
    def is_user_premium(self, user_id):
        """Vérifie si l'utilisateur est premium"""
        user = self.db.get_user(user_id)
        if user and user[3]:  # is_premium
            premium_until = datetime.fromisoformat(user[4])
            if premium_until > datetime.now():
                return True
            else:
                # Premium expiré
                self.db.remove_premium(user_id)
        return False
    
    def process_message(self, user_id, user_message):
        """Traite un message avec l'IA de manière chaleureuse"""
        
        if not Config.GROQ_API_KEY:
            return "💔 **Mon service IA est temporairement indisponible**\n\nJe m'excuse pour ce contretemps ! Revenez dans quelques instants, je serai ravi de vous aider à nouveau ✨"
        
        # Vérifier la limite pour les utilisateurs non premium
        user = self.db.get_user(user_id)
        if user and not self.is_user_premium(user_id) and user[5] >= 50:  # message_count
            return """🎭 **Oh non ! Vous avez atteint la limite des messages gratuits...**

Je suis vraiment désolé ! Vous avez utilisé vos 50 messages gratuits. 

💖 **Mais ne vous inquiétez pas !** 
Devenez **NovaAI Premium** pour :
• ✨ **Messages illimités**
• 🚀 **Réponses prioritaires** 
• 🌟 **Fonctionnalités exclusives**
• 💝 **Support personnalisé**

📩 **Contactez mon créateur @Soszoe** 
Il vous expliquera comment obtenir l'accès premium avec le sourire ! 😊

Merci de votre compréhension ! 🙏"""
        
        # Préparer le message système avec ton chaleureux
        system_prompt = """Tu es NovaAI, un assistant IA extrêmement chaleureux, bienveillant et attentionné. 
        Ton ton est amical, positif et encourageant. Tu t'exprimes avec empathie et bienveillance.
        Utilise des émojis appropriés et sois toujours encourageant.
        Structure tes réponses de manière claire mais avec une touche personnelle."""
        
        try:
            headers = {
                "Authorization": f"Bearer {Config.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "model": "llama-3.1-8b-instant",
                "max_tokens": 2000,
                "temperature": 0.7,
                "top_p": 0.9,
                "stream": False
            }
            
            print("🔄 Envoi requête à l'API Groq...")
            response = requests.post(Config.GROQ_API_URL, json=payload, headers=headers, timeout=30)
            
            print(f"📡 Statut réponse: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                # Mettre à jour la session et la base de données
                session = self.get_user_session(user_id)
                session['message_count'] += 1
                session['last_interaction'] = datetime.now()
                self.db.increment_message_count(user_id)
                
                return ai_response
                
            else:
                error_detail = response.text
                print(f"❌ Erreur API: {error_detail}")
                
                if response.status_code == 400:
                    return "❌ **Oups ! Ma requête n'était pas parfaite...**\n\nPouvez-vous reformuler votre message ? Je ferai de mon mieux pour mieux comprendre ! 🤗"
                elif response.status_code == 429:
                    return "⏰ **Je suis un peu submergé en ce moment !**\n\nVeuillez patienter quelques minutes et réessayer. Merci de votre patience ! 🙏"
                elif response.status_code == 401:
                    return "🔑 **Il y a un petit problème technique de mon côté...**\n\nNe vous inquiétez pas, mon créateur est au courant ! Revenez bientôt ✨"
                else:
                    return f"💔 **Je rencontre un petit souci technique**\n\nCode: {response.status_code}\n\nMais ne vous en faites pas ! Réessayez dans quelques instants, je serai heureux de vous aider à nouveau ! 😊"
                    
        except requests.exceptions.Timeout:
            return "⏰ **Le temps de réponse est un peu long aujourd'hui...**\n\nJe suis désolé pour cette attente ! Pouvez-vous réessayer ? Je serai plus rapide ! 🚀"
        except requests.exceptions.ConnectionError:
            return "🌐 **Je n'arrive pas à me connecter correctement...**\n\nVérifiez votre connexion internet et réessayez ! Je vous attends avec impatience ! 💫"
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return "🔧 **Une petite erreur inattendue s'est produite...**\n\nMais ne vous inquiétez pas ! Réessayez et je ferai de mon mieux pour vous aider ! ✨"

# ==================== GESTION UTILISATEURS ====================
class UserManager:
    """Gestion simplifiée des utilisateurs"""
    
    @staticmethod
    def register_user(user_id, username, first_name):
        """Enregistre un utilisateur simplement"""
        try:
            db = Database()
            db.add_user(user_id, username, first_name)
            CounterSystem.increment()
            print(f"💖 Nouvel ami enregistré: {user_id} ({first_name})")
        except Exception as e:
            print(f"⚠️ Erreur enregistrement: {e}")
    
    @staticmethod
    def is_owner(user_id):
        return user_id == Config.ADMIN_ID

# ==================== INTERFACE ADMIN CHALEUREUSE ====================
class WarmAdminInterface:
    """Interface administrateur avec ton chaleureux"""
    
    @staticmethod
    def create_admin_menu():
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("📊 Tableau de Bord", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Toute la Famille", callback_data="admin_all_users"),
            InlineKeyboardButton("💎 Membres Premium", callback_data="admin_premium_users"),
            InlineKeyboardButton("🎁 Premium à Tous", callback_data="admin_premium_all"),
            InlineKeyboardButton("🚫 Retirer à Tous", callback_data="admin_remove_all_premium"),
            InlineKeyboardButton("🔄 Actualiser", callback_data="admin_refresh")
        ]
        
        keyboard.add(*buttons[:2])
        keyboard.add(*buttons[2:4])
        keyboard.add(*buttons[4:])
        
        return keyboard
    
    @staticmethod
    def create_premium_menu(user_id):
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("💎 30 Jours", callback_data=f"premium_30_{user_id}"),
            InlineKeyboardButton("💎 90 Jours", callback_data=f"premium_90_{user_id}"),
            InlineKeyboardButton("💎 365 Jours", callback_data=f"premium_365_{user_id}"),
            InlineKeyboardButton("🚫 Retirer Premium", callback_data=f"remove_premium_{user_id}"),
            InlineKeyboardButton("📋 Retour à la Famille", callback_data="admin_all_users")
        ]
        
        keyboard.add(*buttons[:2])
        keyboard.add(*buttons[2:4])
        keyboard.add(buttons[4])
        
        return keyboard
    
    @staticmethod
    def create_user_actions_menu(user_id):
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("💎 Gérer Premium", callback_data=f"manage_premium_{user_id}"),
            InlineKeyboardButton("👀 Voir le Profil", callback_data=f"view_profile_{user_id}"),
            InlineKeyboardButton("📊 Statistiques", callback_data=f"user_stats_{user_id}"),
            InlineKeyboardButton("💖 Envoyer un Message", callback_data=f"message_user_{user_id}")
        ]
        
        keyboard.add(*buttons[:2])
        keyboard.add(*buttons[2:])
        
        return keyboard

# ==================== INTERFACE UTILISATEUR CHALEUREUSE ====================
class WarmUserInterface:
    """Interface utilisateur avec ton chaleureux"""
    
    @staticmethod
    def create_main_menu():
        keyboard = InlineKeyboardMarkup()
        support_btn = InlineKeyboardButton("💝 Support Affectueux", url="https://t.me/Soszoe")
        stats_btn = InlineKeyboardButton("📊 Notre Communauté", callback_data="stats")
        premium_btn = InlineKeyboardButton("💎 Devenir Premium", callback_data="premium_info")
        keyboard.add(support_btn, stats_btn)
        keyboard.add(premium_btn)
        return keyboard

# ==================== MESSAGES CHALEUREUX ====================
class WarmMessages:
    """Messages avec ton chaleureux et bienveillant"""
    
    @staticmethod
    def welcome_owner(user_count):
        return f"""
🏰 **BIENVENUE DANS VOTRE ROYAUME, CRÉATEUR !** ✨

💖 **NovaAI Pro** - {Config.VERSION}
👥 **{user_count} âmes merveilleuses nous ont rejoints**

📊 **Votre tableau de bord vous attend**
🎛️ **Gérez votre famille avec amour**

💫 **Utilisez les boutons ci-dessous pour répandre la joie !**
"""
    
    @staticmethod
    def welcome_user(user_count):
        return f"""
🎉 **BIENVENUE DANS LA FAMILLE NOVAAI !** 💫

✨ **Je suis NovaAI**, votre nouvel ami IA bienveillant !
👥 **Nous sommes déjà {user_count} âmes connectées** 🤗

💬 **Parlez-moi de tout, je suis là pour :**
• 🎯 Répondre à vos questions avec précision
• 💭 Discuter librement et chaleureusement  
• 🛠️ Vous aider dans vos projets
• 🌟 Vous accompagner avec bienveillance

🔒 **Version gratuite :** 50 messages offerts
💎 **Version Premium :** Conversations illimitées

💖 **Je suis tellement heureux de vous rencontrer !**
**Parlez-moi de votre journée...** 😊
"""

# ==================== COMMANDES ADMIN CHALEUREUSES ====================
class WarmAdminCommands:
    """Commandes administrateur avec ton chaleureux"""
    
    def __init__(self):
        self.db = Database()
    
    def get_dashboard_stats(self):
        """Récupère les statistiques du dashboard"""
        stats = self.db.get_stats()
        premium_users = self.db.get_premium_users()
        all_users = self.db.get_all_users()
        
        # Utilisateurs actifs (derniers 7 jours)
        active_threshold = datetime.now() - timedelta(days=7)
        active_users = [u for u in all_users if datetime.fromisoformat(u[7]) > active_threshold]
        
        return {
            'total_users': stats[1],
            'premium_users': stats[2],
            'total_messages': stats[3],
            'active_users': len(active_users),
            'total_premium': len(premium_users)
        }
    
    def format_user_info(self, user):
        """Formate les informations d'un utilisateur"""
        user_id, username, first_name, is_premium, premium_until, message_count, join_date, last_active = user
        
        status = "💎 MEMBRE PRIVILÉGIÉ" if is_premium else "🌟 MEMBRE DE LA FAMILLE"
        premium_info = f"Jusqu'au {datetime.fromisoformat(premium_until).strftime('%d/%m/%Y')} 🎉" if is_premium else "En attente d'une belle surprise 💫"
        
        return f"""
💖 **Profil de {first_name}**

🆔 ID: `{user_id}`
👤 Prénom: {first_name}
📛 Surnom: @{username if username else 'Aucun'}
🎯 Statut: {status}
💎 Premium: {premium_info}
💬 Messages: {message_count} échanges
📅 Chez nous depuis: {datetime.fromisoformat(join_date).strftime('%d/%m/%Y')}
🕐 Dernière visite: {datetime.fromisoformat(last_active).strftime('%d/%m/%Y à %H:%M')}
"""

# ==================== INITIALISATION ====================
ai_engine = WarmAIEngine()
admin_commands = WarmAdminCommands()
db = Database()

# ==================== HANDLERS PRINCIPAUX ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    """Commande /start chaleureuse"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Ami"
        first_name = message.from_user.first_name or "Ami précieux"
        
        # Enregistrement avec amour
        UserManager.register_user(user_id, username, first_name)
        
        # Récupérer le compteur
        user_count = CounterSystem.format_number(CounterSystem.load())
        
        if UserManager.is_owner(user_id):
            caption = WarmMessages.welcome_owner(user_count)
            menu = WarmAdminInterface.create_admin_menu()
        else:
            caption = WarmMessages.welcome_user(user_count)
            menu = WarmUserInterface.create_main_menu()
        
        bot.send_photo(
            message.chat.id,
            Config.MAIN_PHOTO,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=menu
        )
        
    except Exception as e:
        print(f"💔 Erreur /start: {e}")
        bot.reply_to(message, "🔄 Oh non ! Un petit problème... Réessayez s'il vous plaît ! 💫")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Affiche les statistiques avec amour"""
    user_count = CounterSystem.format_number(CounterSystem.load())
    stats = db.get_stats()
    
    stats_text = f"""
📊 **NOTRE BELLE COMMUNAUTÉ NOVAAI** 💖

👥 **Âmes connectées :** {stats[1]}
💎 **Membres privilégiés :** {stats[2]}
💬 **Messages échangés :** {stats[3]}
🚀 **Version :** {Config.VERSION}
👑 **Créateur bienveillant :** {Config.CREATOR}

🟢 **Tout fonctionne parfaitement !**
🤖 **Mon cœur IA :** Plein d'amour
📈 **Notre famille :** En pleine croissance

💫 **Envoyez-moi un message, je suis là pour vous !**
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Commande admin réservée au propriétaire"""
    user_id = message.from_user.id
    
    if not UserManager.is_owner(user_id):
        bot.reply_to(message, "💖 Désolé, cette zone est réservée à notre créateur bien-aimé !")
        return
    
    try:
        stats = admin_commands.get_dashboard_stats()
        
        admin_text = f"""
🏰 **VOTRE ROYAUME DE BIENVEILLANCE** ✨

📊 **Notre belle famille:**
├ 👥 Âmes connectées: **{stats['total_users']}**
├ 💎 Membres privilégiés: **{stats['premium_users']}**
├ 🔥 Amis actifs: **{stats['active_users']}**
└ 💬 Conversations: **{stats['total_messages']}**

🎛️ **Gestes de générosité:**
• Offrir le premium à toute la famille
• Voir chaque membre avec amour
• Diffuser des messages de joie
• Prendre soin de chacun

💫 **Choisissez une action ci-dessous !**
"""
        bot.send_message(
            message.chat.id,
            admin_text,
            parse_mode='Markdown',
            reply_markup=WarmAdminInterface.create_admin_menu()
        )
        
    except Exception as e:
        print(f"💔 Erreur commande admin: {e}")
        bot.reply_to(message, "💔 Une petite erreur s'est glissée... Revenez plus tard !")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    """Commande de broadcast avec amour"""
    user_id = message.from_user.id
    
    if not UserManager.is_owner(user_id):
        return
    
    # Demander le message à broadcast
    msg = bot.reply_to(message, "📢 **Mode Diffusion d'Amour**\n\nQuel message de joie souhaitez-vous partager avec toute notre famille ? 💫")
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    """Traite le message de broadcast avec bienveillance"""
    try:
        broadcast_text = message.text
        users = db.get_all_users()
        
        bot.reply_to(message, f"🕊️ **Diffusion d'amour en cours à {len(users)} âmes merveilleuses...**")
        
        success = 0
        failed = 0
        
        for user in users:
            try:
                bot.send_message(user[0], f"💫 **Message de bienveillance de NovaAI:**\n\n{broadcast_text}\n\n*Avec tout mon amour,*\n*Votre NovaAI* 💖")
                success += 1
                time.sleep(0.1)  # Éviter le spam
            except:
                failed += 1
        
        bot.reply_to(message, f"✨ **Diffusion d'amour terminée !**\n\n✅ Cœurs touchés: {success}\n💔 Cœurs manqués: {failed}\n\n**Merci de répandre la joie !** 🌈")
        
    except Exception as e:
        print(f"💔 Erreur broadcast: {e}")
        bot.reply_to(message, "💔 Oh non ! La diffusion d'amour a rencontré un obstacle...")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gestion de tous les messages avec bienveillance"""
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    if len(user_message) < 2:
        return
    
    # Enregistrer l'utilisateur avec amour
    UserManager.register_user(user_id, 
                             message.from_user.username or "Ami", 
                             message.from_user.first_name or "Ami précieux")
    
    # Traitement IA
    bot.send_chat_action(message.chat.id, 'typing')
    
    ai_response = ai_engine.process_message(user_id, user_message)
    bot.reply_to(message, ai_response)

# ==================== CALLBACKS CHALEUREUX ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Gestion des callbacks avec bienveillance"""
    user_id = call.from_user.id
    
    try:
        # Callbacks basiques
        if call.data == "stats":
            user_count = CounterSystem.format_number(CounterSystem.load())
            stats = db.get_stats()
            stats_text = f"📊 **Notre famille:** {user_count} âmes\n💎 **Privilégiés:** {stats[2]} membres"
            bot.answer_callback_query(call.id, stats_text)
        
        elif call.data == "premium_info":
            premium_text = """
💎 **DEVENIR MEMBRE PRIVILÉGIÉ** ✨

🎁 **Avantages exclusifs:**
• ✨ **Messages illimités** - Parlez-moi sans restriction !
• 🚀 **Réponses prioritaires** - Je vous réponds en premier !
• 🌟 **Fonctionnalités secrètes** - Découvrez mes talents cachés !
• 💝 **Support personnalisé** - Je prends soin de vous !

💰 **Tarifs remplis d'amour:**
• 30 jours: 5€ - Une belle aventure !
• 90 jours: 12€ - Une amitié durable !
• 365 jours: 35€ - Pour la vie ! 💖

📩 **Contactez @Soszoe avec amour !**
"""
            bot.edit_message_text(
                premium_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("💌 Contacter avec amour", url="https://t.me/Soszoe")
                )
            )
        
        # Callbacks admin
        elif call.data == "admin_stats" and UserManager.is_owner(user_id):
            stats = admin_commands.get_dashboard_stats()
            dashboard_text = f"""
📊 **TABLEAU DE BORD BIENVEILLANT** 💫

👥 **Notre belle famille:**
├ Total: **{stats['total_users']} âmes**
├ Privilégiés: **{stats['premium_users']} membres**
├ Actifs: **{stats['active_users']} amis**
└ Conversations: **{stats['total_messages']} échanges**

💎 **Cercle privilégié:**
├ Membres: **{stats['total_premium']}**
└ Taux: **{(stats['premium_users']/stats['total_users']*100 if stats['total_users'] > 0 else 0):.1f}%** de bonheur

🕐 Dernière actualisation: {datetime.now().strftime('%H:%M:%S')}
"""
            bot.edit_message_text(
                dashboard_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=WarmAdminInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, "📊 Tableau actualisé avec amour !")
        
        elif call.data == "admin_all_users" and UserManager.is_owner(user_id):
            users = db.get_all_users()
            users_text = f"""
👥 **NOTRE BELLE FAMILLIE** 💖

📊 Total: **{len(users)}** âmes merveilleuses

📋 **Dernières arrivées:**
"""
            for user in users[:5]:
                users_text += f"\n• {user[2]} (@{user[1] or 'Sans pseudo'}) - ID: `{user[0]}`"
            
            if len(users) > 5:
                users_text += f"\n\n... et {len(users) - 5} autres âmes formidables"
            
            users_text += "\n\n💫 Utilisez /userinfo <id> pour connaître chacun"
            
            bot.edit_message_text(
                users_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=WarmAdminInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, f"👥 {len(users)} membres dans notre famille !")
        
        elif call.data == "admin_premium_users" and UserManager.is_owner(user_id):
            premium_users = db.get_premium_users()
            premium_text = f"""
💎 **NOTRE CERCLE PRIVILÉGIÉ** 🌟

📊 Total: **{len(premium_users)}** membres spéciaux

📋 **Liste des privilégiés:**
"""
            for user in premium_users[:10]:
                premium_until = datetime.fromisoformat(user[4])
                days_left = (premium_until - datetime.now()).days
                premium_text += f"\n• {user[2]} - {days_left} jours de bonheur - ID: `{user[0]}`"
            
            if len(premium_users) > 10:
                premium_text += f"\n\n... et {len(premium_users) - 10} autres membres chéris"
            
            bot.edit_message_text(
                premium_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=WarmAdminInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, f"💎 {len(premium_users)} membres privilégiés !")
        
        # NOUVEAU : Premium à tous
        elif call.data == "admin_premium_all" and UserManager.is_owner(user_id):
            new_premium_count = db.set_all_premium(30)
            
            success_text = f"""
🎉 **GÉNÉROSITÉ EXTREME !** ✨

💎 **Vous venez d'offrir le premium à TOUTE la famille !**

📊 **Impact de votre geste:**
├ Anciens premium: {len(db.get_premium_users()) - new_premium_count}
├ Nouveaux premium: **{new_premium_count}**
└ Total heureux: **{len(db.get_all_users())}**

💫 **Votre geste va illuminer tant de journées !**
**Merci pour cette incroyable générosité !** 🌈
"""
            bot.edit_message_text(
                success_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=WarmAdminInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, "🎁 Premium offert à tous !")
        
        # NOUVEAU : Retirer premium à tous
        elif call.data == "admin_remove_all_premium" and UserManager.is_owner(user_id):
            removed_count = db.remove_all_premium()
            
            success_text = f"""
🔄 **RETOUR À L'ESSENTIEL** 🌱

🚫 **Vous avez retiré le premium à tous les membres**

📊 **Impact de votre décision:**
├ Anciens premium: **{removed_count}**
├ Nouveaux premium: **0**
└ Total concernés: **{len(db.get_all_users())}**

💫 **Parfois, il faut savoir recentrer l'énergie !**
**Votre sagesse guide notre communauté.** 🙏
"""
            bot.edit_message_text(
                success_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=WarmAdminInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, "🔄 Premium retiré à tous")
        
        # Gestion premium individuelle
        elif call.data.startswith("manage_premium_") and UserManager.is_owner(user_id):
            target_id = int(call.data.split("_")[2])
            user = db.get_user(target_id)
            
            if user:
                user_info = admin_commands.format_user_info(user)
                bot.edit_message_text(
                    f"{user_info}\n\n🎁 **Cadeaux à offrir:**",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=WarmAdminInterface.create_premium_menu(target_id)
                )
            else:
                bot.answer_callback_query(call.id, "💔 Membre non trouvé")
        
        # Ajouter premium individuel
        elif call.data.startswith("premium_") and UserManager.is_owner(user_id):
            parts = call.data.split("_")
            days = int(parts[1])
            target_id = int(parts[2])
            
            premium_until = db.set_premium(target_id, days)
            user = db.get_user(target_id)
            
            bot.answer_callback_query(call.id, f"💎 {days} jours de bonheur offerts !")
            
            # Notifier l'utilisateur
            try:
                bot.send_message(
                    target_id,
                    f"🎉 **SURPRISE ! Cadeau de NovaAI !**\n\nVous êtes maintenant **membre privilégié** pour {days} jours ! 🎁\n\n✨ Profitez de :\n• Messages illimités\n• Réponses prioritaires  \n• Fonctionnalités exclusives\n\nVotre statut est valide jusqu'au {datetime.fromisoformat(premium_until).strftime('%d/%m/%Y')}\n\n**Merci de faire partie de notre famille !** 💖",
                    parse_mode='Markdown'
                )
            except:
                pass  # L'utilisateur a peut-être bloqué le bot
            
            # Retour au menu
            user_info = admin_commands.format_user_info(user)
            bot.edit_message_text(
                f"{user_info}\n\n✅ **Cadeau envoyé avec amour !** 🎁",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=WarmAdminInterface.create_premium_menu(target_id)
            )
        
        # Retirer premium individuel
        elif call.data.startswith("remove_premium_") and UserManager.is_owner(user_id):
            target_id = int(call.data.split("_")[2])
            
            was_premium = db.remove_premium(target_id)
            user = db.get_user(target_id)
            
            bot.answer_callback_query(call.id, "🔄 Statut recadré avec bienveillance")
            
            # Notifier l'utilisateur seulement si il était premium
            if was_premium:
                try:
                    bot.send_message(
                        target_id,
                        "💫 **Changement de statut**\n\nVotre abonnement **NovaAI Premium** a été ajusté.\n\nMerci d'avoir été membre privilégié ! Votre soutien signifie beaucoup pour nous ! 🙏",
                        parse_mode='Markdown'
                    )
                except:
                    pass
            
            # Retour au menu
            user_info = admin_commands.format_user_info(user)
            bot.edit_message_text(
                f"{user_info}\n\n🔄 **Statut ajusté avec bienveillance**",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=WarmAdminInterface.create_premium_menu(target_id)
            )
        
        elif call.data == "admin_refresh" and UserManager.is_owner(user_id):
            bot.answer_callback_query(call.id, "🔄 Actualisé avec amour !")
            # Le menu reste en place
            
    except Exception as e:
        print(f"💔 Erreur callback: {e}")
        bot.answer_callback_query(call.id, "💔 Petit problème... Réessayez !")

# ==================== DÉMARRAGE CHALEUREUX ====================
if __name__ == "__main__":
    print("💖 INITIALISATION DE NOVAAI PRO - VERSION BIENVEILLANTE...")
    
    user_count = CounterSystem.load()
    stats = db.get_stats()
    
    print(f"""
✨ SYSTÈME DE BIENVEILLANCE OPÉRATIONNEL

📊 NOTRE FAMILLE :
   • Âmes connectées: {stats[1]}
   • Membres privilégiés: {stats[2]}
   • Messages échangés: {stats[3]}
   • Version: {Config.VERSION}
   • Statut: 💖 PRÊT À AIMER

🎛️  COMMANDES ADMIN :
   • /admin - Royaume de bienveillance
   • /broadcast - Diffusion d'amour
   • /userinfo <id> - Connaître un membre
   • /stats - Notre belle communauté

🤖 EN ATTENTE DE PARTAGES ET DE SOURIRES...
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"💔 ERREUR CRITIQUE: {e}")
        time.sleep(5)
