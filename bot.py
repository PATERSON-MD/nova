#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 NOVA-AI ULTIMATE - CORRIGÉ AVEC SYSTÈME PREMIUM
💎 Édition STABLE avec gestion d'erreurs
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

# ==================== CONFIGURATION SIMPLIFIÉE ====================
class Config:
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
    
    CREATOR = "👑 Kervens"
    BOT_NAME = "🚀 NovaAI Pro"
    VERSION = "💎 Édition Premium"
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
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, join_date, last_active) 
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, join_date, join_date))
        
        # Mettre à jour les statistiques
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
        
        cursor.execute('''
            UPDATE users 
            SET is_premium = 1, premium_until = ?
            WHERE user_id = ?
        ''', (premium_until, user_id))
        
        # Mettre à jour les statistiques premium
        cursor.execute('UPDATE stats SET premium_users = premium_users + 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
        
        return premium_until
    
    def remove_premium(self, user_id):
        """Retire le statut premium d'un utilisateur"""
        conn = sqlite3.connect('nova_users.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET is_premium = 0, premium_until = NULL
            WHERE user_id = ?
        ''', (user_id,))
        
        cursor.execute('UPDATE stats SET premium_users = premium_users - 1 WHERE id = 1')
        
        conn.commit()
        conn.close()
    
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

# ==================== MOTEUR IA CORRIGÉ ====================
class SimpleAIEngine:
    """Moteur IA simplifié et stable"""
    
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
        """Traite un message avec l'IA de manière stable"""
        
        if not Config.GROQ_API_KEY:
            return "❌ **Service IA temporairement indisponible**\n\nConfiguration manquante."
        
        # Vérifier la limite pour les utilisateurs non premium
        user = self.db.get_user(user_id)
        if user and not self.is_user_premium(user_id) and user[5] >= 50:  # message_count
            return "🔒 **Limite de messages atteinte**\n\nVous avez atteint la limite de 50 messages gratuits.\n\n💎 Passez à **NovaAI Premium** pour des messages illimités !\n\nContactez @Soszoe pour plus d'informations."
        
        # Préparer le message système
        system_prompt = """Tu es NovaAI, un assistant IA utile et professionnel. 
        Sois concis, précis et utilise un ton amical. 
        Structure tes réponses de manière claire."""
        
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
                    return "❌ **Erreur de requête**\n\nLe format de la requête est incorrect. Réessayez avec un message plus simple."
                elif response.status_code == 429:
                    return "⏰ **Limite de requêtes atteinte**\n\nVeuillez réessayer dans quelques minutes."
                elif response.status_code == 401:
                    return "🔑 **Problème d'authentification**\n\nLa clé API est invalide."
                else:
                    return f"❌ **Erreur de service**\n\nCode: {response.status_code}\n\nVeuillez réessayer."
                    
        except requests.exceptions.Timeout:
            return "⏰ **Délai dépassé**\n\nLa requête a pris trop de temps. Réessayez."
        except requests.exceptions.ConnectionError:
            return "🌐 **Problème de connexion**\n\nVérifiez votre connexion internet."
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return "🔧 **Erreur technique**\n\nUne erreur inattendue s'est produite. Réessayez."

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
            print(f"✅ Utilisateur enregistré: {user_id} ({first_name})")
        except Exception as e:
            print(f"⚠️ Erreur enregistrement: {e}")
    
    @staticmethod
    def is_owner(user_id):
        return user_id == Config.ADMIN_ID

# ==================== INTERFACE ADMIN AVANCÉE ====================
class AdminInterface:
    """Interface administrateur avancée"""
    
    @staticmethod
    def create_admin_menu():
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        buttons = [
            InlineKeyboardButton("📊 Dashboard", callback_data="admin_stats"),
            InlineKeyboardButton("👥 Tous les users", callback_data="admin_all_users"),
            InlineKeyboardButton("💎 Users Premium", callback_data="admin_premium_users"),
            InlineKeyboardButton("🔍 Chercher user", callback_data="admin_search_user"),
            InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast"),
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
            InlineKeyboardButton("📋 Retour", callback_data="admin_all_users")
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
            InlineKeyboardButton("👀 Voir profil", callback_data=f"view_profile_{user_id}"),
            InlineKeyboardButton("📊 Stats user", callback_data=f"user_stats_{user_id}"),
            InlineKeyboardButton("🗑️ Supprimer", callback_data=f"delete_user_{user_id}")
        ]
        
        keyboard.add(*buttons[:2])
        keyboard.add(*buttons[2:])
        
        return keyboard

# ==================== INTERFACE SIMPLE ====================
class SimpleInterface:
    """Interface utilisateur simplifiée"""
    
    @staticmethod
    def create_main_menu():
        keyboard = InlineKeyboardMarkup()
        support_btn = InlineKeyboardButton("💝 Support", url="https://t.me/Soszoe")
        stats_btn = InlineKeyboardButton("📊 Statistiques", callback_data="stats")
        premium_btn = InlineKeyboardButton("💎 Devenir Premium", callback_data="premium_info")
        keyboard.add(support_btn, stats_btn)
        keyboard.add(premium_btn)
        return keyboard
    
    @staticmethod
    def create_owner_menu():
        return AdminInterface.create_admin_menu()

# ==================== MESSAGES SIMPLES ====================
class SimpleMessages:
    """Messages simplifiés"""
    
    @staticmethod
    def welcome_owner(user_count):
        return f"""
🏰 **BIENVENUE PROPRIÉTAIRE !**

🚀 **NovaAI Pro** - {Config.VERSION}
👥 **{user_count} utilisateurs mensuels**

📊 **Tableau de bord disponible**
🎛️ **Contrôles administrateur avancés**

💡 **Utilisez les boutons ci-dessous !**
"""
    
    @staticmethod
    def welcome_user(user_count):
        return f"""
🎉 **BIENVENUE SUR NOVAAI PRO !**

🚀 L'assistant IA le plus avancé
👥 Rejoignez nos **{user_count}** utilisateurs

💬 **Envoyez-moi un message pour :**
• Poser des questions
• Discuter librement  
• Obtenir de l'aide
• Explorer des sujets

🔒 **Limite :** 50 messages gratuits
💎 **Premium :** Messages illimités

✨ **Je suis là pour vous aider !**
"""

# ==================== COMMANDES ADMIN ====================
class AdminCommands:
    """Commandes administrateur étendues"""
    
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
        
        status = "💎 PREMIUM" if is_premium else "🔓 STANDARD"
        premium_info = f"Jusqu'au {datetime.fromisoformat(premium_until).strftime('%d/%m/%Y')}" if is_premium else "Non premium"
        
        return f"""
👤 **Informations Utilisateur**

🆔 ID: `{user_id}`
👤 Nom: {first_name}
📛 Username: @{username if username else 'N/A'}
🎯 Statut: {status}
📅 Premium: {premium_info}
💬 Messages: {message_count}
📅 Inscrit: {datetime.fromisoformat(join_date).strftime('%d/%m/%Y')}
🕐 Dernière activité: {datetime.fromisoformat(last_active).strftime('%d/%m/%Y %H:%M')}
"""

# ==================== INITIALISATION ====================
ai_engine = SimpleAIEngine()
admin_commands = AdminCommands()
db = Database()

# ==================== HANDLERS PRINCIPAUX ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    """Commande /start simplifiée"""
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        # Enregistrement simple
        UserManager.register_user(user_id, username, first_name)
        
        # Récupérer le compteur
        user_count = CounterSystem.format_number(CounterSystem.load())
        
        if UserManager.is_owner(user_id):
            caption = SimpleMessages.welcome_owner(user_count)
            menu = SimpleInterface.create_owner_menu()
        else:
            caption = SimpleMessages.welcome_user(user_count)
            menu = SimpleInterface.create_main_menu()
        
        bot.send_photo(
            message.chat.id,
            Config.MAIN_PHOTO,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=menu
        )
        
    except Exception as e:
        print(f"❌ Erreur /start: {e}")
        bot.reply_to(message, "🔄 Veuillez réessayer...")

@bot.message_handler(commands=['stats'])
def stats_command(message):
    """Affiche les statistiques"""
    user_count = CounterSystem.format_number(CounterSystem.load())
    stats = db.get_stats()
    
    stats_text = f"""
📊 **STATISTIQUES NOVAAI**

👥 **Utilisateurs totaux :** {stats[1]}
💎 **Utilisateurs premium :** {stats[2]}
💬 **Messages totaux :** {stats[3]}
🚀 **Version :** {Config.VERSION}
👑 **Créateur :** {Config.CREATOR}

🟢 **Système opérationnel**
🤖 **IA :** Active
📈 **Croissance :** Stable

💡 **Envoyez un message pour tester l'IA !**
"""
    bot.reply_to(message, stats_text, parse_mode='Markdown')

@bot.message_handler(commands=['admin'])
def admin_command(message):
    """Commande admin réservée au propriétaire"""
    user_id = message.from_user.id
    
    if not UserManager.is_owner(user_id):
        bot.reply_to(message, "❌ Accès refusé. Commande réservée au propriétaire.")
        return
    
    try:
        stats = admin_commands.get_dashboard_stats()
        
        admin_text = f"""
🏰 **PANEL ADMINISTRATEUR**

📊 **Statistiques Globales:**
├ 👥 Utilisateurs totaux: **{stats['total_users']}**
├ 💎 Utilisateurs premium: **{stats['premium_users']}**
├ 🔥 Utilisateurs actifs: **{stats['active_users']}**
└ 💬 Messages totaux: **{stats['total_messages']}**

🎛️ **Actions Disponibles:**
• Gérer les utilisateurs premium
• Voir les statistiques détaillées
• Envoyer des broadcasts
• Gérer les comptes utilisateurs

💡 **Utilisez les boutons ci-dessous !**
"""
        bot.send_message(
            message.chat.id,
            admin_text,
            parse_mode='Markdown',
            reply_markup=AdminInterface.create_admin_menu()
        )
        
    except Exception as e:
        print(f"❌ Erreur commande admin: {e}")
        bot.reply_to(message, "❌ Erreur lors du chargement du panel admin.")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    """Commande de broadcast réservée au propriétaire"""
    user_id = message.from_user.id
    
    if not UserManager.is_owner(user_id):
        return
    
    # Demander le message à broadcast
    msg = bot.reply_to(message, "📢 **Mode Broadcast**\n\nVeuillez envoyer le message que vous souhaitez diffuser à tous les utilisateurs :")
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    """Traite le message de broadcast"""
    try:
        broadcast_text = message.text
        users = db.get_all_users()
        
        bot.reply_to(message, f"🔄 Diffusion en cours à {len(users)} utilisateurs...")
        
        success = 0
        failed = 0
        
        for user in users:
            try:
                bot.send_message(user[0], f"📢 **Annonce de l'équipe NovaAI:**\n\n{broadcast_text}")
                success += 1
                time.sleep(0.1)  # Éviter le spam
            except:
                failed += 1
        
        bot.reply_to(message, f"✅ **Broadcast terminé !**\n\n✅ Succès: {success}\n❌ Échecs: {failed}")
        
    except Exception as e:
        print(f"❌ Erreur broadcast: {e}")
        bot.reply_to(message, "❌ Erreur lors du broadcast.")

@bot.message_handler(commands=['userinfo'])
def userinfo_command(message):
    """Commande pour voir les infos d'un utilisateur"""
    user_id = message.from_user.id
    
    if not UserManager.is_owner(user_id):
        return
    
    try:
        # Vérifier si un ID utilisateur est fourni
        if len(message.text.split()) > 1:
            target_id = int(message.text.split()[1])
            user = db.get_user(target_id)
            
            if user:
                user_info = admin_commands.format_user_info(user)
                bot.reply_to(message, user_info, parse_mode='Markdown')
            else:
                bot.reply_to(message, "❌ Utilisateur non trouvé.")
        else:
            bot.reply_to(message, "❌ Usage: /userinfo <user_id>")
            
    except ValueError:
        bot.reply_to(message, "❌ ID utilisateur invalide.")
    except Exception as e:
        print(f"❌ Erreur userinfo: {e}")
        bot.reply_to(message, "❌ Erreur lors de la récupération des informations.")

@bot.message_handler(func=lambda message: True)
def message_handler(message):
    """Gestion de tous les messages"""
    if message.chat.type in ['group', 'supergroup']:
        return
        
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    if len(user_message) < 2:
        return
    
    # Enregistrer l'utilisateur
    UserManager.register_user(user_id, 
                             message.from_user.username or "User", 
                             message.from_user.first_name or "User")
    
    # Traitement IA
    bot.send_chat_action(message.chat.id, 'typing')
    
    ai_response = ai_engine.process_message(user_id, user_message)
    bot.reply_to(message, ai_response)

# ==================== CALLBACKS AVANCÉS ====================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    """Gestion des callbacks"""
    user_id = call.from_user.id
    
    try:
        # Callbacks basiques
        if call.data == "stats":
            user_count = CounterSystem.format_number(CounterSystem.load())
            stats = db.get_stats()
            stats_text = f"📊 **Statistiques:** {user_count} utilisateurs mensuels\n💎 **Premium:** {stats[2]} utilisateurs"
            bot.answer_callback_query(call.id, stats_text)
        
        elif call.data == "premium_info":
            premium_text = """
💎 **NOVA AI PREMIUM**

✨ **Avantages:**
• Messages illimités
• Accès prioritaire
• Support dédié
• Nouvelles fonctionnalités en avant-première

💰 **Tarifs:**
• 30 jours: 5€
• 90 jours: 12€
• 365 jours: 35€

📩 Contactez @Soszoe pour devenir Premium !
"""
            bot.edit_message_text(
                premium_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton("📩 Contacter", url="https://t.me/Soszoe")
                )
            )
        
        # Callbacks admin
        elif call.data == "admin_stats" and UserManager.is_owner(user_id):
            stats = admin_commands.get_dashboard_stats()
            dashboard_text = f"""
📊 **DASHBOARD PROPRIÉTAIRE**

👥 **Utilisateurs:**
├ Total: **{stats['total_users']}**
├ Premium: **{stats['premium_users']}**
├ Actifs: **{stats['active_users']}**
└ Messages: **{stats['total_messages']}**

💎 **Premium:**
├ Actifs: **{stats['total_premium']}**
└ Taux: **{(stats['premium_users']/stats['total_users']*100 if stats['total_users'] > 0 else 0):.1f}%**

🕐 Dernière MAJ: {datetime.now().strftime('%H:%M:%S')}
"""
            bot.edit_message_text(
                dashboard_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=AdminInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, "📊 Dashboard actualisé")
        
        elif call.data == "admin_all_users" and UserManager.is_owner(user_id):
            users = db.get_all_users()
            users_text = f"""
👥 **TOUS LES UTILISATEURS**

📊 Total: **{len(users)}** utilisateurs

📋 **Derniers inscrits:**
"""
            for user in users[:5]:  # Afficher les 5 premiers
                users_text += f"\n• {user[2]} (@{user[1] or 'N/A'}) - ID: `{user[0]}`"
            
            if len(users) > 5:
                users_text += f"\n\n... et {len(users) - 5} autres utilisateurs"
            
            users_text += "\n\n💡 Utilisez /userinfo <id> pour les détails"
            
            bot.edit_message_text(
                users_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=AdminInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, f"👥 {len(users)} utilisateurs")
        
        elif call.data == "admin_premium_users" and UserManager.is_owner(user_id):
            premium_users = db.get_premium_users()
            premium_text = f"""
💎 **UTILISATEURS PREMIUM**

📊 Total: **{len(premium_users)}** utilisateurs premium

📋 **Liste des premium:**
"""
            for user in premium_users[:10]:  # Afficher les 10 premiers
                premium_until = datetime.fromisoformat(user[4])
                days_left = (premium_until - datetime.now()).days
                premium_text += f"\n• {user[2]} - {days_left} jours restants - ID: `{user[0]}`"
            
            if len(premium_users) > 10:
                premium_text += f"\n\n... et {len(premium_users) - 10} autres"
            
            bot.edit_message_text(
                premium_text,
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=AdminInterface.create_admin_menu()
            )
            bot.answer_callback_query(call.id, f"💎 {len(premium_users)} premium")
        
        # Gestion premium des utilisateurs
        elif call.data.startswith("manage_premium_") and UserManager.is_owner(user_id):
            target_id = int(call.data.split("_")[2])
            user = db.get_user(target_id)
            
            if user:
                user_info = admin_commands.format_user_info(user)
                bot.edit_message_text(
                    f"{user_info}\n\n🎛️ **Gestion Premium:**",
                    call.message.chat.id,
                    call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=AdminInterface.create_premium_menu(target_id)
                )
            else:
                bot.answer_callback_query(call.id, "❌ Utilisateur non trouvé")
        
        # Ajouter premium
        elif call.data.startswith("premium_") and UserManager.is_owner(user_id):
            parts = call.data.split("_")
            days = int(parts[1])
            target_id = int(parts[2])
            
            premium_until = db.set_premium(target_id, days)
            user = db.get_user(target_id)
            
            bot.answer_callback_query(call.id, f"✅ Premium ajouté: {days} jours")
            
            # Notifier l'utilisateur
            try:
                bot.send_message(
                    target_id,
                    f"🎉 **Félicitations !**\n\nVous êtes maintenant **utilisateur NovaAI Premium** pour {days} jours !\n\n✨ Profitez de tous les avantages :\n• Messages illimités\n• Accès prioritaire\n• Support dédié\n\nVotre abonnement est valide jusqu'au {datetime.fromisoformat(premium_until).strftime('%d/%m/%Y')}",
                    parse_mode='Markdown'
                )
            except:
                pass  # L'utilisateur a peut-être bloqué le bot
            
            # Retour au menu
            user_info = admin_commands.format_user_info(user)
            bot.edit_message_text(
                f"{user_info}\n\n✅ **Premium ajouté avec succès !**",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=AdminInterface.create_premium_menu(target_id)
            )
        
        # Retirer premium
        elif call.data.startswith("remove_premium_") and UserManager.is_owner(user_id):
            target_id = int(call.data.split("_")[2])
            
            db.remove_premium(target_id)
            user = db.get_user(target_id)
            
            bot.answer_callback_query(call.id, "🚫 Premium retiré")
            
            # Notifier l'utilisateur
            try:
                bot.send_message(
                    target_id,
                    "ℹ️ **Changement de statut**\n\nVotre abonnement **NovaAI Premium** a été désactivé.\n\nMerci d'avoir utilisé nos services premium !",
                    parse_mode='Markdown'
                )
            except:
                pass
            
            # Retour au menu
            user_info = admin_commands.format_user_info(user)
            bot.edit_message_text(
                f"{user_info}\n\n🚫 **Premium retiré avec succès !**",
                call.message.chat.id,
                call.message.message_id,
                parse_mode='Markdown',
                reply_markup=AdminInterface.create_premium_menu(target_id)
            )
        
        elif call.data == "admin_refresh" and UserManager.is_owner(user_id):
            bot.answer_callback_query(call.id, "🔄 Actualisé")
            # Simplement fermer la query, le menu reste
            
    except Exception as e:
        print(f"❌ Erreur callback: {e}")
        bot.answer_callback_query(call.id, "❌ Erreur")

# ==================== DÉMARRAGE ====================
if __name__ == "__main__":
    print("🚀 INITIALISATION DE NOVAAI PRO AVEC SYSTÈME PREMIUM...")
    
    user_count = CounterSystem.load()
    stats = db.get_stats()
    
    print(f"""
✅ SYSTÈME PREMIUM OPÉRATIONNEL

📊 STATISTIQUES :
   • Utilisateurs totaux: {stats[1]}
   • Utilisateurs premium: {stats[2]}
   • Messages totaux: {stats[3]}
   • Version: {Config.VERSION}
   • Statut: 🟢 PRÊT

🎛️  COMMANDES ADMIN :
   • /admin - Panel administrateur
   • /broadcast - Diffusion massive
   • /userinfo <id> - Infos utilisateur
   • /stats - Statistiques

🤖 EN ATTENTE DE MESSAGES...
    """)
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        time.sleep(5)
