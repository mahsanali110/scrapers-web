# Import datetime library
from datetime import date, timedelta
# Import the files and their respective functions
from dawn_english_articles import dawn_english
from get_categories import get_categories
from get_articles import get_article_data
from batch_latest import BatchGenerator

if __name__ == '__main__':
    while True:
        current_date = date.today().strftime('%Y-%m-%d')
        previous_date = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')

        categories = dawn_english(current_date)
        get_categories(categories, current_date)
        get_article_data(current_date)

        categories_previous = dawn_english(previous_date)
        get_categories(categories_previous, previous_date)
        get_article_data(previous_date)

        batch_generator = BatchGenerator()
        batch_generator.main()
