import seaborn as sns
import matplotlib.pyplot as plt

def create_bar_plot(df):

    if df.shape[1] < 2:
        return None

    x = df.columns[0]
    y = df.columns[1]

    fig, ax = plt.subplots()

    sns.barplot(data=df, x=x, y=y, ax=ax)

    plt.xticks(rotation=45)

    return fig