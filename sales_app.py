import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

# Set page configuration
st.set_page_config(page_title="DataVista: Realtime Sales Dashboard", page_icon='📈', layout='wide')

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(
            io='sales_data.xlsx',
            engine='openpyxl',
            sheet_name='Sales',  
            skiprows=0,  
            nrows=1000
        )
        
        required_columns = [
            'Invoice ID', 'Branch', 'City', 'Customer_type', 'Gender', 'Product line',
            'Unit price', 'Quantity', 'Tax 5%', 'Total', 'Date', 'Time', 'Payment',
            'cogs', 'gross margin percentage', 'gross income', 'Rating'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                st.error(f"Column '{col}' not found in the Excel file.")
                return pd.DataFrame() 
        
        df = df[required_columns]
        df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
        df["date"] = pd.to_datetime(df["Date"]).dt.date
        df["week"] = pd.to_datetime(df["Date"]).dt.to_period("W").apply(lambda r: r.start_time)
        df["month"] = pd.to_datetime(df["Date"]).dt.to_period("M")  # Add month column

        return df
    except ValueError as e:
        st.error(f"Error reading the Excel file: {e}")
        return pd.DataFrame()  
    except FileNotFoundError:
        st.error("Sales data file not found.")
        return pd.DataFrame()  
    except KeyError as e:
        st.error(f"Column or sheet not found: {e}")
        return pd.DataFrame()  
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return pd.DataFrame()  

@st.cache_data
def load_kpi_data():
    product_sales = {}
    hour_sales = {}

    try:
        with open("product_sales.txt", "r") as file:
            for line in file:
                product_line, sales = line.strip().split(": ")
                product_sales[product_line] = float(sales)
    except FileNotFoundError:
        st.error("Product sales data file not found.")
    
    return {
        "product_sales": product_sales,
        "hour_sales": hour_sales
    }

kpi_data = load_kpi_data()

df = load_data()

# Date Range Filter
st.sidebar.header("Filters")
date_range = st.sidebar.date_input("Select Date Range:", [])
if date_range:
    start_date, end_date = date_range
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
else:
    filtered_df = df

city_filter = st.sidebar.multiselect(
    "Select City:",
    options=df["City"].unique(),
    default=df["City"].unique() if not df.empty else []
)
customer_type_filter = st.sidebar.multiselect(
    "Select Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique() if not df.empty else []
)
gender_filter = st.sidebar.multiselect(
    "Select Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique() if not df.empty else []
)

filtered_df = filtered_df[
    (filtered_df["City"].isin(city_filter)) &
    (filtered_df["Customer_type"].isin(customer_type_filter)) &
    (filtered_df["Gender"].isin(gender_filter))
]

def calculate_kpis(df):
    total_sales = round(df["Total"].sum(), 2)
    total_transactions = len(df)
    avg_sale_per_transaction = round(total_sales / total_transactions, 2) if total_transactions > 0 else 0
    avg_rating = round(df["Rating"].mean(), 1)
    total_customers = len(df["Invoice ID"].unique())
    
    product_sales = df.groupby("Product line")["Total"].sum().round(2).to_dict()
    hour_sales = df.groupby("hour")["Total"].sum().round(2).to_dict()
    monthly_sales = df.groupby("month")["Total"].sum().round(2).to_dict()
    
    customer_type_sales = df.groupby("Customer_type")["Total"].sum().round(2).to_dict()
    gender_sales = df.groupby("Gender")["Total"].sum().round(2).to_dict()
    city_sales = df.groupby("City")["Total"].sum().round(2).to_dict()
    
    # Calculate Repeat Customer Rate
    repeat_customers = df["Invoice ID"].duplicated().sum()
    repeat_customer_rate = round((repeat_customers / total_customers) * 100, 2) if total_customers > 0 else 0

    # Estimate Customer Lifetime Value (CLV)
    avg_purchase_value = total_sales / total_customers if total_customers > 0 else 0
    purchase_frequency = total_transactions / total_customers if total_customers > 0 else 0
    avg_customer_value = avg_purchase_value * purchase_frequency
    avg_customer_lifespan = 5  # Assume a 5-year lifespan as an example
    clv = round(avg_customer_value * avg_customer_lifespan, 2)

    return {
        "total_sales": total_sales,
        "total_transactions": total_transactions,
        "avg_sale_per_transaction": avg_sale_per_transaction,
        "avg_rating": avg_rating,
        "total_customers": total_customers,
        "product_sales": product_sales,
        "hour_sales": hour_sales,
        "monthly_sales": monthly_sales,
        "customer_type_sales": customer_type_sales,
        "gender_sales": gender_sales,
        "city_sales": city_sales,
        "repeat_customer_rate": repeat_customer_rate,
        "clv": clv
    }

filtered_kpi_data = calculate_kpis(filtered_df)

st.title("DataVista: Realtime Sales Dashboard")

st.markdown("## Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Sales", f"$ {filtered_kpi_data['total_sales']:,}")
col2.metric("Total Transactions", filtered_kpi_data['total_transactions'])
col3.metric("Avg Sale/Transaction", f"$ {filtered_kpi_data['avg_sale_per_transaction']}")
col4.metric("Avg Rating", filtered_kpi_data['avg_rating'])
col5.metric("Total Customers", filtered_kpi_data['total_customers'])

st.markdown("---")

st.markdown("## Customer Segmentation")

# Sales by Customer Type
fig, ax = plt.subplots()
customer_types = list(filtered_kpi_data["customer_type_sales"].keys())
sales_by_customer_type = list(filtered_kpi_data["customer_type_sales"].values())
ax.pie(sales_by_customer_type, labels=customer_types, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
ax.axis('equal')
st.pyplot(fig)

# Sales by Gender
fig, ax = plt.subplots()
genders = list(filtered_kpi_data["gender_sales"].keys())
sales_by_gender = list(filtered_kpi_data["gender_sales"].values())
ax.pie(sales_by_gender, labels=genders, autopct='%1.1f%%', startangle=90, colors=plt.cm.Set2.colors)
ax.axis('equal')
st.pyplot(fig)

st.markdown("## City-based Analysis")
fig, ax = plt.subplots()
cities = list(filtered_kpi_data["city_sales"].keys())
sales_by_city = list(filtered_kpi_data["city_sales"].values())
ax.bar(cities, sales_by_city, color='c')
ax.set_xlabel("City")
ax.set_ylabel("Sales")
ax.set_title("Sales by City")
st.pyplot(fig)

st.markdown("## Additional Metrics")

col1, col2 = st.columns(2)
col1.metric("Repeat Customer Rate", f"{filtered_kpi_data['repeat_customer_rate']}%")
col2.metric("Customer Lifetime Value (CLV)", f"$ {filtered_kpi_data['clv']}")

st.markdown("---")

st.markdown("## Sales by Product Line")
fig, ax = plt.subplots()
product_lines = list(filtered_kpi_data["product_sales"].keys())
sales = list(filtered_kpi_data["product_sales"].values())
ax.pie(sales, labels=product_lines, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
ax.axis('equal')
st.pyplot(fig)

st.markdown("## Sales by Hour")
fig, ax = plt.subplots()
hours = list(filtered_kpi_data["hour_sales"].keys())
sales_by_hour = list(filtered_kpi_data["hour_sales"].values())
ax.plot(hours, sales_by_hour, marker='o', linestyle='-', color='b')
ax.set_xticks(hours)
ax.set_xlabel("Hour of the Day")
ax.set_ylabel("Sales")
ax.set_title("Sales by Hour")
st.pyplot(fig)

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
