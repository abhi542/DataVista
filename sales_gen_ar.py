import pandas as pd
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker and define states
fake = Faker()
indian_states = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
    "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
    "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
    "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
    "Uttar Pradesh", "Uttarakhand", "West Bengal"
]

# Function to generate random time
def random_time():
    start = datetime.strptime('00:00:00', '%H:%M:%S')
    end = datetime.strptime('23:59:59', '%H:%M:%S')
    random_time = start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))
    return random_time.strftime('%H:%M:%S')

# Function to generate data
def generate_data(num_entries):
    data = []
    
    for _ in range(num_entries):
        invoice_id = fake.uuid4()
        branch = fake.company()
        city = random.choice(indian_states)
        customer_type = random.choice(['Regular', 'Guest'])
        gender = random.choice(['Male', 'Female'])
        product_line = random.choice(['Electronics', 'Furniture', 'Clothing', 'Groceries', 'Toys'])
        unit_price = round(random.uniform(10.0, 500.0), 2)
        quantity = random.randint(1, 10)
        tax = round(unit_price * quantity * 0.05, 2)
        total = round(unit_price * quantity + tax, 2)
        date = fake.date_this_year().strftime('%Y-%m-%d')
        time = random_time()  # Use custom random time function
        payment = random.choice(['Cash', 'Credit Card', 'Debit Card'])
        cogs = round(unit_price * quantity, 2)
        gross_margin_percentage = round((1 - (cogs / total)) * 100, 2)
        gross_income = round(total - cogs, 2)
        rating = round(random.uniform(1.0, 5.0), 1)
        
        data.append([
            invoice_id, branch, city, customer_type, gender, product_line, unit_price,
            quantity, tax, total, date, time, payment, cogs, gross_margin_percentage, 
            gross_income, rating
        ])
    
    # Create DataFrame
    columns = [
        'Invoice ID', 'Branch', 'City', 'Customer_type', 'Gender', 'Product line',
        'Unit price', 'Quantity', 'Tax 5%', 'Total', 'Date', 'Time', 'Payment', 
        'cogs', 'gross margin percentage', 'gross income', 'Rating'
    ]
    
    df = pd.DataFrame(data, columns=columns)
    return df

# Generate 2000 entries
df = generate_data(2000)

# Save to Excel with the sheet name "Sales"
df.to_excel('sales_data.xlsx', sheet_name='Sales', index=False, engine='openpyxl')

print("Data generation complete and saved to 'sales_data.xlsx' with sheet name 'Sales'")
