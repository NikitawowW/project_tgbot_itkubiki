from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from WorkWithDataBase import WorkWithDatabase

db = WorkWithDatabase()

async def create_list_products(products):
    keyboard = InlineKeyboardBuilder()

    for row in products:
        keyboard.add(InlineKeyboardButton(text = str(row[1]), callback_data="product_" + str(row[0])))
    keyboard.add(InlineKeyboardButton(text = "На главную страницу", callback_data = "back_to_start"))
    return keyboard.adjust(1).as_markup()

async def create_list_busket(basket):
    keyboard = InlineKeyboardBuilder()

    for row in basket:
        keyboard.add(InlineKeyboardButton(text = str(db.show_prouct_for_id(row[2])) + " | " + str(row[3]), callback_data="basket_" + str(row[0])))
    keyboard.add(InlineKeyboardButton(text = "На главную страницу", callback_data = "back_to_start"))
    return keyboard.adjust(1).as_markup()