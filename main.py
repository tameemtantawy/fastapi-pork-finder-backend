import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from database import SessionLocal, init_db
from models import Food, Food2
from allowed_food import scrape_foods
from allowed_food_JP import scrape_foodsJP
import asyncio
import pytz
from sqlalchemy.exc import IntegrityError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db():
    async with SessionLocal() as session:
        yield session

@app.get("/api/foods")
async def get_foods(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Food))
    foods = result.scalars().all()
    logger.info(f"Retrieved foods: {foods}")
    return {"foods": foods}

@app.get("/api/foodsJP")
async def get_foods_jp(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Food2))
    foods = result.scalars().all()
    logger.info(f"Retrieved foods: {foods}")
    return {"foods": foods}

@app.post("/api/scrape")
async def scrape_and_save_foods_endpoint(db: AsyncSession = Depends(get_db)):
    await scrape_and_save_foods(db)
    return {"message": "Foods scraped and saved successfully"}

@app.post("/api/scrapeJP")
async def scrape_and_save_foods_jp_endpoint(db: AsyncSession = Depends(get_db)):
    await scrape_and_save_foods_jp(db)
    return {"message": "Foods scraped and saved successfully"}

async def scrape_and_save_foods(db: AsyncSession):
    scraped_foods = scrape_foods()
    logger.info(f"Scraped foods: {scraped_foods}")

    # Clear existing foods
    await db.execute(delete(Food))

    # Use a set to keep track of unique food names
    seen_food_names = set()

    # Add new foods
    for restaurant in scraped_foods:
        for food in restaurant['foods']:
            if food['food'] not in seen_food_names:
                seen_food_names.add(food['food'])
                db.add(Food(
                    restaurant_name=restaurant['restaurant'],
                    name=food['food'],
                    contains_pork=food['contains_pork']
                ))

    try:
        await db.commit()
        logger.info("Foods saved successfully")
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Failed to commit changes to the database: {e}")

async def scrape_and_save_foods_jp(db: AsyncSession):
    scraped_foods = scrape_foodsJP()  # Replace this with your actual scraping function for the new page
    logger.info(f"Scraped foods for Food2: {scraped_foods}")

    # Clear existing foods in Food2
    await db.execute(delete(Food2))

    # Use a set to keep track of unique food names
    seen_food_names = set()

    # Add new foods to Food2
    for restaurant in scraped_foods:
        for food in restaurant['foods']:
            if food['food'] not in seen_food_names:
                seen_food_names.add(food['food'])
                db.add(Food2(
                    restaurant_name=restaurant['restaurant'],
                    name=food['food'],
                    contains_pork=food['contains_pork']
                ))

    try:
        await db.commit()
        logger.info("Foods for Food2 saved successfully")
    except IntegrityError as e:
        await db.rollback()
        logger.error(f"Failed to commit changes to the database (Food2): {e}")

        

async def scrape_and_save_foods_internal():
    async with SessionLocal() as session:
        await scrape_and_save_foods(session)

async def scrape_and_save_foods_internal_jp():
    async with SessionLocal() as session:
        await scrape_and_save_foods_jp(session)



def scrape_and_save_foods_sync():
    asyncio.run(scrape_and_save_foods_internal())

def scrape_and_save_foods_jp_sync():
    asyncio.run(scrape_and_save_foods_internal_jp())

@app.on_event("startup")
async def on_startup():
    await init_db()

    

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
