import sys
import os
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ensure imports work from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import collect_all_news
from processDigest import process_digests
from generate_email import generate_daily_email

def run_pipeline():
    logger.info("========================================")
    logger.info("   STARTING AI NEWS AGGREGATOR PIPELINE")
    logger.info("========================================")
    start_time = time.time()

    try:
        # Step 1: Content Scraping
        logger.info("\n>>> STEP 1: CONTENT SCRAPING")
        collect_all_news()
        logger.info("Step 1 Complete.")

        # Step 2: Summarization
        logger.info("\n>>> STEP 2: GENERATING DIGESTS")
        process_digests()
        logger.info("Step 2 Complete.")

        # Step 3: Ranking & Email Generation
        # Note: generate_email.py includes the ranking logic internally
        logger.info("\n>>> STEP 3: RANKING & EMAIL GENERATION")
        generate_daily_email()
        logger.info("Step 3 Complete.")

        elapsed_time = time.time() - start_time
        logger.info("\n" + "="*40)
        logger.info(f"PIPELINE COMPLETED SUCCESSFULLY in {elapsed_time:.2f} seconds")
        logger.info("="*40)

    except Exception as e:
        logger.error(f"\n!!!!!!!!!!!!!! PIPELINE FAILED !!!!!!!!!!!!!!")
        logger.error(f"Error: {e}")
        logger.exception("Full traceback:")
        sys.exit(1)

if __name__ == "__main__":
    run_pipeline()
