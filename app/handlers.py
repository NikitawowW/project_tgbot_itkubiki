from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import BOT_TOKEN

import openpyxl
import os
import datetime 

from keyboards.keyboards import start_keyboard, personal_account_keyboard, admin_keyboard
from keyboards.keyboards_tools import create_list_products, create_list_busket

from WorkWithDataBase import WorkWithDatabase

db = WorkWithDatabase()

bot = Bot(token = BOT_TOKEN)
router = Router()

class Flag(StatesGroup):
    wait_for_file = State()
    wait_for_count = State()
    wait_for_edit_count = State()

def get_full_user_name(user):
    full_name = user.first_name if user.first_name else "Неизвестный"
    if user.last_name:
        full_name += f" {user.last_name}"
    return full_name

@router.message(Command('start'))
async def start_command_handler(message: Message):
    text = 'Приветственное сообщение'
    await message.answer(text, reply_markup = start_keyboard)

@router.message(Command('admin_panel'))
async def admin_panel_command_handler(message: Message):
    text = 'Добро пожаловать в admin panel'
    await message.answer(text, reply_markup = admin_keyboard)

@router.callback_query(F.data == 'cabinet_basket')
async def cabinet_basket_handler(c: CallbackQuery):
    await c.message.edit_text("Личный Кабинет", reply_markup = personal_account_keyboard)

@router.callback_query(F.data == 'production')
async def show_production_handler(c: CallbackQuery):
    products_data = db.show_products()
    products_keyboard = await create_list_products(products_data)
    await c.message.edit_text(
        "Добавление товаров в корзину", 
        reply_markup = products_keyboard
    )

@router.callback_query(F.data.startswith('add_to_busket'))
async def add_to_busket(c: CallbackQuery, state: FSMContext):
    try:
        id_product = int(c.data.split(':')[1])
        product_name = db.show_product_for_id(id_product)
        
        await state.update_data(id_product = id_product)
        await c.answer(f"Вы выбрали: {product_name}", show_alert=False)
        await c.message.edit_text(f'Вы выбрали {product_name}. Введите желаемое количество товара:')
        await state.set_state(Flag.wait_for_count)
    except Exception as e:
        await c.answer("Произошла ошибка при выборе товара. Попробуйте снова.", show_alert=True)

@router.message(Flag.wait_for_count)
async def get_count_handler(message: Message, state: FSMContext):
    try:
        count = int(message.text)
        if count <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Неверный формат. Введите целое положительное число.")
        return

    data = await state.get_data()
    id_product = data.get('id_product')
    chat_id = str(message.chat.id)

    db.insert_into_user_basket(chat_id, id_product, count)
    
    await state.clear()
    await message.answer("Товар добавлен в корзину!", reply_markup = start_keyboard)

@router.callback_query(F.data == 'show_basket')
async def show_basket_handler(c: CallbackQuery):
    chat_id = str(c.message.chat.id)
    basket = db.select_busket(chat_id)

    if not basket:
        await c.message.edit_text("Ваша корзина пуста.", reply_markup = personal_account_keyboard)
        return

    basket_keyboard = await create_list_busket(basket)
    await c.message.edit_text("Ваша корзина:", reply_markup = basket_keyboard)

@router.callback_query(F.data == 'order_busket')
async def order_busket(c: CallbackQuery):
    chat_id = str(c.message.chat.id)
    
    basket_items = db.select_busket(chat_id)
    
    if not basket_items:
        await c.answer("Ваша корзина пуста.", show_alert=True)
        return

    # --- ДИАГНОСТИЧЕСКИЙ ВЫВОД ---
    print(f"Корзина пользователя {chat_id} содержит {len(basket_items)} элементов:")
    print(basket_items)
    # -----------------------------
    
    now = datetime.datetime.now()
    order_date = now.strftime("%Y-%m-%d %H:%M:%S")
    customer_name = get_full_user_name(c.from_user)

    wb = openpyxl.Workbook()
    sheet = wb.active

    headers = ["Дата", "Имя и Фамилия заказчика"]
    row_data = [order_date, customer_name]
    
    try:
        for i, item in enumerate(basket_items, start=1):
            product_id = item[2]
            count = item[3]
            
            product_name = db.show_product_for_id(product_id) 
            
            headers.extend([f"Имя товара {i}", f"Количество товара {i} (шт.)"])
            
            row_data.extend([product_name, count])
            
            print(f"Добавлен товар {i}: {product_name} ({count} шт.)") # ДИАГНОСТИКА

    except Exception as e:
        await c.answer("Ошибка при обработке одного из товаров корзины.", show_alert=True)
        print(f"КРИТИЧЕСКАЯ ОШИБКА В ЦИКЛЕ ЗАКАЗА: {e}")
        return

    for col_num, header in enumerate(headers, start=1):
        sheet.cell(row=1, column=col_num, value=header)

    for col_num, value in enumerate(row_data, start=1):
        sheet.cell(row=2, column=col_num, value=value)
        
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            try:
                cell_value_str = str(cell.value) if cell.value is not None else ""
                if len(cell_value_str) > max_length:
                    max_length = len(cell_value_str)
            except:
                pass
        adjusted_width = (max_length + 2)
        sheet.column_dimensions[column_letter].width = adjusted_width


    excel_file_name = f"Заказ_{chat_id}_{now.strftime('%Y%m%d%H%M%S')}.xlsx"
    wb.save(excel_file_name)
    
    input_file = FSInputFile(excel_file_name)
    await c.message.answer_document(document = input_file, caption = f"Ваш заказ от {order_date} от заказчика {get_full_user_name(c.from_user)}")
    
    db.delete_busket(chat_id)
    os.remove(excel_file_name) 

@router.callback_query(F.data == 'clear_all_basket')
async def clear_all_basket_handler(c: CallbackQuery):
    chat_id = str(c.message.chat.id)
    db.delete_busket(chat_id)
    await c.answer("Корзина полностью очищена!", show_alert=True)
    await c.message.edit_text("Личный Кабинет", reply_markup = personal_account_keyboard)

@router.callback_query(F.data.startswith('delete_item'))
async def delete_item_handler(c: CallbackQuery):
    item_id = int(c.data.split(':')[1])
    db.delete_item_busket(item_id)
    
    await c.answer("Элемент удален из корзины.", show_alert=False)
    await show_basket_handler(c)

@router.callback_query(F.data.startswith('edit_item'))
async def edit_item_handler(c: CallbackQuery, state: FSMContext):
    item_id = int(c.data.split(':')[1])
    
    await state.update_data(item_id_to_edit=item_id)
    
    await c.answer("Введите новое количество.", show_alert=False)
    await c.message.edit_text("Введите новое количество для выбранного товара:")
    await state.set_state(Flag.wait_for_edit_count)

@router.message(Flag.wait_for_edit_count)
async def get_edit_count_handler(message: Message, state: FSMContext):
    try:
        new_count = int(message.text)
        if new_count <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Неверный формат. Введите целое положительное число.")
        return

    data = await state.get_data()
    item_id_to_edit = data.get('item_id_to_edit')
    
    db.update_item_count(item_id_to_edit, new_count)
    
    await state.clear()
    await message.answer("Количество товара обновлено!", reply_markup = personal_account_keyboard)

@router.callback_query(F.data == 'back_to_start')
async def back_to_start_handler(c: CallbackQuery):
    await c.message.edit_text('Приветственное сообщение', reply_markup = start_keyboard)

@router.callback_query(F.data == 'file_download')
async def file_download_handler(c: CallbackQuery, state: FSMContext):
    await c.message.edit_text('Загрузите файл Excel', reply_markup = start_keyboard)
    await state.set_state(Flag.wait_for_file)

@router.message(Flag.wait_for_file)
async def process_file(message: Message, state: FSMContext):
    if not message.document:
        await message.answer("Пожалуйста, загрузите файл.")
        return
        
    file_name = message.document.file_name
    
    if not file_name.endswith('.xlsx'):
        await message.answer("Поддерживаются только файлы .xlsx.")
        return

    file_id = message.document.file_id
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    
    downloaded_file = await bot.download_file(file_path)
    
    with open(file_name, 'wb') as f:
        f.write(downloaded_file.read())
        
    try:
        workbook = openpyxl.load_workbook(file_name)
        sheet = workbook.active
        
        db.delete_from_products()
        
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] and row[1]:
                db.save_products(str(row[0]), int(row[1]))
                
    except Exception as e:
        await message.answer(f"Ошибка при обработке файла: {e}")
    
    if os.path.exists(file_name):
        os.remove(file_name)
            
    await state.clear()
    await message.answer("Загрузка прошла успешно", reply_markup = admin_keyboard)