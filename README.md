# 🛒 سیستم مدیریت فروشگاه آنلاین (E-Commerce)

پروژه کامل مدیریت فروشگاه آنلاین با Flask و SQLite همراه با ربات تلگرام

## ✨ امکانات

### وب اپلیکیشن
- 🔐 سیستم احراز هویت با نقش‌های Admin و Customer
- 👥 مدیریت کاربران (User) - فقط برای Admin
- 📦 مدیریت محصولات (Product) - فقط برای Admin
- 🛒 مدیریت سفارش‌ها (Order)
- 📋 مدیریت آیتم‌های سفارش (Order Item)
- 📊 داشبورد آماری جداگانه برای Admin و Customer
- 💰 محاسبه خودکار مبلغ کل سفارش
- 🔒 کنترل دسترسی بر اساس نقش کاربر

### ربات تلگرام 🤖
- 📊 مشاهده آمار خریدهای کاربر
- 🛒 مشاهده لیست سفارش‌ها
- 📦 مشاهده محصولات فروشگاه
- ⏳ لغو سفارش‌های در انتظار
- 📋 رابط کاربری ساده با دکمه‌های اینلاین

## 🚀 راه‌اندازی سریع (محلی)

### 1. نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### 2. راه‌اندازی دیتابیس
```bash
python init_db.py
```

### 3. اجرای برنامه
```bash
python app.py
```

### 4. ورود به سیستم
- آدرس: http://localhost:5000
- نام کاربری: `sara_2003`
- رمز عبور: `20032003`

## 🌐 استقرار روی Leapcell.io

[Leapcell](https://leapcell.io) یک پلتفرم PaaS است که امکان استقرار رایگان تا 20 پروژه را فراهم می‌کند.

### مراحل استقرار:

#### 1. آماده‌سازی پروژه
```bash
# اطمینان حاصل کنید که تمام فایل‌ها commit شده‌اند
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. ایجاد حساب کاربری در Leapcell
- به [leapcell.io](https://leapcell.io) بروید
- با GitHub یا Google ثبت‌نام کنید
- وارد داشبورد شوید

#### 3. استقرار پروژه
- روی "Deploy" یا "New Project" کلیک کنید
- گزینه "Import from GitHub" را انتخاب کنید
- repository خود را انتخاب کنید
- تنظیمات زیر را وارد کنید:
  - **Runtime**: Python 3.11
  - **Build Command**: `pip install -r requirements.txt && python init_db.py`
  - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`
  - **Port**: 5000

#### 4. تنظیم متغیرهای محیطی
در داشبورد Leapcell، به بخش Environment Variables بروید و متغیرهای زیر را اضافه کنید:

```
SECRET_KEY=your-secret-key-here
DATABASE_PATH=ecommerce.db
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
```

#### 5. استقرار ربات تلگرام (اختیاری)
برای اجرای ربات تلگرام به صورت جداگانه:
- یک Worker Service جدید ایجاد کنید
- **Start Command**: `python telegram_bot.py`
- متغیر محیطی `TELEGRAM_BOT_TOKEN` را تنظیم کنید

### ساخت ربات تلگرام

1. به [@BotFather](https://t.me/BotFather) در تلگرام پیام دهید
2. دستور `/newbot` را ارسال کنید
3. نام و username ربات را انتخاب کنید
4. توکن دریافت شده را در متغیر محیطی `TELEGRAM_BOT_TOKEN` قرار دهید

### دستورات ربات تلگرام

- `/start` - شروع کار با ربات و نمایش منوی اصلی
- `/help` - نمایش راهنما
- `/stats` - نمایش آمار خریدهای شما
- `/orders` - نمایش لیست سفارش‌های شما
- `/products` - نمایش لیست محصولات فروشگاه

## 📁 ساختار پروژه

```
e_commerce/
├── app.py              # اپلیکیشن اصلی Flask
├── auth.py             # مدیریت احراز هویت
├── database.py         # لایه دسترسی به دیتابیس
├── init_db.py          # راه‌اندازی دیتابیس
├── telegram_bot.py     # ربات تلگرام
├── requirements.txt    # وابستگی‌ها
├── leapcell.yaml       # تنظیمات استقرار Leapcell
├── Procfile            # تنظیمات Process برای Leapcell
├── ecommerce.db        # فایل دیتابیس SQLite
├── templates/          # قالب‌های HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── login.html
│   ├── products.html
│   ├── orders.html
│   ├── users.html
│   └── ...
└── static/             # فایل‌های استاتیک
    ├── css/
    └── js/
```

## 🗄️ ساختار دیتابیس

- **user**: کاربران سیستم (admin/customer)
- **product**: محصولات فروشگاه
- **order**: سفارش‌ها
- **order_item**: آیتم‌های هر سفارش

## 🔐 کنترل دسترسی

### نقش Admin
- دسترسی کامل به تمام بخش‌ها
- مدیریت کاربران و محصولات
- مشاهده تمام سفارش‌ها
- تغییر وضعیت سفارش‌ها
- مشاهده آمار کلی سیستم

### نقش Customer
- ویرایش پروفایل خود
- مشاهده و ثبت سفارش
- لغو سفارش‌های pending خود
- مشاهده فقط سفارش‌های خود
- مشاهده آمار خریدهای خود

## 📝 نکات مهم

- دیتابیس SQLite به صورت خودکار ایجاد می‌شود
- کاربر پیش‌فرض admin با یوزرنیم `sara_2003` ایجاد می‌شود
- تمام عملیات CRUD برای تمام موجودیت‌ها پیاده‌سازی شده است
- درآمد فقط از سفارش‌های `completed` محاسبه می‌شود
- با لغو سفارش، موجودی محصولات بازگردانده می‌شود
- مبلغ کل سفارش به صورت خودکار محاسبه می‌شود

## 🛠️ تکنولوژی‌های استفاده شده

- **Backend**: Flask 3.0.0
- **Authentication**: Flask-Login
- **Database**: SQLite
- **Deployment**: Leapcell.io
- **Telegram Bot**: python-telegram-bot 20.7
- **WSGI Server**: Gunicorn

## 📚 منابع

- [Leapcell Documentation](https://leapcell.io/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [python-telegram-bot Documentation](https://python-telegram-bot.org/)

## 📄 لایسنساین پروژه برای استفاده آموزشی ایجاد شده است.

## 👥 نویسندگان

پروژه درسی سیستم‌های پایگاه داده - ترم 7

---

**نکته**: برای استفاده از ربات تلگرام، باید شناسه کاربری تلگرام را با شناسه کاربری در سیستم مرتبط کنید. در نسخه فعلی، از شناسه تلگرام به عنوان شناسه کاربری استفاده می‌شود.