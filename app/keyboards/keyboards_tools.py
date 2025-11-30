from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from WorkWithDataBase import WorkWithDatabase

db = WorkWithDatabase()

async def create_list(components, item_type):
    keyboard = InlineKeyboardBuilder()

    for row in components:
        if item_type == 'products':
            button_text = f"{row[1]} | {row[2]} руб./шт." 
            keyboard.add(InlineKeyboardButton(text = button_text, callback_data="add_to_busket:" + str(row[0])))
        elif item_type == 'basket':
            product_info = db.show_product_for_id(row[2])
            product_name = product_info[0] 
            keyboard.add(InlineKeyboardButton(text = product_name + " | " + str(row[3]) + " шт.", callback_data="basket_" + str(row[0])))    

    keyboard.add(InlineKeyboardButton(text = "На главную страницу", callback_data = "back_to_start"))
    return keyboard.adjust(1).as_markup()