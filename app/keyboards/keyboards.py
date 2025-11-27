from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "Личный Кабинет", callback_data = "cabinet_basket")],
        [InlineKeyboardButton(text = "Общая выпускаемая продукция", callback_data = "production")]])

personal_account_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "Просмотреть корзину", callback_data = "show_basket")],
        [InlineKeyboardButton(text = "Заказать товары", callback_data = "order_products")],
        [InlineKeyboardButton(text = "На главную страницу", callback_data = "back_to_start")]
])

admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text = "Загрузить товары", callback_data = "download_products")],
        [InlineKeyboardButton(text = "Выгрузить товары", callback_data = "get_porducts")],
        [InlineKeyboardButton(text = "На главную страницу", callback_data = "back_to_start")]
])

