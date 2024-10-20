import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import re

API_URL_TEMPLATE = "https://mahmoud-aheqh0b3csgagdf4.centralus-01.azurewebsites.net/info?api_key=تيم_C4&id={}"
LIKE_API_URL_TEMPLATE = "https://mahmoud-aheqh0b3csgagdf4.centralus-01.azurewebsites.net/request?api_key=تيم_C4&id={}&type=likes"
VISITORS_API_URL = "https://mahmoud-aheqh0b3csgagdf4.centralus-01.azurewebsites.net/visitors?api_key=تيم_C4&id=12345678"
FRIEND_SPAM_API_URL = "https://mahmoud-aheqh0b3csgagdf4.centralus-01.azurewebsites.net/request?api_key=تيم_C4&id=12345678&type=friend-spam"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "مرحبا بك في بوت C4 TEAM النسخة الحديثة\n"
        "الإرسال الإعجابات: أكتب /like مثل:\n"
        "/like 12345678\n"
        "لإرسال الزوار: أكتب /VU4 مثل:\n"
        "/VU4 12345678\n"
        "لإرسال سبام طلبات الصداقة: أكتب /inv مثل:\n"
        "/inv 12345678\n"
        "لمعرفة معلومات اللاعب: أكتب /C4 مثل:\n"
        "/C4 12345678"
    )

# دالة لمعالجة أمر /like
async def get_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1:
        await update.message.reply_text("يرجى استخدام الأمر بالشكل التالي: /like <ID>")
        return

    player_id = context.args[0]
    api_url = API_URL_TEMPLATE.format(player_id)

    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        player_info_raw = data.get('player_info', '')

        nickname_match = re.search(r'nickname: "([^"]+)"', player_info_raw)
        account_id_match = re.search(r'accountId: (\d+)', player_info_raw)
        level_match = re.search(r'level: (\d+)', player_info_raw)
        likes_match = re.search(r'liked: (\d+)', player_info_raw)

        nickname = nickname_match.group(1) if nickname_match else 'غير متوفر'
        account_id = account_id_match.group(1) if account_id_match else 'غير متوفر'
        level = level_match.group(1) if level_match else 'غير متوفر'
        likes_start = int(likes_match.group(1)) if likes_match else 0

        like_api_url = LIKE_API_URL_TEMPLATE.format(player_id)
        like_response = requests.get(like_api_url)

        if like_response.status_code == 200:
            like_data = like_response.json()
            if like_data.get("message") == "Successfully processed likes.":
                updated_response = requests.get(api_url)
                if updated_response.status_code == 200:
                    updated_data = updated_response.json()
                    updated_player_info_raw = updated_data.get('player_info', '')

                    updated_likes_match = re.search(r'liked: (\d+)', updated_player_info_raw)
                    likes_after = int(updated_likes_match.group(1)) if updated_likes_match else 0

                    likes_given = likes_after - likes_start
                    response_message = (
                        f"Player Nickname: {nickname}\n"
                        f"Player ID: {account_id}\n"
                        f"Player Level: {level}\n"
                        f"Likes at start of day: {likes_start}\n"
                        f"Likes after Command: {likes_after}\n"
                        f"Likes Given By Bot: {likes_given}\n"
                    )

                    if likes_given == 0:
                        response_message += ("You got likes today, try again tomorrow.")

                    await update.message.reply_text(response_message)
                else:
                    await update.message.reply_text("حدث خطأ أثناء إعادة الاتصال بالـ API.")
            else:
                await update.message.reply_text(f"طلب الإعجاب لم يُعالج بنجاح.")
        else:
            await update.message.reply_text(f"حدث خطأ أثناء معالجة طلب الإعجاب.")
    else:
        await update.message.reply_text("حدث خطأ أثناء الاتصال بالـ API.")

# دالة لمعالجة أمر /VU4 (الزوار)
async def get_visitors(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = requests.get(VISITORS_API_URL)
    if response.status_code == 200:
        data = response.json()
        visitors_count = data.get('visitors_count', 'غير متوفر')
        await update.message.reply_text(f"عدد الزوار: {visitors_count}")
    else:
        await update.message.reply_text("حدث خطأ أثناء الاتصال بالـ API.")

# دالة لمعالجة أمر /inv (سبام دعوات الصداقة)
async def send_friend_spam(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    response = requests.get(FRIEND_SPAM_API_URL)
    if response.status_code == 200:
        data = response.json()
        message = data.get('message', 'غير متوفر')
        await update.message.reply_text(f"النتيجة: {message}")
    else:
        await update.message.reply_text("حدث خطأ أثناء الاتصال بالـ API.")

def main() -> None:
    app = ApplicationBuilder().token("7058542763:AAE9BiKT-VHYNm0eDCO9UpGHdXBY6rzkwSI").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("like", get_info))
    app.add_handler(CommandHandler("VU4", get_visitors))
    app.add_handler(CommandHandler("inv", send_friend_spam))

    app.run_polling()

if __name__ == '__main__':
    main()
