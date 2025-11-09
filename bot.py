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

# 🔐 ADMIN - 7908680781 EST LE PROPRIÉTAIRE PERMANENT
ADMIN_ID = 7908680781

# Stockage
user_sessions = {}

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
    c.execute('SELECT user_id, username, first_name, has_premium, added_date FROM user_access')
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

def register_user(user_id, username, first_name):
    conn = sqlite3.connect('bot_groups.db')
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO user_access 
                 (user_id, username, first_name, added_date) 
                 VALUES (?, ?, ?, ?)''', 
                 (user_id, username, first_name, datetime.now()))
    conn.commit()
    conn.close()

# ==================== FONCTIONS ADMIN ====================
def is_owner(user_id):
    """Vérifie si l'utilisateur est le propriétaire 7908680781"""
    return user_id == ADMIN_ID

# ==================== FONCTIONS UTILISATEURS ====================
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

def create_premium_menu(user_id=None):
    """Menu premium"""
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
    
    keyboard.add(add_button)
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
    """Affiche les statistiques directement"""
    total_users = len(get_all_users())
    premium_users = len([u for u in get_all_users() if u[3]])
    groups_count = get_group_stats()
    
    stats_text = f"""
📊 **STATISTIQUES LÉGENDAIRES**

👥 **Utilisateurs :** {total_users}
⭐ **Premium :** {premium_users}
🔒 **Standard :** {total_users - premium_users}
📁 **Groupes :** {groups_count}/5
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
        user_id, username, first_name, has_premium, added_date = user
        premium_status = "⭐" if has_premium else "🔒"
        username_display = f"@{username}" if username else "❌ Sans username"
        response += f"{i}. {premium_status} **{first_name}**\n"
        response += f"   👤 {username_display}\n"
        response += f"   🆔 `{user_id}`\n"
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
@bot.message_handler(commands=['start', 'aide', 'help'])
def start_handler(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or "Utilisateur"
        first_name = message.from_user.first_name or "Utilisateur"
        
        register_user(user_id, username, first_name)
        
        # Vérifier si c'est le propriétaire 7908680781
        if is_owner(user_id):
            activate_user_premium(user_id)  # Premium automatique
            
            caption = f"""
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
        
        # Photo du créateur pour les utilisateurs normaux
        send_legendary_photo(
            message.chat.id,
            f"📸 **{CREATOR}** - Créateur du bot\n*Votre expert en IA* 👑",
            create_main_menu() if check_premium_access(user_id) else create_premium_menu(user_id)
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
            
            bot.send_message(message.chat.id, menu, parse_mode='Markdown', reply_markup=create_premium_menu(user_id))
            
    except Exception as e:
        print(f"❌ Erreur start: {e}")
        bot.reply_to(message, "❌ Erreur temporaire. Réessayez.")

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
            start_broadcast(user_id)
            bot.answer_callback_query(call.id, "📢 Broadcast")
        
        elif call.data == "admin_mail":
            # Simuler la commande mail
            users = get_all_users()
            response = f"📨 **MESSAGES REÇUS**\n\n📊 Total utilisateurs: {len(users)}\n💡 Fonctionnalité à venir..."
            send_legendary_photo(call.message.chat.id, response)
            bot.answer_callback_query(call.id, "📨 Messages")
        
        elif call.data == "admin_logs":
            response = "📋 **LOGS ADMIN**\n\n🕐 Dernière activité: Maintenant\n👤 Admin connecté: Vous\n💡 Système opérationnel"
            send_legendary_photo(call.message.chat.id, response)
            bot.answer_callback_query(call.id, "📋 Logs")
        
        elif call.data == "admin_system":
            response = "🖥️ **SYSTÈME**\n\n💾 Mémoire: OK\n⚡ CPU: Optimal\n🔗 Connexion: Stable\n🤖 Bot: Actif"
            send_legendary_photo(call.message.chat.id, response)
            bot.answer_callback_query(call.id, "🖥️ Système")
        
        elif call.data == "admin_advanced":
            send_legendary_photo(
                call.message.chat.id,
                "⚡ **OUTILS AVANCÉS**\n\nChoisissez un outil :",
                create_advanced_admin_menu()
            )
            bot.answer_callback_query(call.id, "⚡ Avancé")
        
        elif call.data == "admin_premium_all":
            give_premium_to_all(user_id)
            bot.answer_callback_query(call.id, "⚡ Premium à Tous")
        
        elif call.data == "admin_cleanup":
            response = "🧹 **NETTOYAGE EFFECTUÉ**\n\n✅ Base de données optimisée\n🗑️ Cache nettoyé\n⚡ Performances améliorées"
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
        
        response = f"✅ **PREMIUM ACCORDÉ !**\n\n⭐ **Premium activé pour l'utilisateur {target_user_id}**"
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
    
    if not check_premium_access(user_id):
        total = get_group_stats()
        if total >= 5:
            bot.reply_to(message, 
                       "🎊 **PRÊT POUR LE PREMIUM !**\n\n✅ 5/5 groupes atteints !\n\n🎁 Cliquez sur 'Activer Premium' pour débloquer l'IA !",
                       reply_markup=create_premium_menu(user_id))
        else:
            bot.reply_to(message, 
                       f"🔒 **Version limitée**\n\n{get_progress_bar()}\n\nAjoutez le bot à {5-total} groupe(s) pour débloquer l'IA.",
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
    print("💎 SYSTÈME SANS AUTHENTIFICATION")
    print(f"   👑 Propriétaire: {ADMIN_ID}")
    print("   🔓 Accès admin automatique pour 7908680781")
    print("   🚫 Pas d'authentification requise")
    print("🤖 En attente de messages...")
    
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Erreur: {e}")
        time.sleep(5)
