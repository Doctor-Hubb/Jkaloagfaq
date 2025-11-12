import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import time
import asyncio

# تنظیمات
BOT_TOKEN = ""
ADMIN_USER_ID = 6674558636

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(BOT_TOKEN).build()
        self.active_groups = set()
        self.bot_start_time = time.time()
        self.setup_handlers()
        
    def setup_handlers(self):
        # کامندها
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("groups", self.list_groups_command))
        self.application.add_handler(CommandHandler("send", self.send_to_group_command))
        self.application.add_handler(CommandHandler("broadcast", self.broadcast_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("test", self.test_command))
        self.application.add_handler(CommandHandler("loadgroups", self.load_groups_command))
        
        # هندلرهای پیام
        self.application.add_handler(MessageHandler(
            filters.ChatType.PRIVATE & filters.User(ADMIN_USER_ID), 
            self.handle_private_message
        ))
        
        self.application.add_handler(MessageHandler(
            filters.ChatType.PRIVATE, 
            self.handle_other_users
        ))
        
        # هندلرهای گروه
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS, 
            self.handle_bot_added_to_group
        ))
        
        self.application.add_handler(MessageHandler(
            filters.StatusUpdate.LEFT_CHAT_MEMBER,
            self.handle_bot_removed_from_group
        ))
        
        self.application.add_handler(MessageHandler(
            filters.ChatType.GROUPS & ~filters.StatusUpdate.ALL, 
            self.forward_group_message
        ))
    
    async def load_existing_groups(self):
        """لود کردن گروه‌هایی که بات در حال حاضر در آنها است"""
        try:
            print("🔍 در حال بررسی گروه‌های موجود...")
            
            # دریافت اطلاعات بات
            bot_info = await self.application.bot.get_me()
            bot_username = bot_info.username
            print(f"🤖 نام بات: @{bot_username}")
            
            # روش ساده: وقتی پیامی از گروه می‌آید، گروه را اضافه کن
            # این متد بعداً با پیام‌های دریافتی پر می‌شود
            
        except Exception as e:
            print(f"❌ خطا در لود گروه‌ها: {e}")
    
    async def load_groups_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """کامند برای لود دستی گروه‌ها"""
        await update.message.reply_text("🔍 در حال بررسی گروه‌ها...")
        
        # اضافه کردن گروه از طریق پیام‌های دریافتی
        await update.message.reply_text(
            "💡 برای اضافه شدن گروه‌ها به لیست، یکی از این کارها را انجام دهید:\n\n"
            "1. در هر گروه یک پیام بفرستید\n"
            "2. بات را از گروه حذف و دوباره اضافه کنید\n"
            "3. از کامند /groups در خود گروه استفاده کنید"
        )
    
    async def test_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """کامند تست ساده"""
        user_id = update.effective_user.id
        chat_type = update.effective_chat.type
        
        if chat_type in ["group", "supergroup"]:
            # اگر کامند از گروه فرستاده شده، گروه را اضافه کن
            group_id = update.effective_chat.id
            group_title = update.effective_chat.title
            
            if group_id not in self.active_groups:
                self.active_groups.add(group_id)
                await update.message.reply_text(
                    f"✅ گروه به لیست اضافه شد!\n"
                    f"🏷️ نام گروه: {group_title}\n"
                    f"🆔 آی‌دی گروه: {group_id}"
                )
                print(f"✅ گروه جدید اضافه شد: {group_title} (ID: {group_id})")
            else:
                await update.message.reply_text(f"✅ گروه از قبل در لیست است: {group_title}")
        
        else:
            await update.message.reply_text(f"✅ تست موفق! User ID: {user_id}")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """کامند /start"""
        user_id = update.effective_user.id
        chat_type = update.effective_chat.type
        
        if chat_type in ["group", "supergroup"]:
            # اگر کامند از گروه فرستاده شده
            group_id = update.effective_chat.id
            group_title = update.effective_chat.title
            
            if group_id not in self.active_groups:
                self.active_groups.add(group_id)
                await update.message.reply_text(
                    f"✅ گروه به لیست اضافه شد!\n"
                    f"🏷️ نام گروه: {group_title}\n"
                    f"🆔 آی‌دی گروه: {group_id}\n\n"
                    f"📨 از این پس پیام‌های این گروه فوروارد می‌شوند."
                )
                print(f"✅ گروه جدید اضافه شد: {group_title} (ID: {group_id})")
        
        await update.message.reply_text(
            f"🤖 بات فعال شد!\n"
            f"🕒 زمان شروع: {time.ctime(self.bot_start_time)}\n"
            f"👥 گروه‌های فعال: {len(self.active_groups)}\n"
            f"💡 از /help برای راهنما استفاده کنید"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """کامند /help"""
        help_text = """
📖 **راهنمای بات:**

🔹 **/start** - اطلاعات بات (در گروه: اضافه شدن گروه)
🔹 **/help** - این راهنما  
🔹 **/test** - تست ساده (در گروه: اضافه شدن گروه)
🔹 **/status** - وضعیت بات
🔹 **/groups** - نمایش گروه‌های فعال
🔹 **/loadgroups** - راهنمای اضافه کردن گروه‌ها
🔹 **/send <group_id> <message>** - ارسال پیام به گروه خاص
🔹 **/broadcast <message>** - ارسال پیام به همه گروه‌ها

💡 **نکته:** فقط پیام‌های بعد از شروع بات فوروارد می‌شوند.
        """
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """کامند /status"""
        await update.message.reply_text(
            f"📊 وضعیت بات:\n"
            f"• زمان شروع: {time.ctime(self.bot_start_time)}\n"
            f"• گروه‌های فعال: {len(self.active_groups)}\n"
            f"• مدت زمان فعالیت: {int(time.time() - self.bot_start_time)} ثانیه"
        )
    
    async def list_groups_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """کامند /groups"""
        if not self.active_groups:
            await update.message.reply_text(
                "📭 هیچ گروه فعالی وجود ندارد.\n\n"
                "💡 برای اضافه کردن گروه‌ها:\n"
                "• در هر گروه /test یا /start بفرستید\n"
                "• یا در گروه پیام معمولی بفرستید"
            )
            return
        
        groups_text = "👥 **گروه‌های فعال:**\n\n"
        for i, group_id in enumerate(self.active_groups, 1):
            try:
                chat = await context.bot.get_chat(group_id)
                groups_text += f"{i}. **{chat.title}**\n🆔 `{group_id}`\n\n"
            except Exception as e:
                groups_text += f"{i}. گروه ناشناس\n🆔 `{group_id}`\n\n"
        
        await update.message.reply_text(groups_text)
    
    async def send_to_group_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """کامند /send"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "📤 **استفاده:**\n"
                "`/send <group_id> <message>`\n\n"
                "📝 **مثال:**\n"
                "`/send -1001234567890 سلام به این گروه`"
            )
            return
        
        try:
            group_id = int(context.args[0])
            message_text = " ".join(context.args[1:])
            
            await context.bot.send_message(
                chat_id=group_id,
                text=message_text
            )
            await update.message.reply_text(f"✅ پیام به گروه `{group_id}` ارسال شد.")
            
        except ValueError:
            await update.message.reply_text("❌ group_id باید عدد باشد.")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا: {e}")
    
    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """کامند /broadcast"""
        if not context.args:
            await update.message.reply_text(
                "📢 **استفاده:**\n"
                "`/broadcast <message>`\n\n"
                "📝 **مثال:**\n"
                "`/broadcast سلام به همه گروه‌ها`"
            )
            return
        
        if not self.active_groups:
            await update.message.reply_text("❌ هیچ گروه فعالی وجود ندارد.")
            return
        
        message_text = " ".join(context.args)
        success_count = 0
        
        for group_id in self.active_groups:
            try:
                await context.bot.send_message(
                    chat_id=group_id,
                    text=message_text
                )
                success_count += 1
                print(f"✅ ارسال به {group_id}")
            except Exception as e:
                print(f"❌ خطا در ارسال به {group_id}: {e}")
        
        await update.message.reply_text(
            f"✅ پیام به **{success_count}** از **{len(self.active_groups)}** گروه ارسال شد."
        )
    
    async def handle_bot_added_to_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """وقتی بات به گروه اضافه می‌شود"""
        try:
            chat = update.effective_chat
            new_members = update.message.new_chat_members
            
            bot_username = context.bot.username
            bot_added = any(
                hasattr(member, 'username') and member.username == bot_username 
                for member in new_members
            )
            
            if bot_added:
                self.active_groups.add(chat.id)
                print(f"✅ بات به گروه اضافه شد: {chat.title} (ID: {chat.id})")
                
                await context.bot.send_message(
                    chat_id=ADMIN_USER_ID,
                    text=f"✅ بات به گروه اضافه شد:\n🏷️ {chat.title}\n🆔 {chat.id}"
                )
                
        except Exception as e:
            print(f"خطا در پردازش اضافه شدن به گروه: {e}")
    
    async def handle_bot_removed_from_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """وقتی بات از گروه حذف می‌شود"""
        try:
            chat = update.effective_chat
            left_member = update.message.left_chat_member
            
            if hasattr(left_member, 'is_bot') and left_member.is_bot:
                self.active_groups.discard(chat.id)
                print(f"❌ بات از گروه حذف شد: {chat.id}")
                
        except Exception as e:
            print(f"خطا در پردازش حذف از گروه: {e}")
    
    async def forward_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """فوروارد پیام‌های گروه (فقط جدید)"""
        try:
            message = update.message
            chat = message.chat
            
            # اگر گروه در لیست فعال نیست، اضافه کن
            if chat.id not in self.active_groups:
                self.active_groups.add(chat.id)
                print(f"✅ گروه جدید شناسایی شد: {chat.title} (ID: {chat.id})")
            
            if message.date.timestamp() < self.bot_start_time:
                print(f"⏪ پیام قدیمی نادیده گرفته شد: {message.text[:50] if message.text else 'بدون متن'}...")
                return
            
            user_name = message.from_user.first_name if message.from_user else "ناشناس"
            user_id = message.from_user.id if message.from_user else "ناشناس"
            
            info_text = (
                f"📨 از گروه: **{chat.title}**\n"
                f"👤 کاربر: **{user_name}**\n"
                f"🆔 گروه: `{chat.id}`\n"
                f"➖➖➖➖➖➖➖"
            )
            
            await context.bot.send_message(
                chat_id=ADMIN_USER_ID,
                text=info_text
            )
            
            await message.forward(chat_id=ADMIN_USER_ID)
            print(f"✅ پیام جدید فوروارد شد از {chat.title}")
            
        except Exception as e:
            print(f"خطا در فوروارد: {e}")
    
    async def handle_private_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش پیام‌های خصوصی ادمین"""
        await update.message.reply_text(
            "💡 برای ارسال پیام از دستورات استفاده کنید:\n\n"
            "🔹 /send <group_id> <message>\n"
            "🔹 /broadcast <message>\n\n"
            "🔹 /help برای راهنمایی بیشتر"
        )
    
    async def handle_other_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """پردازش پیام کاربران دیگر"""
        await update.message.reply_text("👋 سلام! با ادمین تماس بگیرید.")
    
    def run(self):
        """اجرای بات"""
        print("🤖 بات در حال اجرا...")
        print(f"🔧 ADMIN_ID: {ADMIN_USER_ID}")
        print("📨 فقط پیام‌های جدید فوروارد می‌شوند")
        print("⏹️  Ctrl+C برای توقف")
        
        self.application.run_polling()

if __name__ == "__main__":
    bot = TelegramBot()
    bot.run()
