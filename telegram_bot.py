"""
Telegram Bot for E-Commerce System
این ربات تلگرام برای مدیریت فروشگاه آنلاین طراحی شده است.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from database import db

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن ربات تلگرام (از متغیر محیطی)
TELEGRAM_BOT_TOKEN = os.environ.get("7622207519:AAH_A7Ih6SjEF_RJJLyil40Jo5ZLqjOCbwY", "")


def get_user_stats_text(user_id: int) -> str:
    """دریافت آمار کاربر به صورت متن"""
    stats = db.get_user_stats(user_id)
    orders = db.get_user_orders(user_id, limit=5)
    
    text = f"📊 *آمار شما:*\n\n"
    text += f"🛒 تعداد سفارش‌ها: {stats['total_orders']}\n"
    text += f"💰 مجموع خریدها: {stats['total_revenue']:,.0f} تومان\n\n"
    
    if orders:
        text += "📋 *آخرین سفارش‌ها:*\n"
        for order in orders[:5]:
            status_emoji = {
                'completed': '✅',
                'pending': '⏳',
                'processing': '🔄',
                'canceled': '❌'
            }.get(order['status'], '📦')
            text += f"{status_emoji} سفارش #{order['order_id']}: {order['total_amount']:,.0f} تومان ({order['status']})\n"
    else:
        text += "هنوز سفارشی ثبت نشده است.\n"
    
    return text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    keyboard = [
        [InlineKeyboardButton("📊 آمار من", callback_data="my_stats")],
        [InlineKeyboardButton("🛒 سفارش‌های من", callback_data="my_orders")],
        [InlineKeyboardButton("📦 محصولات", callback_data="products")],
        [InlineKeyboardButton("ℹ️ راهنما", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = """
🤖 *به ربات فروشگاه آنلاین خوش آمدید!*

با استفاده از این ربات می‌توانید:
• سفارش‌های خود را مشاهده کنید
• آمار خریدهای خود را ببینید
• لیست محصولات را مشاهده کنید
• سفارش‌های در انتظار را لغو کنید

برای شروع، یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /help"""
    help_text = """
📖 *راهنمای استفاده از ربات:*

/start - شروع کار با ربات
/help - نمایش این راهنما
/stats - نمایش آمار شما
/orders - نمایش سفارش‌های شما
/products - نمایش لیست محصولات

*نکات مهم:*
• برای استفاده از ربات، باید در وب‌سایت ثبت‌نام کرده باشید
• شناسه کاربری شما در تلگرام باید با شناسه در سیستم یکسان باشد
• می‌توانید سفارش‌های در انتظار (pending) را لغو کنید
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /stats"""
    user_id = update.effective_user.id
    
    # در اینجا باید user_id تلگرام را به user_id سیستم مپ کنید
    # برای سادگی، از user_id تلگرام استفاده می‌کنیم
    # در حالت واقعی باید یک جدول mapping داشته باشید
    
    try:
        text = get_user_stats_text(user_id)
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await update.message.reply_text("❌ خطا در دریافت آمار. لطفاً دوباره تلاش کنید.")


async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /orders"""
    user_id = update.effective_user.id
    
    try:
        orders = db.get_user_orders(user_id)
        
        if not orders:
            await update.message.reply_text("📭 شما هنوز سفارشی ثبت نکرده‌اید.")
            return
        
        text = f"🛒 *سفارش‌های شما:*\n\n"
        for order in orders[:10]:  # حداکثر 10 سفارش
            status_emoji = {
                'completed': '✅',
                'pending': '⏳',
                'processing': '🔄',
                'canceled': '❌'
            }.get(order['status'], '📦')
            
            text += f"{status_emoji} *سفارش #{order['order_id']}*\n"
            text += f"💰 مبلغ: {order['total_amount']:,.0f} تومان\n"
            text += f"📊 وضعیت: {order['status']}\n"
            text += f"📅 تاریخ: {order['created_at']}\n\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error getting orders: {e}")
        await update.message.reply_text("❌ خطا در دریافت سفارش‌ها. لطفاً دوباره تلاش کنید.")


async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /products"""
    try:
        products = db.get_all_products(limit=10)
        
        if not products:
            await update.message.reply_text("📦 محصولی در فروشگاه موجود نیست.")
            return
        
        text = "📦 *محصولات فروشگاه:*\n\n"
        for product in products:
            stock_status = "✅ موجود" if product['stock_quantity'] > 0 else "❌ ناموجود"
            text += f"*{product['name']}*\n"
            text += f"💰 قیمت: {product['price']:,.0f} تومان\n"
            text += f"📊 موجودی: {product['stock_quantity']} ({stock_status})\n"
            text += f"🏷️ دسته: {product['category']}\n\n"
        
        await update.message.reply_text(text, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error getting products: {e}")
        await update.message.reply_text("❌ خطا در دریافت محصولات. لطفاً دوباره تلاش کنید.")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک روی دکمه‌های اینلاین"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    if query.data == "my_stats":
        try:
            text = get_user_stats_text(user_id)
            await query.edit_message_text(text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ خطا در دریافت آمار.")
    
    elif query.data == "my_orders":
        try:
            orders = db.get_user_orders(user_id)
            if not orders:
                await query.edit_message_text("📭 شما هنوز سفارشی ثبت نکرده‌اید.")
                return
            
            text = f"🛒 *سفارش‌های شما:*\n\n"
            for order in orders[:5]:
                status_emoji = {
                    'completed': '✅',
                    'pending': '⏳',
                    'processing': '🔄',
                    'canceled': '❌'
                }.get(order['status'], '📦')
                text += f"{status_emoji} سفارش #{order['order_id']}: {order['total_amount']:,.0f} تومان\n"
            
            await query.edit_message_text(text, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text("❌ خطا در دریافت سفارش‌ها.")
    
    elif query.data == "products":
        await products_command(update, context)
    
    elif query.data == "help":
        await help_command(update, context)


def main():
    """تابع اصلی برای راه‌اندازی ربات"""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set!")
        return
    
    # ایجاد اپلیکیشن
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # اضافه کردن handlerها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("orders", orders_command))
    application.add_handler(CommandHandler("products", products_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # شروع ربات
    logger.info("Telegram bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
