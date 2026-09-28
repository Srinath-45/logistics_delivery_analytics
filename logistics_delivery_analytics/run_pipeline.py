from src.data_loader import load_data
from src.data_cleaner import clean_data
from src.business_analysis import generate_business_metrics
from src.visualization import generate_all_charts


def main():
    print("Starting logistics analytics pipeline...")

    # 1. Load raw data
    print("Loading raw data...")
    data = load_data()

    # 2. Clean and transform data
    print("Cleaning and transforming data...")
    cleaned_data = clean_data(data)

    # 3. Generate business metrics
    print("Generating business metrics...")
    generate_business_metrics(cleaned_data)

    # 4. Generate charts
    print("Generating charts...")
    generate_all_charts(cleaned_data)

    print("\nPipeline completed successfully!")


if __name__ == "__main__":
    main()