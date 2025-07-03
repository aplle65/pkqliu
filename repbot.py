import asyncio
import random
from datetime import date
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os
from keepalive import keep_alive
keep_alive()

BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_BOT_URL = os.getenv("TARGET_BOT_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
user_modes = {}

REGIONS = ["usa", "uk", "aus", "canada"]
REGION_LIMITS = {
    "usa": (0, 3),
    "uk": (0, 2),
    "aus": (0, 2),
    "canada": (0, 3)
}

# In-memory phone data: region -> list of dicts
phone_data = {
    "usa": [
        {"phone": "18002211161", "company": "PayPal", "is_working": True, "updated_at": date.today()},
        {"phone": "18558124430", "company": "Venmo", "is_working": True, "updated_at": date.today()},
        {"phone": "18009691940", "company": "Cash App", "is_working": True, "updated_at": date.today()},
        {"phone": "18665797172", "company": "Netflix", "is_working": True, "updated_at": date.today()},
        {"phone": "18004321000", "company": "Bank of America", "is_working": True, "updated_at": date.today()},
        {"phone": "18889087930", "company": "Coinbase(Int)", "is_working": True, "updated_at": date.today()},
        {"phone": "18882804331", "company": "Amazon", "is_working": True, "updated_at": date.today()},
        {"phone": "18009359935", "company": "Chase", "is_working": True, "updated_at": date.today()},
        {"phone": "18887622265", "company": "PNC Bank", "is_working": True, "updated_at": date.today()},
        {"phone": "18773834802", "company": "Capital One", "is_working": True, "updated_at": date.today()},
        {"phone": "18008693557", "company": "Wells Fargo", "is_working": True, "updated_at": date.today()},
        {"phone": "18003749700", "company": "Citi", "is_working": True, "updated_at": date.today()},
        {"phone": "18002752273", "company": "Apple Pay", "is_working": True, "updated_at": date.today()},
        {"phone": "97317207777", "company": "BDO Unibank(Int)", "is_working": True, "updated_at": date.today()},
    ],
    "uk": [
        {"phone": "448003587911", "company": "PayPal", "is_working": True, "updated_at": date.today()},
        {"phone": "448000966379", "company": "Netflix", "is_working": True, "updated_at": date.today()},
        {"phone": "448004961081", "company": "Amazon", "is_working": True, "updated_at": date.today()},
        {"phone": "448003763333", "company": "Chase UK", "is_working": True, "updated_at": date.today()},
        {"phone": "443444812812", "company": "Capital One UK", "is_working": True, "updated_at": date.today()},
        {"phone": "44800005500", "company": "Citi UK", "is_working": True, "updated_at": date.today()},
        {"phone": "448000480408", "company": "Apple Pay", "is_working": True, "updated_at": date.today()},
        {"phone": "448081684635", "company": "Coinbase", "is_working": True, "updated_at": date.today()},
        {"phone": "97317207777", "company": "BDO Unibank(Int)", "is_working": True, "updated_at": date.today()},
    ],
    "aus": [
        {"phone": "611800073263", "company": "PayPal", "is_working": True, "updated_at": date.today()},
        {"phone": "611800071578", "company": "Netflix", "is_working": True, "updated_at": date.today()},
        {"phone": "611800571894", "company": "Amazon", "is_working": True, "updated_at": date.today()},
        {"phone": "61132484", "company": "Citi Australia", "is_working": True, "updated_at": date.today()},
        {"phone": "611300321456", "company": "Apple Pay", "is_working": True, "updated_at": date.today()},
        {"phone": "611300115533", "company": "Zip", "is_working": True, "updated_at": date.today()},
        {"phone": "97317207777", "company": "BDO Unibank(Int)", "is_working": True, "updated_at": date.today()},
        {"phone": "18889087930", "company": "Coinbase(Int)", "is_working": True, "updated_at": date.today()},
    ],
    "canada": [
        {"phone": "18888839770", "company": "PayPal", "is_working": True, "updated_at": date.today()},
        {"phone": "18445052993", "company": "Netflix", "is_working": True, "updated_at": date.today()},
        {"phone": "18775863230", "company": "Amazon Canada", "is_working": True, "updated_at": date.today()},
        {"phone": "18004813239", "company": "Capital One Canada", "is_working": True, "updated_at": date.today()},
        {"phone": "18003871616", "company": "Citi Canada", "is_working": True, "updated_at": date.today()},
        {"phone": "18002633394", "company": "Apple Pay", "is_working": True, "updated_at": date.today()},
        {"phone": "18002655158", "company": "Chase Canada", "is_working": True, "updated_at": date.today()},
        {"phone": "18889087930", "company": "Coinbase(Int)", "is_working": True, "updated_at": date.today()},
        {"phone": "97317207777", "company": "BDO Unibank(Int)", "is_working": True, "updated_at": date.today()},
    ]
}

def find_number(region, phone):
    for entry in phone_data[region]:
        if entry["phone"] == phone:
            return entry
    return None

def get_all_statuses(region):
    return phone_data[region]

def is_known_number(region, phone):
    return find_number(region, phone) is not None

def random_update_statuses():
    for region in REGIONS:
        all_entries = phone_data[region]
        if not all_entries:
            continue
        # Set all to working
        for entry in all_entries:
            entry["is_working"] = True
            entry["updated_at"] = date.today()
        # Pick a subset to mark as not working
        min_c, max_c = REGION_LIMITS[region]
        count = random.randint(min_c, min(max_c, len(all_entries)))
        affected = random.sample(all_entries, count)
        for entry in affected:
            entry["is_working"] = False
            entry["updated_at"] = date.today()
        print(f"{region.upper()}: {count} numbers set to not_working")

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 System Status", callback_data="status")],
        [InlineKeyboardButton(text="📞 Check Caller-ID", callback_data="check_id")],
        [InlineKeyboardButton(text="📊 List Status", callback_data="list")],
        [InlineKeyboardButton(text="🚩 Report Bad ID", callback_data="report")]
    ])

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("🚀 <b>Apollo OTP</b>👋 Phone Bot Checker – choose action:", parse_mode="HTML", reply_markup=main_menu())

@dp.callback_query(F.data == "status")
async def handle_global_status(cb: types.CallbackQuery):
    await cb.message.delete()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="OTP BOT 🤖", url=TARGET_BOT_URL)]])
    await cb.message.answer("🌐 System is <b>ONLINE</b>", parse_mode="HTML", reply_markup=kb)
    await cb.answer()

@dp.callback_query(F.data == "check_id")
async def prompt_for_check_id(cb: types.CallbackQuery):
    user_modes[cb.from_user.id] = "check"
    await cb.message.delete()
    await cb.message.answer("📲 Send 11-digit number to check.")
    dp.message.register(handle_number_input)
    await cb.answer()

@dp.callback_query(F.data == "list")
async def handle_list_prompt(cb: types.CallbackQuery):
    await cb.message.delete()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇸 USA", callback_data="list_usa")],
        [InlineKeyboardButton(text="🇬🇧 UK", callback_data="list_uk")],
        [InlineKeyboardButton(text="🇦🇺 Australia", callback_data="list_aus")],
        [InlineKeyboardButton(text="🇨🇦 Canada", callback_data="list_canada")]
    ])
    await cb.message.answer("🌍 Choose region to list statuses:", reply_markup=kb)
    await cb.answer()

@dp.callback_query(F.data.startswith("list_"))
async def handle_list(cb: types.CallbackQuery):
    region = cb.data.split("_")[1]
    await cb.message.delete()
    rows = get_all_statuses(region)
    if not rows:
        await cb.message.answer("No data found.")
        await cb.answer()
        return
    max_company = max(len(r["company"]) for r in rows)
    max_phone = max(len(r["phone"]) for r in rows)
    lines = []
    for r in rows:
        company = r["company"].ljust(max_company + 2)
        phone = r["phone"].rjust(max_phone)
        status = "working" if r["is_working"] else "not_working"
        lines.append(f"{company}{phone} → {status} @ {r['updated_at'].strftime('%Y-%m-%d')}")
    text = "\n".join(lines)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="OTP BOT 🤖", url=TARGET_BOT_URL)]])
    await cb.message.answer(f"<pre>{text}</pre>", parse_mode="HTML", reply_markup=kb)
    await cb.answer()

@dp.callback_query(F.data == "report")
async def handle_report_prompt(cb: types.CallbackQuery):
    user_modes[cb.from_user.id] = "report"
    await cb.message.delete()
    await cb.message.answer("📲 Send 11-digit number to report.")
    dp.message.register(handle_number_input)
    await cb.answer()

async def handle_number_input(msg: types.Message):
    user_id = msg.from_user.id
    number = msg.text.strip()
    mode = user_modes.get(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="OTP BOT 🤖", url=TARGET_BOT_URL)]])
    if mode == "check":
        for region in REGIONS:
            row = find_number(region, number)
            if row:
                status_str = "working" if row["is_working"] else "not_working"
                text = f"🔍 <b>{row['company']}</b> ({region.upper()})\n📞 {row['phone']} → <b>{status_str}</b> @ {row['updated_at'].strftime('%Y-%m-%d')}"
                await msg.answer(text, parse_mode="HTML", reply_markup=kb)
                break
        else:
            await msg.answer("❌ Not our number.", reply_markup=kb)
    elif mode == "report":
        found = False
        for region in REGIONS:
            row = find_number(region, number)
            if row:
                row["is_working"] = False
                row["updated_at"] = date.today()
                await msg.answer(f"🚩 Reported {number} as not working in {region.upper()}.", reply_markup=kb)
                found = True
        if not found:
            await msg.answer("❌ Not our number.", reply_markup=kb)
    user_modes.pop(user_id, None)

def is_admin(user_id):
    return user_id == ADMIN_ID

@dp.message(Command("insert"))
async def handle_insert(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ You are not authorized.")
        return
    try:
        _, region, phone, company = message.text.split(maxsplit=3)
        if region not in REGIONS:
            await message.answer("❌ Invalid region.")
            return
        if find_number(region, phone):
            await message.answer("❌ Number already exists.")
            return
        phone_data[region].append({
            "phone": phone,
            "company": company,
            "is_working": True,
            "updated_at": date.today()
        })
        await message.answer(f"✅ Inserted {phone} for {company} in {region.upper()}.")
    except Exception as e:
        await message.answer("❌ Usage: /insert <region> <phone> <company>")

@dp.message(Command("delete"))
async def handle_delete(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("❌ You are not authorized.")
        return
    try:
        _, region, phone = message.text.split(maxsplit=2)
        if region not in REGIONS:
            await message.answer("❌ Invalid region.")
            return
        before = len(phone_data[region])
        phone_data[region] = [entry for entry in phone_data[region] if entry["phone"] != phone]
        after = len(phone_data[region])
        if before == after:
            await message.answer("❌ Number not found.")
        else:
            await message.answer(f"✅ Deleted {phone} from {region.upper()}.")
    except Exception as e:
        await message.answer("❌ Usage: /delete <region> <phone>")

def setup_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(random_update_statuses, "interval", hours=24)
    scheduler.start()

def main():
    setup_scheduler()
    random_update_statuses()  # Initial randomization
    dp.run_polling(bot)

if __name__ == "__main__":
    main()
