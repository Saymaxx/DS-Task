# 🚀 Import Libraries
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.stats import ttest_ind

# 📥 Load Datasets
sentiment = pd.read_csv(r"C:\Users\prosa\Downloads\fear_greed_index.csv")
trades = pd.read_csv(r"C:\Users\prosa\Downloads\historical_data.csv")

# 🕒 Convert Timestamps
# For sentiment data
sentiment['date'] = pd.to_datetime(sentiment['date'])

# For trade data
trades['timestamp_dt'] = pd.to_datetime(trades['Timestamp'], unit='ms')
trades['date'] = trades['timestamp_dt'].dt.normalize()

# 🔍 Data Preprocessing
trades['Side'] = trades['Side'].str.lower()  # Normalize trade side text

# 📊 Exploratory Data Analysis (EDA)

# 1️⃣ Distribution of Closed PnL
plt.figure(figsize=(10, 5))
sns.histplot(trades['Closed PnL'], bins=100, kde=True)
plt.title("Distribution of Closed PnL")
plt.xlabel("Closed PnL")
plt.ylabel("Frequency")
plt.show()

# 2️⃣ Boxplot: Closed PnL by Side
plt.figure(figsize=(8, 5))
sns.boxplot(x='Side', y='Closed PnL', data=trades)
plt.title("Closed PnL by Trade Side")
plt.show()

# 3️⃣ Scatter: Size vs Closed PnL
plt.figure(figsize=(8, 5))
sns.scatterplot(x='Size USD', y='Closed PnL', hue='Side', data=trades, alpha=0.5)
plt.title("Size vs Closed PnL")
plt.show()

# 4️⃣ Time Series: Daily PnL
daily_pnl = trades.groupby('date')['Closed PnL'].sum().reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(data=daily_pnl, x='date', y='Closed PnL')
plt.title("Daily Total Closed PnL Over Time")
plt.xticks(rotation=45)
plt.show()

# 5️⃣ Bar Chart: Top 10 Accounts by PnL
top_accounts = trades.groupby('Account')['Closed PnL'].sum().sort_values(ascending=False).head(10)

plt.figure(figsize=(10, 5))
sns.barplot(x=top_accounts.index, y=top_accounts.values)
plt.xticks(rotation=90)
plt.title("Top 10 Accounts by Total PnL")
plt.ylabel("Total Closed PnL")
plt.show()

# 6️⃣ Sentiment Analysis

# 6.1 Fear/Greed Index Over Time
plt.figure(figsize=(12, 6))
sns.lineplot(data=sentiment, x='date', y='value')
plt.title("Fear/Greed Index Over Time")
plt.xticks(rotation=45)
plt.ylabel("Sentiment Value")
plt.show()

# 6.2 Sentiment Classification Counts
plt.figure(figsize=(6, 4))
sns.countplot(data=sentiment, x='classification', order=sentiment['classification'].value_counts().index)
plt.title("Sentiment Classification Counts")
plt.show()

# 6.3 Monthly Sentiment Averages
sentiment['year_month'] = sentiment['date'].dt.to_period('M')
monthly_sentiment = sentiment.groupby('year_month')['value'].mean().reset_index()
monthly_sentiment['year_month_str'] = monthly_sentiment['year_month'].astype(str)

plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_sentiment, x='year_month_str', y='value')
plt.title("Monthly Average Fear/Greed Index")
plt.xticks(rotation=45)
plt.xlabel("Year-Month")
plt.ylabel("Average Fear/Greed Index")
plt.show()

# 🧪 Hypothesis Testing: Buy vs Sell PnL
buy_pnl = trades[trades['Side'] == 'buy']['Closed PnL']
sell_pnl = trades[trades['Side'] == 'sell']['Closed PnL']

print("Buy Side Count:", len(buy_pnl))
print("Sell Side Count:", len(sell_pnl))

t_stat, p_val = ttest_ind(buy_pnl, sell_pnl, equal_var=False)
print(f"T-statistic: {t_stat}")
print(f"P-value: {p_val}")

# 📈 Trader Clustering

# 1️⃣ Feature Engineering for Clustering
trader_features = trades.groupby('Account').agg({
    'Closed PnL': 'sum',
    'Size USD': 'mean',
    'Execution Price': 'mean'
}).reset_index()

trader_features.rename(columns={
    'Closed PnL': 'Total PnL',
    'Size USD': 'Avg Trade Size (USD)',
    'Execution Price': 'Avg Execution Price'
}, inplace=True)

print(trader_features.head())

# 2️⃣ K-Means Clustering
scaler = StandardScaler()
scaled_features = scaler.fit_transform(trader_features[['Total PnL', 'Avg Trade Size (USD)', 'Avg Execution Price']])

kmeans = KMeans(n_clusters=3, random_state=42)
trader_features['Cluster'] = kmeans.fit_predict(scaled_features)

print(trader_features['Cluster'].value_counts())

# 3️⃣ Cluster Visualization
plt.figure(figsize=(10, 6))
sns.scatterplot(data=trader_features, x='Avg Trade Size (USD)', y='Total PnL', hue='Cluster', palette='Set2')
plt.title("Trader Clusters Based on PnL and Trade Size")
plt.show()

# 4️⃣ Cluster Analysis
cluster_analysis = trader_features.groupby('Cluster').agg({
    'Total PnL': ['mean', 'std'],
    'Avg Trade Size (USD)': ['mean', 'std'],
    'Avg Execution Price': ['mean', 'std']
}).reset_index()
cluster_analysis.columns = ['Cluster', 'Mean Total PnL', 'Std Total PnL', 
                             'Mean Avg Trade Size (USD)', 'Std Avg Trade Size (USD)', 
                             'Mean Avg Execution Price', 'Std Avg Execution Price']
print(cluster_analysis)
