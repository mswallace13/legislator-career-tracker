import sqlite3
import time
from scraper import scrape_and_populate_bio

def scrape_all_unprocessed_legislators():
    conn = sqlite3.connect("legislators.db")
    cursor = conn.cursor()

    # Query legislators who don't have education or military details yet
    cursor.execute("""
        SELECT l.id, l.name, l.state 
        FROM legislators l
        LEFT JOIN education e ON l.id = e.legislator_id
        LEFT JOIN military_service m ON l.id = m.legislator_id
        WHERE e.legislator_id IS NULL AND m.legislator_id IS NULL
    """)
    unprocessed = cursor.fetchall()
    conn.close()

    print(f"Found {len(unprocessed)} legislators ready for scraping.")

    for leg_id, name, state in unprocessed:
        # Construct Wikipedia search / bio URL target
        formatted_name = name.replace(" ", "_")
        url = f"https://en.wikipedia.org/wiki/{formatted_name}"

        print(f"Scraping [{state}] {name} ({leg_id})...")
        scrape_and_populate_bio(leg_id, url)
        time.sleep(0.5)  # Respectful scraping rate limit

if __name__ == "__main__":
    scrape_all_unprocessed_legislators()