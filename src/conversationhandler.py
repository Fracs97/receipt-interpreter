#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import os
from dotenv import load_dotenv
from google_api import ocr_summarize
import json
from datetime import datetime
from database import get_db
from models import User, Category, Receipt
from sqlalchemy import func

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

CATEGORY,BUDGET_FLOW_DECIDE, SET_BUDGET, CATEGORY_FLOW_DECIDE, RECEIPT = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    user = update.effective_user
    #Saving user into User table if not already present in database
    with get_db() as db:
        if db.query(User).filter(User.id == str(user.id)).first() is None:
            new_user = User(id = str(user.id))
            db.add(new_user)
            db.commit()
    await update.message.reply_text(
        f'Hello {user.first_name}, welcome to your expense tracker.')
    await update.message.reply_text("Let's start by setting up your expense categories.")
    await update.message.reply_text("What's the name of the category?")

    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the name of the expense category"""
    with get_db() as db:
        #Creating fixed category "Others"
        if (db.query(Category).filter(Category.user_id == str(update.effective_user.id)).filter(
                                      Category.category_name == 'Others')).first() is None:
            others = Category(user_id = update.effective_user.id,
                              category_name = 'Others')
            db.add(others)
            db.commit()
        #Checking if category already exists in the database for that user
        if (db.query(Category).filter(Category.user_id == str(update.effective_user.id)).filter(
                                      Category.category_name == update.message.text)).first() is not None:
            await update.message.reply_text("You have already registered that category.")
            await update.message.reply_text("What's the name of the new category?")
            return CATEGORY
    if 'categories' not in context.user_data:
        context.user_data['categories'] = []

    #adding category to context with no budget at first
    context.user_data['categories'].append({'name': update.message.text, 'budget': None})
    user = update.message.from_user
    logger.info("Category chosen by %s: %s", user.first_name, update.message.text)
    keyboard = [['Yes','No']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("Alright, do you wish to set a budget value for that?", reply_markup = reply_markup)
        
    return BUDGET_FLOW_DECIDE

async def budget_flow_decide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Decides where to direct the user concerning budget value"""
    logger.info("User answered %s", update.message.text)

    if update.message.text == 'Yes':
        await update.message.reply_text("How much?")
        return SET_BUDGET
    elif update.message.text == 'No':
        #saving category with no budget in categories table
        user = update.effective_user
        with get_db() as db:
            new_category = Category(user_id = str(user.id), 
                                    category_name = context.user_data['categories'][-1]['name'].capitalize())
            
            db.add(new_category)
            db.commit()

        keyboard = [['Yes','No']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

        await update.message.reply_text("Want to setup another category?", reply_markup = reply_markup)

        return CATEGORY_FLOW_DECIDE


async def set_budget(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the budget value for given category"""
    #context.user_data['categories'][-1]['budget'] = update.message.text
    user = update.effective_user
    #saving category with budget in categories table
    with get_db() as db:
            new_category = Category(user_id = str(user.id), 
                                    category_name = context.user_data['categories'][-1]['name'].capitalize(),
                                    budget = float(update.message.text))
            
            db.add(new_category)
            db.commit()

    logger.info("Budget value typed by %s: %s", user.first_name, update.message.text)
    keyboard = [['Yes','No']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text("Want to setup another category?", reply_markup = reply_markup)
        
    return CATEGORY_FLOW_DECIDE

async def category_flow_decide(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Decides where to direct the user concerning category registry"""
    if update.message.text == 'Yes':
        await update.message.reply_text("What's the name of the category?")
        return CATEGORY
    elif update.message.text == 'No':
        await update.message.reply_text('Your budget summary:')
        with get_db() as db:
            categories =  db.query(Category).filter(Category.user_id == str(update.effective_user.id)).all()
        for category in categories:
            if category.budget is None:
                await update.message.reply_text(f"{category.category_name} | No Budget.")
            else:
                await update.message.reply_text(f"{category.category_name} | Budget: U${category.budget}")
        await update.message.reply_text("Alright! Feel free to send a receipt whenever you want and I'll save the total value and tag it in the proper category.")
        return RECEIPT


async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Analyzes the receipt photo and returns summary"""
    receipt_file = await update.message.photo[-1].get_file()
    image_bytes = bytes(await receipt_file.download_as_bytearray())
    await update.message.reply_text(
        "Analyzing receipt data..."
    )
    user_id = str(update.effective_user.id)
    #checking all available categories to let gemini know how to categorize the expense
    with get_db() as db:
        categories = [x.category_name for x in db.query(Category).filter(Category.user_id == user_id).all()]

    response = ocr_summarize(image_bytes, categories).replace('`','').replace('json','')
    logger.info(response)
    response_json = json.loads(response)
    #if none of the categories match the one in the receipt, it is assigned to Others
    if response_json['date'] is None:
        response_json['date'] = str(datetime.today().strftime("%m/%d/%Y"))

    #Saving receipt data into database
    with get_db() as db:
        cat_id = db.query(Category).filter(Category.user_id == user_id).filter(Category.category_name == response_json['category']).first().id
        new_category = Receipt(user_id = str(user_id), 
                                category_id = cat_id,
                                expense_date = response_json['date'],
                                amount = float(response_json['amount']))
        
        db.add(new_category)
        db.commit()
    await update.message.reply_text(f'Date: {response_json['date']} | Category: {response_json['category']} | Total spent: {response_json['currency']}{response_json['amount']}')
    return RECEIPT

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Generates a summary for all expenses."""
    user_id = str(update.effective_user.id)
    await update.message.reply_text('Here is the summary of your expenses:')
    #Retrieving and grouping receipt data
    with get_db() as db:
        if db.query(Receipt).filter(Receipt.user_id == user_id).all() is not None:
            #joining receipts and categories table to recover category name and grouping expenses by category
            summary = (db.query(Category.category_name, func.sum(Receipt.amount), Category.budget)
                       .join(Category).filter(Receipt.user_id == user_id).group_by(Category.category_name, Category.budget)).all()
            for cat_name, amount, budget in summary:
                if budget is not None:
                    await update.message.reply_text(f'{cat_name}: {amount}/{budget} ({(100*amount/budget):.1f}%)')
                else:
                    await update.message.reply_text(f'{cat_name}: {amount}')

    return RECEIPT



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
            BUDGET_FLOW_DECIDE: [MessageHandler(filters.Regex("(?i)^(Yes|No)$"), budget_flow_decide)],
            SET_BUDGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_budget)],
            CATEGORY_FLOW_DECIDE: [MessageHandler(filters.Regex("(?i)^(Yes|No)$"), category_flow_decide)],
            RECEIPT: [MessageHandler(filters.PHOTO, receipt),
                      CommandHandler("summary", summary)]},
            fallbacks = [])
    

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()