import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st



def classify_profile(row):
    if row['income'] > 75000:
        return "High Earners"
    elif 30000 <= row['income'] <= 75000 and row['marital_status'] == 'M' and row['total_children'] > 0:
        return "Middle Class Families"
    elif 30000 <= row['income'] <= 75000 and row['marital_status'] == 'S' and row['total_children'] == 0 and \
         row['education'] in ['Bachelors', 'Graduate Degree']:
        return "Young Professionals"
    elif row['income'] < 30000:
        return "Low Income"
    else:
        return "Other"



# Load the customer data
# Assuming the data has been preprocessed and includes the "Profile" column
@st.cache
def load_data():
    # Database connection parameters
    host = "mtas01.vlba.uni-oldenburg.de"          # e.g., "localhost" or "127.0.0.1"
    port = "5432"               # Default PostgreSQL port
    database = "bicourse_db_35"  # Database name
    user = "bicourse_user_35"      # PostgreSQL username
    password = "fVe9mkY291"  # PostgreSQL password


    # Connect to the database and fetch data
    try:
        # Establish connection
        connection = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        
        # Create a cursor object
        cursor = connection.cursor()
        
        # SQL query to fetch the required data
        query = """
        SELECT yearly_income, 
            marital_status, 
            total_children, 
            gender, 
            english_education, 
            house_owner_flag, 
            number_cars_owned
        FROM dim_customer; -- Replace with your actual table name
        """
        
        # Execute the query and fetch results
        cursor.execute(query)
        data = cursor.fetchall()
        
        # Load data into a DataFrame
        columns = ['income', 'marital_status', 'total_children', 'gender', 'education', 'house_owner', 'number_cars_owned']
        customer_data = pd.DataFrame(data, columns=columns)
        
        print("Data fetched successfully!")
        print(customer_data.head())  # Preview the data

    except Exception as error:
        print("Error while fetching data:", error)

    finally:
        if connection:
            cursor.close()
            connection.close()
            # Define profiles
    customer_data['Profile'] = customer_data.apply(lambda row: classify_profile(row), axis=1)

    return customer_data

customer_data = load_data()

# Sidebar for navigation
st.sidebar.title("Customer Profile Dashboard")
option = st.sidebar.selectbox("Choose a Section", ["Overview", "Business Insights"])

# Section: Overview
if option == "Overview":
    st.title("Customer Profile Distribution")
    
    # Profile Distribution Bar Chart
    profile_counts = customer_data['Profile'].value_counts()
    fig, ax = plt.subplots()
    profile_counts.plot(kind='bar', color=['skyblue', 'orange', 'green', 'red'], ax=ax)
    ax.set_title("Customer Profiles Distribution")
    ax.set_xlabel("Profile")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    st.write("This chart shows the number of customers in each profile.")

# Section: Business Insights
elif option == "Business Insights":
    st.title("Business Insights")

    # Question 1: Income Distribution by Profile
    st.subheader("Income Distribution Across Profiles")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(x='Profile', y='income', data=customer_data, ax=ax, palette="Set3")
    ax.set_title("Income Distribution by Customer Profile")
    st.pyplot(fig)
    st.write("This visualization shows income ranges for each profile, helping assess purchasing power.")

    # Question 2: Demographic Breakdown
    st.subheader("Demographics of Each Profile")
    demographic_breakdown = customer_data.groupby(['Profile', 'gender']).size().unstack()
    fig, ax = plt.subplots(figsize=(10, 6))
    demographic_breakdown.plot(kind='bar', stacked=True, ax=ax, colormap='viridis')
    ax.set_title("Gender Breakdown by Customer Profile")
    ax.set_xlabel("Profile")
    ax.set_ylabel("Count")
    st.pyplot(fig)
    st.write("This chart highlights gender distribution for each profile, useful for designing targeted campaigns.")
