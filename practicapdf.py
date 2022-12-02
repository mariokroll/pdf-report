import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from fpdf import FPDF


WIDTH = 210
HEIGHT = 297


def get_weekly_profit(df: pd.DataFrame, prediction: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the weekly profit
    """
    profits = [df.groupby('week')['price'].sum().values[i] for i in range(0, 53)]
    return profits


def extract() -> pd.DataFrame:
    """
    Extract the data from the csv file
    """
    prediction = pd.read_csv('2017_prediction.csv')
    prediction.set_index('Unnamed: 0', inplace=True)
    pizzas2 = pd.read_csv('df_merged.csv')
    pizzas = pd.read_csv('pizzas.csv')
    return prediction, pizzas2, pizzas


def transform(pizzas2: pd.DataFrame, pizzas: pd.DataFrame) -> pd.DataFrame:
    """
    Transform the csv, including new columns that will be useful for the analysis and plots
    """
    df = pd.merge(pizzas2, pizzas.loc[:, ['pizza_id', 'price']], on='pizza_id')
    df['price'] = df['price'] * df['quantity']
    df['date'] = pd.to_datetime(df['date'])
    df["pizza_name"] = df['pizza_id'].str.replace(r'_[a-z]+$', '', regex=True)
    sold_pizzas = df['pizza_name'].value_counts()
    sizes = df['pizza_id'].str.replace(r'[a-z]+_', '', regex=True)
    return df, sold_pizzas, sizes


def load(pdf: FPDF):
    pdf.output("practica.pdf")


def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=20, style='B')
    pdf.cell(200, 10, txt="PIZZAS MAVEN", ln=1, align="C")
    pdf.image("means.png", w=190, h=HEIGHT/3-10)
    pdf.image("subplot.png", w=WIDTH-20, h=HEIGHT/3-10)
    pdf.image("profit.png", w=WIDTH-20, h=HEIGHT/4)
    return pdf


def plot_graphics(df: pd.DataFrame, profits: list, sold_pizzas: pd.Series, sizes: pd.Series):
    """
    Plot the necessary graphics that we are going to use in the pdf
    """

    # Barplot of the weekly units of each ingredient used
    means = [df[col].mean() for col in df.columns]
    fig = plt.figure(figsize=(12, 5))
    plt.title('Weekly mean of each ingredient')
    sns.barplot(x=df.columns, y=means)
    plt.xticks(rotation=90, fontsize=7)
    plt.savefig('means.png', bbox_inches='tight')
    plt.clf()

    # Plot of the weekly profit
    fig = plt.figure(figsize=(12, 5))
    plt.plot(profits, color='black')
    plt.title('Annual profit per week')
    plt.xlabel('Week number')
    plt.ylabel('Profit ($)')
    plt.grid(True, color='grey', linewidth=0.5)
    plt.savefig('profit.png', bbox_inches='tight')
    plt.clf()

    ## Subplot of the yearly units of each pizza sold and the percentage of each size
    # Pie chart of the sizes
    fig = plt.figure(figsize=(8, 4))
    ax2 = plt.subplot2grid((1, 3), (0, 0))
    pie = plt.pie(sizes.value_counts(), explode=(0, 0, 0, 0, 0.2), autopct='%1.1f%%', startangle=90)
    ax2.legend(pie[0], sizes.value_counts().index, loc='upper right', bbox_to_anchor=(1.25, 1))
    ax2.set_title('Percentage of each size')

    # Barplot of the sold pizzas
    ax1 = plt.subplot2grid((1, 3), (0, 1), colspan=2)
    plt.title('Sold pizzas')
    sns.barplot(x=sold_pizzas.iloc[:10].index, y=sold_pizzas.iloc[:10].values)
    plt.xticks(rotation=90, fontsize=7)
    ax1.set_title('Top 10 most sold pizzas')
    plt.tight_layout()
    plt.savefig('subplot.png')
    plt.clf()



if __name__ == '__main__':
    prediction, pizzas2, pizzas = extract()
    df_complete, sold_pizzas, sizes = transform(pizzas2, pizzas)
    profit = get_weekly_profit(df_complete, prediction)
    plot_graphics(prediction, profit, sold_pizzas, sizes)
    pdf = create_pdf()
    load(pdf)