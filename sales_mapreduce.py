import pandas as pd

def read_data():
    try:
        # Load the entire sheet to inspect its content
        df = pd.read_excel(
            io='sales_data.xlsx',
            engine='openpyxl',
            sheet_name='Sales',  # Ensure this is the correct sheet name
            skiprows=0,  # Adjust if necessary
            nrows=1000
        )
        # Print column names to debug
        print("Columns in Excel file:", df.columns)
        
        # Ensure these columns exist in the DataFrame
        required_columns = [
            'Invoice ID', 'Branch', 'City', 'Customer_type', 'Gender', 'Product line',
            'Unit price', 'Quantity', 'Tax 5%', 'Total', 'Date', 'Time', 'Payment',
            'cogs', 'gross margin percentage', 'gross income', 'Rating'
        ]
        
        # Check if all required columns are present
        for col in required_columns:
            if col not in df.columns:
                raise KeyError(f"Column '{col}' not found in the Excel file.")
        
        # Filter out the necessary columns
        df = df[required_columns]
        df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
        
        return df
    except ValueError as e:
        print(f"Error reading the Excel file: {e}")
        return pd.DataFrame()  # Return empty DataFrame if error occurs
    except FileNotFoundError:
        print("Sales data file not found.")
        return pd.DataFrame()  # Return empty DataFrame if file is not found
    except KeyError as e:
        print(f"Column or sheet not found: {e}")
        return pd.DataFrame()  # Return empty DataFrame if column or sheet is missing
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return pd.DataFrame()  # Return empty DataFrame for unexpected errors

def mapper(df):
    results = {
        "total_sales": [],
        "product_line_sales": [],
        "hour_sales": [],
        "ratings": [],
        "customer_ids": []
    }

    for _, row in df.iterrows():
        product_line = row['Product line']
        total_sales = row['Total']
        rating = row['Rating']
        hour = row['hour']
        customer_id = row['Invoice ID']

        results["total_sales"].append(total_sales)
        results["product_line_sales"].append((product_line, total_sales))
        results["hour_sales"].append((hour, total_sales))
        results["ratings"].append(rating)
        results["customer_ids"].append(customer_id)

    return results

def reducer(mapped_data):
    total_sales = sum(mapped_data["total_sales"])
    total_transactions = len(mapped_data["total_sales"])
    avg_sale_per_transaction = total_sales / total_transactions if total_transactions > 0 else 0
    avg_rating = sum(mapped_data["ratings"]) / total_transactions if total_transactions > 0 else 0
    total_customers = len(set(mapped_data["customer_ids"]))

    product_sales = {}
    for product_line, sales in mapped_data["product_line_sales"]:
        if product_line not in product_sales:
            product_sales[product_line] = 0
        product_sales[product_line] += sales

    hour_sales = {}
    for hour, sales in mapped_data["hour_sales"]:
        if hour not in hour_sales:
            hour_sales[hour] = 0
        hour_sales[hour] += sales

    with open("product_sales.txt", "w") as file:
        for product_line, sales in product_sales.items():
            file.write(f"{product_line}: {sales}\n")

    return {
        "total_sales": total_sales,
        "total_transactions": total_transactions,
        "avg_sale_per_transaction": avg_sale_per_transaction,
        "avg_rating": avg_rating,
        "total_customers": total_customers,
        "product_sales": product_sales,
        "hour_sales": hour_sales
    }

def main():
    try:
        df = read_data()
        if df.empty:
            print("No data to process.")
            return
        mapped_data = mapper(df)
        kpi_data = reducer(mapped_data)
        print("MapReduce processing complete.")
        print("KPIs:", kpi_data)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
