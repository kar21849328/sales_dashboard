import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration at the very beginning
st.set_page_config(
    page_title="✨ Data Insights Dashboard ✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set the authentication code
AUTH_CODE = "2580"

def authenticate():
    """Authenticate the user by verifying the code."""
    st.title("Authentication")
    code = st.text_input("Enter the authentication code:", type="password")
    if code == AUTH_CODE:
        return True
    else:
        if code:
            st.error("Invalid code. Please try again.")
        return False

def sales_data_analysis():
    """Execute the sales data analysis code."""
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>📊 Sales Insights Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.sidebar.title("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload Your Sales Data Excel File", type=["xlsx"])

    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file, sheet_name=0)
        data['TrDate'] = pd.to_datetime(data['TrDate'])
        data = data[data['GrossSales'] > 0]

        trend_period = st.selectbox(
            "📅 Choose Sales Trend Period",
            ["Weekly", "Monthly", "Quarterly", "Yearly"]
        )

        unique_outlets = data['PCNumber'].unique()
        selected_outlet = st.selectbox("🏢 Select Outlet for Trend Analysis", unique_outlets)

        # Key Performance Metrics
        total_sales = round(data['GrossSales'].sum() / 1e6, 2)
        total_customers = int(data['CustomerCount'].sum())
        average_sales = round(data['GrossSales'].mean(), 2)
        total_tax = round(data['SalesTax'].sum() / 1e6, 2)
        total_discount = round(data['DiscountRefund'].sum() / 1e6, 2)

        st.markdown("<h2 style='text-align: center; color: #333;'>📈 Key Performance Metrics</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col4, col5, col6 = st.columns(3)

        col1.metric("🏪 Outlets Count", f"{len(unique_outlets)}")
        col2.metric("💵 Total Sales (Millions)", f"${total_sales:,.2f}M")
        col3.metric("👥 Total Customers", f"{total_customers}")
        col4.metric("💸 Average Sales", f"${average_sales:,.2f}")
        col5.metric("💰 Total Tax (Millions)", f"${total_tax:,.2f}M")
        col6.metric("🎟️ Total Discount (Millions)", f"${total_discount:,.2f}M")

        st.markdown("---")
        st.markdown("<h2 style='text-align: center; color: #333;'>📅 Sales Trend Analysis for Selected Outlet</h2>", unsafe_allow_html=True)
        
        outlet_data = data[data['PCNumber'] == selected_outlet]
        if trend_period == "Weekly":
            sales_trend = outlet_data.groupby(outlet_data['TrDate'].dt.to_period("W")).agg({'GrossSales': 'sum'}).reset_index()
        elif trend_period == "Monthly":
            sales_trend = outlet_data.groupby(outlet_data['TrDate'].dt.to_period("M")).agg({'GrossSales': 'sum'}).reset_index()
        elif trend_period == "Quarterly":
            sales_trend = outlet_data.groupby(outlet_data['TrDate'].dt.to_period("Q")).agg({'GrossSales': 'sum'}).reset_index()
        else:
            sales_trend = outlet_data.groupby(outlet_data['TrDate'].dt.to_period("Y")).agg({'GrossSales': 'sum'}).reset_index()

        sales_trend['TrDate'] = sales_trend['TrDate'].dt.to_timestamp()
        fig_trend = px.line(sales_trend, x='TrDate', y='GrossSales', title=f"{trend_period} Sales Trend for Outlet {selected_outlet}", labels={"TrDate": "Date", "GrossSales": "Total Sales"}, template="plotly_dark")
        fig_trend.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_trend, use_container_width=True)

        st.markdown("<h2 style='text-align: center; color: #333;'>🏢 Sales Breakdown by Outlet</h2>", unsafe_allow_html=True)
        outlet_sales = data.groupby('PCNumber').agg({'GrossSales': 'sum'}).reset_index()
        outlet_sales['GrossSales'] = outlet_sales['GrossSales'] / 1e6

        fig_bar = px.bar(outlet_sales, x='PCNumber', y='GrossSales', title="Total Sales by Outlet (in Millions)", labels={"PCNumber": "Outlet/PC Name", "GrossSales": "Total Sales (Millions)"}, template="plotly_dark", text=outlet_sales['GrossSales'].round(2))
        fig_bar.update_traces(marker_color='#FF5733', width=0.3, textposition="outside")
        fig_bar.update_xaxes(type='category')
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("<h2 style='text-align: center; color: #333;'>📊 Store-Specific Metrics</h2>", unsafe_allow_html=True)
        
        customer_visits = data.groupby('PCNumber').agg({'CustomerCount': 'sum'}).reset_index()
        fig_customers = px.bar(customer_visits, x='PCNumber', y='CustomerCount', title="Total Customers Visited per Store", labels={"PCNumber": "Outlet/PC Name", "CustomerCount": "Customers Visited"}, template="plotly_dark", text=customer_visits['CustomerCount'])
        fig_customers.update_traces(width=0.3, textposition="outside")
        fig_customers.update_xaxes(type='category')
        st.plotly_chart(fig_customers, use_container_width=True)

        tax_per_store = data.groupby('PCNumber').agg({'SalesTax': 'sum'}).reset_index()
        tax_per_store['SalesTax'] = tax_per_store['SalesTax'] / 1e6

        fig_tax = px.bar(tax_per_store, x='PCNumber', y='SalesTax', title="Total Tax Paid per Store (Millions)", labels={"PCNumber": "Outlet/PC Name", "SalesTax": "Total Tax (Millions)"}, template="plotly_dark", text=tax_per_store['SalesTax'].round(2))
        fig_tax.update_traces(width=0.3, textposition="outside")
        fig_tax.update_xaxes(type='category')
        st.plotly_chart(fig_tax, use_container_width=True)

        discount_per_store = data.groupby('PCNumber').agg({'DiscountRefund': 'sum'}).reset_index()
        discount_per_store['DiscountRefund'] = discount_per_store['DiscountRefund'] / 1e6

        fig_discount = px.bar(discount_per_store, x='PCNumber', y='DiscountRefund', title="Total Discount per Store (Millions)", labels={"PCNumber": "Outlet/PC Name", "DiscountRefund": "Total Discount (Millions)"}, template="plotly_dark", text=discount_per_store['DiscountRefund'].round(2))
        fig_discount.update_traces(width=0.3, textposition="outside")
        fig_discount.update_xaxes(type='category')
        st.plotly_chart(fig_discount, use_container_width=True)

        avg_sales_per_store = data.groupby('PCNumber').agg({'GrossSales': 'mean'}).reset_index()
        fig_avg_sales = px.bar(avg_sales_per_store, x='PCNumber', y='GrossSales', title="Average Sales per Store (in Dollars)", labels={"PCNumber": "Outlet/PC Name", "GrossSales": "Average Sales"}, template="plotly_dark", text=avg_sales_per_store['GrossSales'].round(2))
        fig_avg_sales.update_traces(width=0.3, textposition="outside")
        fig_avg_sales.update_xaxes(type='category')
        st.plotly_chart(fig_avg_sales, use_container_width=True)

    else:
        st.info("Please upload an Excel file from the sidebar to view the dashboard.")

def products_data_analysis():
    """Execute the products data analysis code."""
    st.markdown("<h1 style='text-align: center; color: #FF5733;'>📊 Products Insights Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.sidebar.title("Upload Data")
    uploaded_file = st.sidebar.file_uploader("Upload Your Sales Data Excel File", type=["xlsx"])

    if uploaded_file is not None:
        data = pd.read_excel(uploaded_file, sheet_name='Sheet1')
        data['TrDate'] = pd.to_datetime(data['TrDate'])
        data['Sales'] = data['Sales'].abs()

        total_revenue = data['Sales'].sum()
        total_quantity_all_outlets = data['CheckQuantity'].sum()

        st.markdown("<h2 style='text-align: center; color: #333;'>🌐 Overall Metrics for All Outlets</h2>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.metric("💵 Total Revenue Generated", f"${total_revenue:,.2f}")
        col2.metric("📦 Total Quantity Sold", f"{total_quantity_all_outlets}")

        st.markdown("---")

        unique_outlets = data['PCNumber'].unique()
        selected_outlet = st.selectbox("🏢 Select Outlet for Analysis", unique_outlets)

        outlet_data = data[data['PCNumber'] == selected_outlet]

        total_sales = outlet_data['Sales'].sum()
        total_quantity_sold = outlet_data['CheckQuantity'].sum()
        top_category = outlet_data.groupby('Category')['Sales'].sum().idxmax()

        st.markdown("<h2 style='text-align: center; color: #333;'>📈 Key Performance Metrics for Selected Outlet</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("💵 Total Sales", f"${total_sales:,.2f}")
        col2.metric("📦 Total Quantity Sold", f"{total_quantity_sold}")
        col3.metric("🏆 Top Category", top_category)

        st.markdown("---")

        st.subheader("📅 Day-wise Revenue Trend Analysis")
        daily_sales = outlet_data.groupby('TrDate')['Sales'].sum().reset_index()
        fig_trend = px.line(daily_sales, x='TrDate', y='Sales', title=f"Day-wise Revenue Trend for Outlet {selected_outlet}", labels={"TrDate": "Date", "Sales": "Revenue"}, template="plotly_dark")
        fig_trend.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_trend, use_container_width=True)

        st.subheader("🏆 Top 10 Selling Products by Quantity Sold")
        top_products = outlet_data.groupby('RecipeName')['CheckQuantity'].sum().sort_values(ascending=False).head(10).reset_index()
        fig_top_products = px.bar(top_products, x='CheckQuantity', y='RecipeName', orientation='h', title="Top 10 Selling Products by Quantity Sold", labels={"CheckQuantity": "Quantity Sold", "RecipeName": "Product"}, template="plotly_dark", text='CheckQuantity')
        fig_top_products.update_traces(texttemplate='%{text}', textposition="outside")
        fig_top_products.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top_products, use_container_width=True)

        st.subheader("📊 Product Mix Ratios by Category")
        product_mix = outlet_data.groupby('Category')['Sales'].sum() / total_sales * 100
        product_mix = product_mix.reset_index().rename(columns={'Sales': 'SalesPercentage'})
        fig_product_mix = px.pie(product_mix, names='Category', values='SalesPercentage', title="Product Mix Ratios by Category", template="plotly_dark")
        st.plotly_chart(fig_product_mix, use_container_width=True)

        st.subheader("📈 Cumulative Sales Over Time")
        outlet_data = outlet_data.sort_values(by='TrDate')
        outlet_data['Cumulative Sales'] = outlet_data['Sales'].cumsum()
        fig_cumulative = px.line(outlet_data, x='TrDate', y='Cumulative Sales', title="Cumulative Sales Over Time", labels={"TrDate": "Date", "Cumulative Sales": "Cumulative Sales"}, template="plotly_dark")
        fig_cumulative.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig_cumulative, use_container_width=True)

        st.subheader("📊 Sales by Category and Subcategory")
        category_sales = outlet_data.groupby(['Category', 'Subcategory'])['Sales'].sum().reset_index()
        fig_category_sales = px.bar(category_sales, x='Sales', y='Subcategory', color='Category', orientation='h', title="Sales by Category and Subcategory", labels={"Sales": "Total Sales", "Subcategory": "Subcategory"}, template="plotly_dark", text='Sales')
        fig_category_sales.update_traces(texttemplate='$%{text:,.2f}', textposition="outside")
        fig_category_sales.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_category_sales, use_container_width=True)

        if data['PCNumber'].nunique() > 1:
            st.subheader("🏢 Total Sales by Outlet")
            sales_by_outlet = data.groupby('PCNumber')['Sales'].sum().reset_index()
            fig_outlet_sales = px.bar(sales_by_outlet, x='PCNumber', y='Sales', title="Total Sales by Outlet", labels={"PCNumber": "Outlet (PCNumber)", "Sales": "Total Sales"}, template="plotly_dark", text='Sales')
            fig_outlet_sales.update_traces(marker_color='#FF5733', texttemplate='$%{text:,.2f}', textposition="outside")
            st.plotly_chart(fig_outlet_sales, use_container_width=True)

    else:
        st.info("Please upload an Excel file to view the dashboard.")

def main():
    if authenticate():
        st.title("Data Analysis Options")
        option = st.selectbox("Choose an analysis type", ["Sales Data Analysis", "Products Data Analysis"])
        if option == "Sales Data Analysis":
            sales_data_analysis()
        elif option == "Products Data Analysis":
            products_data_analysis()

if __name__ == "__main__":
    main()
