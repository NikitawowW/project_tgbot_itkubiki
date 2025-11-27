from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from config import BOT_TOKEN

import openpyxl
import os

from keyboards.keyboards import start_keyboard, personal_account_keyboard, admin_keyboard
from keyboards.keyboards_tools import create_list_products, create_list_busket

from WorkWithDataBase import WorkWithDatabase

db = WorkWithDatabase()

bot = Bot(token = BOT_TOKEN)
router = Router()

class Flag(StatesGroup):
    wait_for_file = State()
    wait_for_count = State()

@router.message(Command('start'))
async def start(message: Message):
    text = 'Приветственное сообщение'
    await message.answer(text, reply_markup = start_keyboard)

@router.message(Command('admin_panel'))
async def start(message: Message):
    text = 'Добро пожаловать в admin panel'
    await message.answer(text, reply_markup = admin_keyboard)

@router.callback_query(F.data == 'show_basket')
async def start(c: CallbackQuery):
    await c.message.edit_text("Ваша корзина", reply_markup = await create_list_busket(db.select_busket(str(c.message.chat.id))))

@router.callback_query(F.data == 'production')
async def start(c: CallbackQuery):
    await c.message.edit_text("Добавление товаров в корзину", reply_markup = await create_list_products(db.show_products()))

@router.callback_query(F.data.startswith('product_'))
async def start(c: CallbackQuery, state: FSMContext):
    await state.update_data(name = c.data.split('_')[1])
    await state.set_state(Flag.wait_for_count)
    await c.message.answer("Введите сколько этого товара вы хотите добавить")

@router.callback_query(F.data == 'download_products')
async def start(c: CallbackQuery, state: FSMContext):
    await state.set_state(Flag.wait_for_file)
    await c.message.answer(text = 'Пришлите excel файл')

#TODO: сделать проверку на существующие записи в бд
@router.message(Flag.wait_for_count)
async def process_file(message: Message, state: FSMContext):
    cost = message.text
    product_id = await state.get_data()
    print(message.text, product_id['name'])
    print(message.chat.id)
    db.insert_into_user_basket(str(message.chat.id), int(product_id['name']), int(cost))
    await state.clear()

@router.callback_query(F.data == 'get_porducts')
async def start(c: CallbackQuery, state: FSMContext):
    wb = openpyxl.Workbook()

    sheet = wb.active
    sheet.title = "Отчет"

    headers = ["Наименование", "Цена за штуку"]
    for col_num, header in enumerate(headers, start=1):
        cell = sheet.cell(row=1, column=col_num)
        cell.value = header

    data = []

    for row in db.show_products():
        data.append([row[1], row[2]])

    for row_num, row_data in enumerate(data, start=2):
        for col_num, value in enumerate(row_data, start=1):
            sheet.cell(row=row_num, column=col_num, value=value)

    wb.save("отчет_продаж.xlsx")
    input_file = FSInputFile("отчет_продаж.xlsx")
    await c.message.answer_document(document = input_file, caption = "вот ваш файл!")
    os.remove('отчет_продаж.xlsx')

#TODO: валидация excel файла
@router.message(Flag.wait_for_file)
async def process_file(message: Message, state: FSMContext):
    file_name = message.document.file_name
    file_id = message.document.file_id


    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, file_name)
    

    wb = openpyxl.load_workbook(file_name)
    sheet = wb.active  
    
    db.delete_from_products()
    f = True
    for row in sheet.iter_rows(values_only=True):
        if f:
            f = False
            continue
        db.save_products(row[0], row[1])

    os.remove(file_name)

    await state.clear()
    await message.reply("Загрузка прошла успешно")


@router.callback_query(F.data == 'back_to_start')
async def start(c: CallbackQuery):
    text = 'Приветственное сообщение'
    await c.message.edit_text(text = text, reply_markup = start_keyboard)


@router.callback_query(F.data == 'cabinet_basket')
async def personal_cabinet(c: CallbackQuery):
    text = 'Личный кабинет'
    await c.message.edit_text(text, reply_markup = personal_account_keyboard)