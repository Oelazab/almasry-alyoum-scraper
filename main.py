from lib.amays import AlmasryalyoumScraper

if __name__ == "__main__":
    scraper = AlmasryalyoumScraper(max_retries=3, delay_range=(5, 15))
    results = scraper.scrape_articles(keyword="سد النهضة", limit=12)
    
    print(f"\nScraped {len(results)} articles:")
    for idx, article in enumerate(results, 1):
        print(f"{idx}. {article['title']}")
        print(f"   Time: {article['time']}")
        print(f"   URL: {article['url']}\n")
    
    scraper.save_to_json(results)