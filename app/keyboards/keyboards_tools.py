from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from WorkWithDataBase import WorkWithDatabase

db = WorkWithDatabase()

async def create_list_products(products):
    keyboard = InlineKeyboardBuilder()

    for row in products:
        keyboard.add(InlineKeyboardButton(text = str(row[1]), callback_data="add_to_busket:" + str(row[0])))
    keyboard.add(InlineKeyboardButton(text = "На главную страницу", callback_data = "back_to_start"))
    return keyboard.adjust(1).as_markup()

async def create_list_busket(basket):
    keyboard = InlineKeyboardBuilder()

    for row in basket:
        item_id = str(row[0]) # ID записи в корзине
        product_name = str(db.show_product_for_id(row[2]))
        
        # Строка с названием и количеством
        keyboard.row(InlineKeyboardButton(text = f"{product_name} | {row[3]} шт.", callback_data="ignore"))
        
        # Кнопки управления элементом
        keyboard.row(
            InlineKeyboardButton(text = "❌ Удалить", callback_data=f"delete_item:{item_id}"),
            InlineKeyboardButton(text = "✏️ Изменить кол-во", callback_data=f"edit_item:{item_id}")
        )
    
    keyboard.row(InlineKeyboardButton(text = "На главную страницу", callback_data = "back_to_start"))
    return keyboard.as_markup()