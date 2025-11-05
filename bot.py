#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-

import telebot
import openai
import os
import time
from datetime import datetime
from dotenv import load_dotenv

print("🚀 Initialisation du Bot IA Termux...")

# ==================== CONFIGURATION SÉCURISÉE ====================
# Charge les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupère les tokens de manière sécurisée
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Vérification que les clés sont présentes
if not TELEGRAM_TOKEN:
    print("❌ ERREUR: TELEGRAM_TOKEN non trouvé dans .env")
    print("💡 Crée un fichier .env avec votre token Telegram")
    exit(1)

if not OPENAI_API_KEY:
    print("❌ ERREUR: OPENAI_API_KEY non trouvé dans .env")
    print("💡 Crée un fichier .env avec votre clé API OpenAI")
    exit(1)

# Initialisation du bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)
openai.api_key = OPENAI_API_KEY

print("✅ Bot configuré avec succès!")
print("🤖 En attente de messages...")

# ==================== COMMANDES PRINCIPALES ====================

@bot.message_handler(commands=['start', 'aide', 'help'])
def welcome_message(message):
    user = message.from_user
    welcome_text = f"""
🎉 **Bienvenue {user.first_name} !** 🎉

🤖 *Je suis ton Assistant IA Personnel*

✨ **Ce que je peux faire pour toi :**
• Répondre à toutes tes questions
• T'expliquer des concepts complexes  
• Générer des idées créatives
• T'aider dans tes projets
• Discuter de tout sujet

🚀 **Commandes disponibles :**
`/ask` - Poser une question
`/learn` - Apprendre un sujet
`/ideas` - Générer des idées
`/write` - Écrire un texte
`/explain` - Explication détaillée
`/translate` - Traduire du texte
`/status` - Statut du bot

💡 **Exemples d'utilisation :**
`/ask` Comment fonctionne l'IA ?
`/learn` la programmation Python
`/ideas` projet écologique innovant
`/write` une lettre de motivation
`/explain` la blockchain
`/translate` Hello, how are you?

📱 *Bot déployé sur Termux avec ❤️*
    """
    bot.reply_to(message, welcome_text, parse_mode='Markdown')
    print(f"👋 Welcome envoyé à {user.first_name}")

@bot.message_handler(commands=['ask'])
def ask_question(message):
    try:
        question = message.text.replace('/ask', '').strip()
        
        if not question:
            bot.reply_to(message, "❓ *Utilisation :* `/ask ta question`\n\n*Exemple :* `/ask Comment les avions volent-ils ?`", parse_mode='Markdown')
            return
        
        print(f"🧠 Question reçue : {question[:50]}...")
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Appel à l'API OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant utile et précis. Réponds de manière claire et détaillée."},
                {"role": "user", "content": question}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        
        # Réponse formatée
        response_text = f"""
❓ **Question :** {question}

💡 **Réponse :**

{answer}

⏰ *{datetime.now().strftime("%H:%M")} - Assistant IA Termux*
        """
        bot.reply_to(message, response_text, parse_mode='Markdown')
        print(f"✅ Réponse envoyée")
        
    except Exception as e:
        error_msg = f"❌ **Erreur :** {str(e)}\n\n🔄 Réessaie dans quelques instants !"
        bot.reply_to(message, error_msg, parse_mode='Markdown')
        print(f"🚨 Erreur : {str(e)}")

@bot.message_handler(commands=['learn'])
def learn_topic(message):
    try:
        topic = message.text.replace('/learn', '').strip()
        
        if not topic:
            bot.reply_to(message, "📚 *Utilisation :* `/learn sujet`\n\n*Exemple :* `/learn l'intelligence artificielle`", parse_mode='Markdown')
            return
        
        print(f"🎓 Apprentissage demandé : {topic}")
        bot.send_chat_action(message.chat.id, 'typing')
        
        prompt = f"""
        Enseigne-moi le sujet suivant : {topic}
        
        Structure ta réponse :
        1. Définition simple
        2. Concepts clés à comprendre
        3. Exemples concrets
        4. Applications pratiques
        5. Pour aller plus loin
        
        Sois pédagogique et passionnant !
        """
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000
        )
        
        lesson = response.choices[0].message.content
        
        response_text = f"""
🎓 **Leçon : {topic}**

{lesson}

📚 *Session d'apprentissage - {datetime.now().strftime("%H:%M")}*
        """
        bot.reply_to(message, response_text, parse_mode='Markdown')
        print(f"✅ Leçon envoyée sur : {topic}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Erreur :** {str(e)}", parse_mode='Markdown')

@bot.message_handler(commands=['ideas'])
def generate_ideas(message):
    try:
        theme = message.text.replace('/ideas', '').strip()
        
        if not theme:
            bot.reply_to(message, "💡 *Utilisation :* `/ideas thème`\n\n*Exemple :* `/ideas startup technologique`", parse_mode='Markdown')
            return
        
        print(f"💡 Génération d'idées : {theme}")
        bot.send_chat_action(message.chat.id, 'typing')
        
        prompt = f"Génère 5 idées créatives, innovantes et pratiques sur le thème : {theme}. Pour chaque idée, donne un titre accrocheur et une brève description."
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        
        ideas = response.choices[0].message.content
        
        response_text = f"""
💫 **Idées pour : {theme}**

{ideas}

✨ *Créez, innovez, réalisez !*
        """
        bot.reply_to(message, response_text, parse_mode='Markdown')
        print(f"✅ Idées générées pour : {theme}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Erreur :** {str(e)}", parse_mode='Markdown')

@bot.message_handler(commands=['write'])
def write_content(message):
    try:
        request = message.text.replace('/write', '').strip()
        
        if not request:
            bot.reply_to(message, "✍️ *Utilisation :* `/write demande`\n\n*Exemple :* `/write un poème sur la nature`", parse_mode='Markdown')
            return
        
        print(f"✍️ Rédaction demandée : {request}")
        bot.send_chat_action(message.chat.id, 'typing')
        
        prompt = f"Rédige : {request}. Sois créatif, clair et adapte le style au contexte demandé."
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800
        )
        
        content = response.choices[0].message.content
        
        response_text = f"""
✍️ **Contenu généré :**

{content}

🖋️ *Créativité assistée par IA*
        """
        bot.reply_to(message, response_text, parse_mode='Markdown')
        print(f"✅ Contenu généré")
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Erreur :** {str(e)}", parse_mode='Markdown')

@bot.message_handler(commands=['explain'])
def explain_concept(message):
    try:
        concept = message.text.replace('/explain', '').strip()
        
        if not concept:
            bot.reply_to(message, "🔍 *Utilisation :* `/explain concept`\n\n*Exemple :* `/explain la blockchain`", parse_mode='Markdown')
            return
        
        print(f"🔍 Explication demandée : {concept}")
        bot.send_chat_action(message.chat.id, 'typing')
        
        prompt = f"Explique le concept '{concept}' de manière simple et accessible, comme si tu parlais à un ami. Utilise des analogies de la vie quotidienne."
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        
        explanation = response.choices[0].message.content
        
        response_text = f"""
🔍 **Explication de : {concept}**

{explanation}

💡 *Compréhension facilitée par IA*
        """
        bot.reply_to(message, response_text, parse_mode='Markdown')
        print(f"✅ Concept expliqué : {concept}")
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Erreur :** {str(e)}", parse_mode='Markdown')

@bot.message_handler(commands=['translate'])
def translate_text(message):
    try:
        text = message.text.replace('/translate', '').strip()
        
        if not text:
            bot.reply_to(message, "🌐 *Utilisation :* `/translate texte`\n\n*Exemple :* `/translate Hello, how are you?`", parse_mode='Markdown')
            return
        
        print(f"🌐 Traduction demandée : {text[:30]}...")
        bot.send_chat_action(message.chat.id, 'typing')
        
        prompt = f"Traduis ce texte en français s'il est en anglais, ou en anglais s'il est en français. Texte: {text}"
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=400
        )
        
        translation = response.choices[0].message.content
        
        response_text = f"""
🌐 **Traduction :**

*Original :* {text}
*Traduction :* {translation}

🔄 *Traduction intelligente par IA*
        """
        bot.reply_to(message, response_text, parse_mode='Markdown')
        print(f"✅ Texte traduit")
        
    except Exception as e:
        bot.reply_to(message, f"❌ **Erreur :** {str(e)}", parse_mode='Markdown')

@bot.message_handler(commands=['status'])
def bot_status(message):
    status_text = f"""
📊 **Statut du Bot IA Termux**

✅ **En ligne et opérationnel**
🤖 **IA : Active et réactive**
🕐 **Heure : {datetime.now().strftime("%H:%M:%S")}**
📅 **Date : {datetime.now().strftime("%d/%m/%Y")}**
📱 **Plateforme : Termux Android**

✨ **Fonctionnalités :**
• Réponses intelligentes
• Apprentissage personnalisé
• Génération d'idées
• Rédaction assistée
• Explications détaillées
• Traduction automatique

💫 *Tout fonctionne parfaitement !*
    """
    bot.reply_to(message, status_text, parse_mode='Markdown')
    print("📊 Statut envoyé")

# ==================== MODE CONVERSATION ====================

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    # Ignore les commandes inconnues
    if message.text.startswith('/'):
        help_text = """
❓ **Commande non reconnue**

🔄 **Commandes disponibles :**
`/start` - Menu principal
`/ask` - Poser une question  
`/learn` - Apprendre un sujet
`/ideas` - Générer des idées
`/write` - Écrire un texte
`/explain` - Expliquer un concept
`/translate` - Traduire du texte
`/status` - Statut du bot

💡 *Tu peux aussi parler naturellement sans commande !*
        """
        bot.reply_to(message, help_text, parse_mode='Markdown')
    
    else:
        # Mode conversation libre
        try:
            print(f"💬 Message libre : {message.text[:30]}...")
            bot.send_chat_action(message.chat.id, 'typing')
            
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Tu es un assistant amical, intelligent et utile. Réponds de manière naturelle et engageante."},
                    {"role": "user", "content": message.text}
                ],
                max_tokens=500,
                temperature=0.8
            )
            
            answer = response.choices[0].message.content
            bot.reply_to(message, answer)
            print("✅ Réponse conversation envoyée")
            
        except Exception as e:
            bot.reply_to(message, "🤖 Je rencontre un petit problème. Réessaie avec une commande comme `/ask` !", parse_mode='Markdown')

# ==================== GESTION DES ERREURS ====================

def main():
    try:
        print("""
🎯 BOT IA TERMUX - PRÊT AU DÉMARRAGE
=====================================
✅ Configuration chargée
✅ Handlers enregistrés  
✅ En attente de messages...
        """)
        
        bot.infinity_polling()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
        
    except Exception as e:
        print(f"🚨 ERREUR CRITIQUE : {e}")
        print("🔄 Redémarrage dans 10 secondes...")
        time.sleep(10)
        main()

if __name__ == "__main__":
    main()
