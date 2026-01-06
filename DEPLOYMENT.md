# 🚀 راهنمای استقرار روی Leapcell.io

این راهنما به شما کمک می‌کند تا پروژه فروشگاه آنلاین را روی [Leapcell.io](https://leapcell.io) استقرار دهید.

## 📋 پیش‌نیازها

1. حساب کاربری در [Leapcell.io](https://leapcell.io)
2. حساب GitHub (برای import کردن پروژه)
3. ربات تلگرام (اختیاری - برای استفاده از ربات)

## 🔧 مراحل استقرار

### مرحله 1: آماده‌سازی پروژه

```bash
# اطمینان حاصل کنید که تمام تغییرات commit شده‌اند
git add .
git commit -m "Ready for Leapcell deployment"
git push origin main
```

### مرحله 2: ورود به Leapcell

1. به [leapcell.io](https://leapcell.io) بروید
2. با GitHub یا Google وارد شوید
3. وارد داشبورد شوید

### مرحله 3: ایجاد پروژه جدید

1. روی دکمه **"Deploy"** یا **"+ New Project"** کلیک کنید
2. گزینه **"Import from GitHub"** را انتخاب کنید
3. Repository خود را انتخاب کنید
4. نام پروژه را وارد کنید (مثلاً: `e-commerce`)

### مرحله 4: تنظیمات Runtime

در صفحه تنظیمات:

- **Runtime**: `Python 3.11`
- **Build Command**: 
  ```bash
  pip install --upgrade pip && pip install -r requirements.txt && python init_db.py
  ```
- **Start Command**: 
  ```bash
  gunicorn -w 4 -b 0.0.0.0:$PORT app:app
  ```
- **Port**: `5000` (یا از متغیر محیطی `$PORT` استفاده کنید)

### مرحله 5: تنظیم متغیرهای محیطی

در بخش **Environment Variables**، متغیرهای زیر را اضافه کنید:

| متغیر | مقدار | توضیحات |
|------|-------|---------|
| `SECRET_KEY` | یک رشته تصادفی | برای امنیت session ها |
| `DATABASE_PATH` | `ecommerce.db` | مسیر فایل دیتابیس |
| `TELEGRAM_BOT_TOKEN` | توکن ربات تلگرام | (اختیاری) برای ربات تلگرام |

**تولید SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

### مرحله 6: استقرار

1. روی دکمه **"Deploy"** کلیک کنید
2. منتظر بمانید تا build و deploy انجام شود
3. پس از اتمام، URL پروژه شما نمایش داده می‌شود

### مرحله 7: تست

1. به URL داده شده بروید
2. با اطلاعات زیر وارد شوید:
   - نام کاربری: `sara_2003`
   - رمز عبور: `20032003`

## 🤖 استقرار ربات تلگرام (اختیاری)

### مرحله 1: ساخت ربات تلگرام

1. به [@BotFather](https://t.me/BotFather) در تلگرام پیام دهید
2. دستور `/newbot` را ارسال کنید
3. نام ربات را وارد کنید (مثلاً: `My E-Commerce Bot`)
4. Username ربات را وارد کنید (باید به `bot` ختم شود، مثلاً: `my_ecommerce_bot`)
5. توکن دریافت شده را کپی کنید

### مرحله 2: ایجاد Worker Service

1. در داشبورد Leapcell، یک **Worker Service** جدید ایجاد کنید
2. نام آن را `telegram-bot` بگذارید
3. **Start Command**: `python telegram_bot.py`
4. متغیر محیطی `TELEGRAM_BOT_TOKEN` را تنظیم کنید
5. Deploy کنید

### مرحله 3: تست ربات

1. ربات خود را در تلگرام پیدا کنید
2. دستور `/start` را ارسال کنید
3. باید منوی ربات نمایش داده شود

## 📊 مانیتورینگ

در داشبورد Leapcell می‌توانید:
- لاگ‌های اپلیکیشن را مشاهده کنید
- آمار ترافیک را ببینید
- استفاده از منابع را بررسی کنید

## 🔄 بروزرسانی

برای بروزرسانی پروژه:

```bash
git add .
git commit -m "Update description"
git push origin main
```

Leapcell به صورت خودکار تغییرات را detect کرده و دوباره deploy می‌کند.

## 🛠️ عیب‌یابی

### مشکل: اپلیکیشن اجرا نمی‌شود

- بررسی کنید که `requirements.txt` کامل باشد
- لاگ‌ها را در داشبورد Leapcell بررسی کنید
- مطمئن شوید که `PORT` environment variable تنظیم شده است

### مشکل: دیتابیس کار نمی‌کند

- بررسی کنید که `init_db.py` در build command اجرا می‌شود
- مطمئن شوید که `DATABASE_PATH` صحیح است

### مشکل: ربات تلگرام کار نمی‌کند

- بررسی کنید که `TELEGRAM_BOT_TOKEN` صحیح است
- لاگ‌های Worker Service را بررسی کنید
- مطمئن شوید که Worker Service در حال اجرا است

## 📚 منابع بیشتر

- [مستندات Leapcell](https://leapcell.io/docs)
- [راهنمای Python Deployment](https://leapcell.io/docs/python)
- [راهنمای Environment Variables](https://leapcell.io/docs/env-vars)

## 💡 نکات

- Leapcell تا 20 پروژه رایگان ارائه می‌دهد
- برای پروژه‌های بزرگ‌تر، می‌توانید به پلن Plus یا Pro ارتقا دهید
- دیتابیس SQLite برای پروژه‌های کوچک مناسب است، برای پروژه‌های بزرگ‌تر از PostgreSQL استفاده کنید
