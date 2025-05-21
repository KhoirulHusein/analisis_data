import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    # Membaca file CSV dari dataset e-commerce
    customers_df = pd.read_csv('data/customers_dataset.csv')
    geolocation_df = pd.read_csv('data/geolocation_dataset.csv')
    order_items_df = pd.read_csv('data/order_items_dataset.csv')
    order_payments_df = pd.read_csv('data/order_payments_dataset.csv')
    order_reviews_df = pd.read_csv('data/order_reviews_dataset.csv')
    orders_df = pd.read_csv('data/orders_dataset.csv')
    products_df = pd.read_csv('data/products_dataset.csv')
    sellers_df = pd.read_csv('data/sellers_dataset.csv')
    category_name_translation_df = pd.read_csv('data/product_category_name_translation.csv')
    
    # Mengkonversi kolom timestamp pada dataset orders menjadi format datetime
    timestamp_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 
                        'order_delivered_customer_date', 'order_estimated_delivery_date']

    for col in timestamp_columns:
        orders_df[col] = pd.to_datetime(orders_df[col])
    
    # Mengkonversi kolom timestamp pada dataset order_reviews menjadi format datetime
    review_timestamp_columns = ['review_creation_date', 'review_answer_timestamp']

    for col in review_timestamp_columns:
        order_reviews_df[col] = pd.to_datetime(order_reviews_df[col])
    
    # Menangani nilai yang hilang pada dataset products
    products_df['product_category_name'] = products_df['product_category_name'].fillna('unknown')
    
    # Menggabungkan dataset products dengan category_name_translation
    products_with_category_df = products_df.merge(category_name_translation_df, on='product_category_name', how='left')
    products_with_category_df['product_category_name_english'] = products_with_category_df['product_category_name_english'].fillna(products_with_category_df['product_category_name'])
    
    # Menghitung waktu pengiriman untuk pesanan yang telah dikirim
    delivered_orders_df = orders_df[orders_df['order_status'] == 'delivered'].copy()
    delivered_orders_df['delivery_time_days'] = (delivered_orders_df['order_delivered_customer_date'] - 
                                                delivered_orders_df['order_purchase_timestamp']).dt.days
    delivered_orders_df['delivery_vs_estimate_days'] = (delivered_orders_df['order_delivered_customer_date'] - 
                                                      delivered_orders_df['order_estimated_delivery_date']).dt.days
    
    # Ekstrak informasi waktu dari order_purchase_timestamp
    orders_df['purchase_hour'] = orders_df['order_purchase_timestamp'].dt.hour
    orders_df['purchase_day'] = orders_df['order_purchase_timestamp'].dt.day_name()
    orders_df['purchase_month'] = orders_df['order_purchase_timestamp'].dt.month_name()
    orders_df['purchase_year'] = orders_df['order_purchase_timestamp'].dt.year
    orders_df['purchase_date'] = orders_df['order_purchase_timestamp'].dt.date
    
    return {
        'customers': customers_df,
        'geolocation': geolocation_df,
        'order_items': order_items_df,
        'order_payments': order_payments_df,
        'order_reviews': order_reviews_df,
        'orders': orders_df,
        'products': products_df,
        'products_with_category': products_with_category_df,
        'sellers': sellers_df,
        'delivered_orders': delivered_orders_df
    }

# Fungsi untuk menghitung metrik utama
@st.cache_data
def calculate_metrics(data):
    # Jumlah pelanggan unik
    unique_customers = data['customers']['customer_unique_id'].nunique()
    
    # Jumlah pesanan
    total_orders = len(data['orders'])
    
    # Jumlah produk
    total_products = len(data['products'])
    
    # Total pendapatan
    data['order_items']['total_price'] = data['order_items']['price'] + data['order_items']['freight_value']
    total_revenue = data['order_items']['total_price'].sum()
    
    # Rating rata-rata
    avg_rating = data['order_reviews']['review_score'].mean()
    
    # Waktu pengiriman rata-rata (dalam hari)
    avg_delivery_time = data['delivered_orders']['delivery_time_days'].mean()
    
    return {
        'unique_customers': unique_customers,
        'total_orders': total_orders,
        'total_products': total_products,
        'total_revenue': total_revenue,
        'avg_rating': avg_rating,
        'avg_delivery_time': avg_delivery_time
    }

# Fungsi untuk analisis pola pembelian berdasarkan waktu
@st.cache_data
def time_analysis(data):
    # Analisis pola pembelian berdasarkan jam
    hourly_orders = data['orders']['purchase_hour'].value_counts().sort_index()
    
    # Analisis pola pembelian berdasarkan hari
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_orders = data['orders']['purchase_day'].value_counts().reindex(day_order)
    
    # Analisis pola pembelian berdasarkan bulan
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    monthly_orders = data['orders']['purchase_month'].value_counts().reindex(month_order)
    
    # Analisis tren pembelian berdasarkan waktu (time series)
    daily_order_counts = data['orders'].groupby('purchase_date').size().reset_index(name='order_count')
    daily_order_counts['purchase_date'] = pd.to_datetime(daily_order_counts['purchase_date'])
    
    return {
        'hourly_orders': hourly_orders,
        'daily_orders': daily_orders,
        'monthly_orders': monthly_orders,
        'daily_order_counts': daily_order_counts
    }

# Fungsi untuk analisis kategori produk
@st.cache_data
def product_category_analysis(data):
    # Menggabungkan dataset order_items dengan products_with_category
    order_items_with_category = data['order_items'].merge(data['products_with_category'], on='product_id', how='left')
    
    # Menghitung jumlah produk yang terjual per kategori
    category_sales_count = order_items_with_category.groupby('product_category_name_english').size().reset_index(name='sales_count')
    category_sales_count = category_sales_count.sort_values('sales_count', ascending=False)
    
    # Menghitung total pendapatan per kategori produk
    order_items_with_category['total_price'] = order_items_with_category['price'] + order_items_with_category['freight_value']
    category_revenue = order_items_with_category.groupby('product_category_name_english')['total_price'].sum().reset_index()
    category_revenue = category_revenue.sort_values('total_price', ascending=False)
    
    # Menghitung harga rata-rata per kategori produk
    category_avg_price = order_items_with_category.groupby('product_category_name_english')['price'].mean().reset_index()
    category_avg_price = category_avg_price.sort_values('price', ascending=False)
    
    return {
        'order_items_with_category': order_items_with_category,
        'category_sales_count': category_sales_count,
        'category_revenue': category_revenue,
        'category_avg_price': category_avg_price
    }

# Fungsi untuk analisis performa penjual
@st.cache_data
def seller_performance_analysis(data):
    # Menggabungkan dataset order_items dengan sellers
    order_items_with_seller = data['order_items'].merge(data['sellers'], on='seller_id', how='left')
    
    # Menghitung jumlah penjualan dan pendapatan per penjual
    seller_performance = order_items_with_seller.groupby('seller_id').agg(
        sales_count=('order_id', 'count'),
        total_revenue=('price', 'sum'),
        avg_price=('price', 'mean'),
        seller_state=('seller_state', 'first'),
        seller_city=('seller_city', 'first')
    ).reset_index()
    
    # Menghitung rating rata-rata per pesanan
    order_ratings = data['order_reviews'].groupby('order_id')['review_score'].mean().reset_index()
    
    # Menggabungkan dengan order_items untuk mendapatkan rating per penjual
    order_items_with_rating = data['order_items'].merge(order_ratings, on='order_id', how='left')
    seller_ratings = order_items_with_rating.groupby('seller_id')['review_score'].mean().reset_index()
    
    # Menggabungkan performa penjual dengan rating
    seller_performance = seller_performance.merge(seller_ratings, on='seller_id', how='left')
    
    # Analisis performa penjual berdasarkan lokasi
    state_performance = seller_performance.groupby('seller_state').agg(
        seller_count=('seller_id', 'nunique'),
        avg_sales=('sales_count', 'mean'),
        avg_revenue=('total_revenue', 'mean'),
        avg_rating=('review_score', 'mean')
    ).reset_index()
    
    return {
        'seller_performance': seller_performance,
        'state_performance': state_performance
    }

# Fungsi untuk analisis RFM
@st.cache_data
def rfm_analysis(data):
    # Menggabungkan dataset orders dengan order_items
    orders_with_items = data['orders'].merge(data['order_items'], on='order_id', how='left')
    orders_with_items['total_price'] = orders_with_items['price'] + orders_with_items['freight_value']
    
    # Menentukan tanggal referensi (tanggal terakhir dalam dataset + 1 hari)
    reference_date = data['orders']['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    # Menghitung RFM untuk setiap pelanggan
    rfm = orders_with_items.groupby('customer_id').agg({
        'order_purchase_timestamp': lambda x: (reference_date - x.max()).days,  # Recency (dalam hari)
        'order_id': 'nunique',  # Frequency
        'total_price': 'sum'  # Monetary
    }).reset_index()
    
    rfm.columns = ['customer_id', 'recency', 'frequency', 'monetary']
    
    # Membuat skor RFM (1-5, 5 adalah yang terbaik)
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    
    # Menghitung skor RFM gabungan
    rfm['rfm_score'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)
    
    # Membuat segmen pelanggan berdasarkan skor RFM
    rfm['customer_segment'] = pd.qcut(rfm['rfm_score'], 4, labels=['Bronze', 'Silver', 'Gold', 'Platinum'])
    
    # Menghitung jumlah pelanggan per segmen
    segment_counts = rfm['customer_segment'].value_counts().reset_index()
    segment_counts.columns = ['customer_segment', 'count']
    
    # Analisis karakteristik setiap segmen pelanggan
    segment_analysis = rfm.groupby('customer_segment').agg({
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'customer_id': 'count'
    }).reset_index()
    
    segment_analysis.columns = ['customer_segment', 'avg_recency', 'avg_frequency', 'avg_monetary', 'customer_count']
    
    return {
        'rfm': rfm,
        'segment_counts': segment_counts,
        'segment_analysis': segment_analysis
    }

# Sidebar
st.sidebar.title("E-Commerce Dashboard")
st.sidebar.image("https://img.icons8.com/color/96/000000/shopping-cart--v2.png", width=100)

# Menu navigasi
page = st.sidebar.radio("Navigasi", ["Beranda", "Pola Pembelian", "Analisis Kategori Produk", "Performa Penjual", "Segmentasi Pelanggan (RFM)", "Insight & Kesimpulan"])

# Memuat data
data = load_data()
metrics = calculate_metrics(data)

# Halaman Beranda
if page == "Beranda":
    st.title("Dashboard Analisis E-Commerce")
    st.markdown("Dashboard ini menyajikan analisis komprehensif dari dataset e-commerce publik, mencakup pola pembelian, kategori produk, performa penjual, dan segmentasi pelanggan.")
    
    # Metrik utama
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Jumlah Pelanggan", f"{metrics['unique_customers']:,}")
        st.metric("Jumlah Pesanan", f"{metrics['total_orders']:,}")
    
    with col2:
        st.metric("Jumlah Produk", f"{metrics['total_products']:,}")
        st.metric("Total Pendapatan", f"R$ {metrics['total_revenue']:,.2f}")
    
    with col3:
        st.metric("Rating Rata-rata", f"{metrics['avg_rating']:.2f}/5")
        st.metric("Waktu Pengiriman Rata-rata", f"{metrics['avg_delivery_time']:.1f} hari")
    
    # Grafik tren pesanan harian
    st.subheader("Tren Pesanan Harian")
    time_data = time_analysis(data)
    fig = px.line(time_data['daily_order_counts'], x='purchase_date', y='order_count',
                 title='Tren Jumlah Pesanan Harian')
    fig.update_layout(xaxis_title='Tanggal', yaxis_title='Jumlah Pesanan')
    st.plotly_chart(fig, use_container_width=True)
    
    # Grafik kategori produk terlaris
    st.subheader("Kategori Produk Terlaris")
    product_data = product_category_analysis(data)
    fig = px.bar(product_data['category_sales_count'].head(10), 
                x='sales_count', y='product_category_name_english',
                title='10 Kategori Produk Terlaris',
                labels={'sales_count': 'Jumlah Penjualan', 'product_category_name_english': 'Kategori Produk'},
                orientation='h')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)

# Halaman Pola Pembelian
elif page == "Pola Pembelian":
    st.title("Analisis Pola Pembelian")
    st.markdown("Analisis pola pembelian pelanggan berdasarkan waktu (jam, hari, bulan) dan lokasi geografis.")
    
    time_data = time_analysis(data)
    
    # Pola pembelian berdasarkan jam
    st.subheader("Pola Pembelian Berdasarkan Jam")
    fig = px.bar(x=time_data['hourly_orders'].index, y=time_data['hourly_orders'].values,
                labels={'x': 'Jam (0-23)', 'y': 'Jumlah Pesanan'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Pola pembelian berdasarkan hari
    st.subheader("Pola Pembelian Berdasarkan Hari")
    fig = px.bar(x=time_data['daily_orders'].index, y=time_data['daily_orders'].values,
                labels={'x': 'Hari', 'y': 'Jumlah Pesanan'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Pola pembelian berdasarkan bulan
    st.subheader("Pola Pembelian Berdasarkan Bulan")
    fig = px.bar(x=time_data['monthly_orders'].index, y=time_data['monthly_orders'].values,
                labels={'x': 'Bulan', 'y': 'Jumlah Pesanan'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Heatmap jam vs hari
    st.subheader("Pola Pembelian: Jam vs Hari")
    orders_df = data['orders']
    orders_df['purchase_day_num'] = orders_df['order_purchase_timestamp'].dt.dayofweek
    hour_day_pivot = pd.crosstab(index=orders_df['purchase_hour'], columns=orders_df['purchase_day_num'])
    hour_day_pivot.columns = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
    
    fig = px.imshow(hour_day_pivot, 
                   labels=dict(x="Hari", y="Jam", color="Jumlah Pesanan"),
                   x=hour_day_pivot.columns,
                   y=hour_day_pivot.index,
                   color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
    
    # Analisis pola pembelian berdasarkan lokasi geografis
    st.subheader("Pola Pembelian Berdasarkan Lokasi")
    
    # Menggabungkan dataset orders dengan customers
    orders_with_location = data['orders'].merge(data['customers'], on='customer_id', how='left')
    
    # Menghitung jumlah pesanan per negara bagian
    state_orders = orders_with_location['customer_state'].value_counts().reset_index()
    state_orders.columns = ['customer_state', 'order_count']
    
    fig = px.bar(state_orders.head(10), 
                x='customer_state', 
                y='order_count',
                title='10 Negara Bagian dengan Jumlah Pesanan Tertinggi',
                labels={'customer_state': 'Negara Bagian', 'order_count': 'Jumlah Pesanan'},
                color='order_count',
                color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

# Halaman Analisis Kategori Produk
elif page == "Analisis Kategori Produk":
    st.title("Analisis Kategori Produk")
    st.markdown("Analisis kategori produk yang paling populer dan menghasilkan pendapatan tertinggi.")
    
    product_data = product_category_analysis(data)
    
    # Kategori produk terlaris
    st.subheader("Kategori Produk Terlaris")
    fig = px.bar(product_data['category_sales_count'].head(15), 
                x='sales_count', y='product_category_name_english',
                title='15 Kategori Produk Terlaris',
                labels={'sales_count': 'Jumlah Penjualan', 'product_category_name_english': 'Kategori Produk'},
                orientation='h')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Kategori dengan pendapatan tertinggi
    st.subheader("Kategori dengan Pendapatan Tertinggi")
    fig = px.bar(product_data['category_revenue'].head(15), 
                x='total_price', y='product_category_name_english',
                title='15 Kategori Produk dengan Pendapatan Tertinggi',
                labels={'total_price': 'Total Pendapatan (R$)', 'product_category_name_english': 'Kategori Produk'},
                orientation='h')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Kategori dengan harga rata-rata tertinggi
    st.subheader("Kategori dengan Harga Rata-rata Tertinggi")
    fig = px.bar(product_data['category_avg_price'].head(15), 
                x='price', y='product_category_name_english',
                title='15 Kategori Produk dengan Harga Rata-rata Tertinggi',
                labels={'price': 'Harga Rata-rata (R$)', 'product_category_name_english': 'Kategori Produk'},
                orientation='h')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Hubungan antara jumlah penjualan dan pendapatan
    st.subheader("Hubungan antara Jumlah Penjualan dan Pendapatan")
    
    # Menggabungkan informasi jumlah penjualan dan pendapatan
    category_analysis = product_data['category_sales_count'].merge(product_data['category_revenue'], on='product_category_name_english', how='inner')
    category_analysis = category_analysis.rename(columns={'total_price': 'total_revenue'})
    
    fig = px.scatter(category_analysis, 
                    x='sales_count', 
                    y='total_revenue',
                    title='Hubungan antara Jumlah Penjualan dan Total Pendapatan per Kategori',
                    labels={'sales_count': 'Jumlah Penjualan', 'total_revenue': 'Total Pendapatan (R$)'},
                    hover_name='product_category_name_english',
                    size='sales_count',
                    color='total_revenue',
                    color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

# Halaman Performa Penjual
elif page == "Performa Penjual":
    st.title("Analisis Performa Penjual")
    st.markdown("Analisis performa penjual berdasarkan lokasi, volume penjualan, dan rating pelanggan.")
    
    seller_data = seller_performance_analysis(data)
    
    # Jumlah penjual per negara bagian
    st.subheader("Jumlah Penjual per Negara Bagian")
    top_seller_states = seller_data['state_performance'].sort_values('seller_count', ascending=False).head(10)
    
    fig = px.bar(top_seller_states, 
                x='seller_state', 
                y='seller_count',
                title='10 Negara Bagian dengan Jumlah Penjual Tertinggi',
                labels={'seller_state': 'Negara Bagian', 'seller_count': 'Jumlah Penjual'},
                color='avg_rating',
                color_continuous_scale='RdYlGn',
                text='avg_rating')
    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    # Hubungan antara volume penjualan dan rating
    st.subheader("Hubungan antara Volume Penjualan dan Rating")
    
    # Menambahkan kategori berdasarkan volume penjualan
    seller_data['seller_performance']['sales_category'] = pd.qcut(seller_data['seller_performance']['sales_count'], 4, labels=['Low', 'Medium-Low', 'Medium-High', 'High'])
    
    # Menghitung rating rata-rata per kategori volume penjualan
    sales_category_ratings = seller_data['seller_performance'].groupby('sales_category')['review_score'].agg(['mean', 'count']).reset_index()
    
    fig = px.bar(sales_category_ratings, 
                x='sales_category', 
                y='mean',
                title='Rating Rata-rata Berdasarkan Volume Penjualan',
                labels={'sales_category': 'Kategori Volume Penjualan', 'mean': 'Rating Rata-rata'},
                color='mean',
                color_continuous_scale='RdYlGn',
                text='count')
    fig.update_traces(texttemplate='%{text} penjual', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)
    
    # Analisis waktu pengiriman dan pengaruhnya terhadap rating
    st.subheader("Pengaruh Waktu Pengiriman terhadap Rating")
    
    # Menggabungkan dataset orders dengan order_reviews
    delivery_reviews = data['delivered_orders'].merge(data['order_reviews'], on='order_id', how='inner')
    
    # Mengelompokkan waktu pengiriman menjadi beberapa kategori
    delivery_reviews['delivery_time_category'] = pd.cut(delivery_reviews['delivery_time_days'], 
                                                      bins=[0, 7, 14, 21, 28, float('inf')],
                                                      labels=['1 week', '2 weeks', '3 weeks', '4 weeks', '> 4 weeks'])
    
    # Menghitung rating rata-rata per kategori waktu pengiriman
    delivery_time_ratings = delivery_reviews.groupby('delivery_time_category')['review_score'].agg(['mean', 'count']).reset_index()
    
    fig = px.bar(delivery_time_ratings, 
                x='delivery_time_category', 
                y='mean',
                title='Rating Rata-rata Berdasarkan Waktu Pengiriman',
                labels={'delivery_time_category': 'Waktu Pengiriman', 'mean': 'Rating Rata-rata'},
                color='mean',
                color_continuous_scale='RdYlGn',
                text='count')
    fig.update_traces(texttemplate='%{text} pesanan', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

# Halaman Segmentasi Pelanggan (RFM)
elif page == "Segmentasi Pelanggan (RFM)":
    st.title("Segmentasi Pelanggan (RFM Analysis)")
    st.markdown("Analisis RFM (Recency, Frequency, Monetary) untuk segmentasi pelanggan.")
    
    rfm_data = rfm_analysis(data)
    
    # Distribusi segmen pelanggan
    st.subheader("Distribusi Segmen Pelanggan")
    fig = px.pie(rfm_data['segment_counts'], 
                values='count', 
                names='customer_segment',
                title='Segmentasi Pelanggan Berdasarkan Analisis RFM',
                color='customer_segment',
                color_discrete_map={'Bronze': '#CD7F32', 'Silver': '#C0C0C0', 'Gold': '#FFD700', 'Platinum': '#E5E4E2'})
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, use_container_width=True)
    
    # Karakteristik segmen pelanggan
    st.subheader("Karakteristik Segmen Pelanggan")
    
    # Recency
    fig = px.bar(rfm_data['segment_analysis'], 
                x='customer_segment', 
                y='avg_recency',
                title='Rata-rata Recency per Segmen (hari)',
                labels={'customer_segment': 'Segmen Pelanggan', 'avg_recency': 'Rata-rata Recency (hari)'},
                color='customer_segment',
                color_discrete_map={'Bronze': '#CD7F32', 'Silver': '#C0C0C0', 'Gold': '#FFD700', 'Platinum': '#E5E4E2'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Frequency
    fig = px.bar(rfm_data['segment_analysis'], 
                x='customer_segment', 
                y='avg_frequency',
                title='Rata-rata Frequency per Segmen (pesanan)',
                labels={'customer_segment': 'Segmen Pelanggan', 'avg_frequency': 'Rata-rata Frequency (pesanan)'},
                color='customer_segment',
                color_discrete_map={'Bronze': '#CD7F32', 'Silver': '#C0C0C0', 'Gold': '#FFD700', 'Platinum': '#E5E4E2'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Monetary
    fig = px.bar(rfm_data['segment_analysis'], 
                x='customer_segment', 
                y='avg_monetary',
                title='Rata-rata Monetary per Segmen (R$)',
                labels={'customer_segment': 'Segmen Pelanggan', 'avg_monetary': 'Rata-rata Monetary (R$)'},
                color='customer_segment',
                color_discrete_map={'Bronze': '#CD7F32', 'Silver': '#C0C0C0', 'Gold': '#FFD700', 'Platinum': '#E5E4E2'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Jumlah pelanggan per segmen
    fig = px.bar(rfm_data['segment_analysis'], 
                x='customer_segment', 
                y='customer_count',
                title='Jumlah Pelanggan per Segmen',
                labels={'customer_segment': 'Segmen Pelanggan', 'customer_count': 'Jumlah Pelanggan'},
                color='customer_segment',
                color_discrete_map={'Bronze': '#CD7F32', 'Silver': '#C0C0C0', 'Gold': '#FFD700', 'Platinum': '#E5E4E2'})
    st.plotly_chart(fig, use_container_width=True)

# Halaman Insight & Kesimpulan
elif page == "Insight & Kesimpulan":
    st.title("Insight & Kesimpulan")
    
    st.header("1. Pola Pembelian Pelanggan")
    st.markdown("""
    **Insight:**
    - Pelanggan paling aktif melakukan pembelian pada jam kerja (10:00-18:00) pada hari kerja (Senin-Jumat), dengan puncak aktivitas pada siang hingga sore hari.
    - Terdapat penurunan aktivitas pembelian pada akhir pekan, terutama pada hari Minggu.
    - Negara bagian SP (São Paulo), RJ (Rio de Janeiro), dan MG (Minas Gerais) memiliki jumlah pesanan tertinggi, yang mencerminkan konsentrasi populasi di Brasil.
    
    **Rekomendasi:**
    - Optimalkan kampanye pemasaran dan promosi pada jam 10:00-18:00 pada hari kerja untuk meningkatkan konversi.
    - Pertimbangkan untuk memberikan insentif khusus (seperti diskon atau pengiriman gratis) pada akhir pekan untuk meningkatkan aktivitas pembelian pada periode tersebut.
    - Sesuaikan strategi pemasaran berdasarkan lokasi geografis, dengan fokus pada negara bagian dengan jumlah pesanan tertinggi (SP, RJ, MG).
    """)
    
    st.header("2. Kategori Produk Terpopuler dan Pendapatan")
    st.markdown("""
    **Insight:**
    - Kategori produk terlaris adalah bed_bath_table (tempat tidur, meja, dan perlengkapan kamar mandi), health_beauty (kesehatan dan kecantikan), dan sports_leisure (olahraga dan rekreasi).
    - Kategori dengan pendapatan tertinggi adalah health_beauty, watches_gifts (jam tangan dan hadiah), dan computers_accessories (komputer dan aksesori).
    - Terdapat korelasi negatif antara harga rata-rata produk dan jumlah penjualan, yang menunjukkan bahwa produk dengan harga lebih rendah cenderung terjual lebih banyak.
    
    **Rekomendasi:**
    - Fokus pada pengembangan dan pemasaran kategori produk terlaris untuk mempertahankan volume penjualan yang tinggi.
    - Optimalkan strategi harga dan promosi untuk kategori dengan pendapatan tinggi untuk meningkatkan margin keuntungan.
    - Pertimbangkan untuk menerapkan strategi bundling produk, menggabungkan produk dari kategori terlaris dengan produk dari kategori dengan pendapatan tinggi.
    """)
    
    st.header("3. Performa Penjual")
    st.markdown("""
    **Insight:**
    - Negara bagian SP (São Paulo) memiliki jumlah penjual tertinggi, diikuti oleh RJ (Rio de Janeiro) dan MG (Minas Gerais).
    - Penjual dengan volume penjualan tinggi cenderung memiliki rating yang lebih tinggi, yang menunjukkan hubungan positif antara pengalaman penjual dan kepuasan pelanggan.
    - Waktu pengiriman memiliki pengaruh signifikan terhadap rating pelanggan, dengan pesanan yang dikirim lebih cepat mendapatkan rating yang lebih tinggi.
    
    **Rekomendasi:**
    - Berikan insentif dan dukungan kepada penjual dengan volume penjualan rendah untuk meningkatkan performa mereka.
    - Implementasikan program pelatihan dan sertifikasi untuk penjual baru untuk meningkatkan kualitas layanan mereka.
    - Optimalkan proses logistik dan pengiriman untuk mengurangi waktu pengiriman, terutama untuk pesanan dengan jarak jauh.
    """)
    
    st.header("4. Segmentasi Pelanggan (RFM)")
    st.markdown("""
    **Insight:**
    - Segmentasi pelanggan berdasarkan analisis RFM menghasilkan empat segmen: Bronze, Silver, Gold, dan Platinum.
    - Segmen Platinum memiliki nilai recency terendah (pembelian terbaru), frequency tertinggi (jumlah pesanan), dan monetary tertinggi (total pengeluaran).
    - Setiap segmen pelanggan memiliki preferensi kategori produk yang berbeda.
    
    **Rekomendasi:**
    - Kembangkan program loyalitas yang disesuaikan untuk setiap segmen pelanggan, dengan fokus pada mempertahankan pelanggan Platinum dan meningkatkan pelanggan Gold ke Platinum.
    - Implementasikan strategi retensi untuk pelanggan Bronze dan Silver, seperti penawaran khusus dan komunikasi yang ditargetkan.
    - Sesuaikan rekomendasi produk berdasarkan preferensi kategori untuk setiap segmen pelanggan.
    """)
    
    st.header("Kesimpulan Akhir")
    st.markdown("""
    Analisis data e-commerce ini memberikan wawasan berharga tentang pola pembelian pelanggan, kategori produk populer, performa penjual, dan segmentasi pelanggan. Dengan menerapkan rekomendasi yang diusulkan, perusahaan dapat meningkatkan strategi pemasaran, mengoptimalkan penawaran produk, meningkatkan kepuasan pelanggan, dan pada akhirnya meningkatkan pendapatan dan profitabilitas.
    
    Langkah selanjutnya adalah mengimplementasikan strategi yang direkomendasikan, memantau hasilnya, dan melakukan penyesuaian berdasarkan umpan balik dan perubahan tren pasar. Analisis data secara berkelanjutan akan membantu perusahaan tetap kompetitif dan responsif terhadap kebutuhan pelanggan yang terus berkembang.
    """)

# Footer
st.sidebar.markdown("---")
st.sidebar.info("Dashboard ini dibuat sebagai bagian dari Proyek Analisis Data E-Commerce.")

if __name__ == "__main__":
    pass
