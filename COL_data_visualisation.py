import psycopg2
import pandas as pd
from matplotlib import pyplot as plt

households = pd.read_csv("C://Datenbanken/transformed_data/Households.csv")
households_names = list(households["Name"])

# creation of csv files for each household
for name in households_names:
    
    # connetion to database in postgresSQL 16
    conn = psycopg2.connect(database = "CostofLiving", 
                            user = "postgres", 
                            host= 'localhost',
                            # password goes here
                            password = "xxx",
                            port = 5432)
    
    cur = conn.cursor()
    # Execute a command: create datacamp_courses table
    cur.execute(f"""WITH TotalSalaries AS (
    SELECT
        h.HouseholdID,
        h.Name AS HouseholdName,
        c.CityID,
        c.Name AS CityName,
        co.CountryID,
        co.Name AS CountryName,
        SUM (s.Salary * h.NumberSalaries) AS TotalSalaries
    FROM
        Households h
        JOIN HouseholdsCities hc ON h.HouseholdID = hc.HouseholdID
        JOIN Cities c ON hc.CityID = c.CityID
        JOIN Countries co ON c.CountryID = co.CountryID
        JOIN Salaries s ON c.CityID = s.CityID
    GROUP BY
        h.HouseholdID,
        h.Name,
        c.CityID,
        c.Name,
        co.CountryID,
        co.Name
    ),
    TotalVariableCosts AS (
    SELECT
        h.HouseholdID,
        c.CityID,
        SUM (vc.Amount * p.Price) AS TotalVariableCosts
    FROM
        Households h
        JOIN VariableCosts vc ON h.HouseholdID = vc.HouseholdID
        JOIN Prices p ON vc.ItemID = p.ItemID
        JOIN Cities c ON p.CityID = c.CityID
    GROUP BY
        h.HouseholdID,
        c.CityID
    ),
    TotalFixedCosts AS (
    SELECT
        h.HouseholdID,
        c.CityID,
        SUM (p.Price) AS TotalFixedCosts
    FROM
        Households h
        JOIN FixedCosts fc ON h.HouseholdID = fc.HouseholdID
        JOIN Prices p ON fc.ItemID = p.ItemID
        JOIN Cities c ON p.CityID = c.CityID
    GROUP BY
        h.HouseholdID,
        c.CityID
    )
    SELECT
    ts.HouseholdName,
    ts.CityName,
    ts.CountryName,
    ts.TotalSalaries,
    tvc.TotalVariableCosts,
    tfc.TotalFixedCosts,
    ts.TotalSalaries - tvc.TotalVariableCosts - tfc.TotalFixedCosts AS Profit
    FROM
    TotalSalaries ts
    JOIN TotalVariableCosts tvc ON ts.HouseholdID = tvc.HouseholdID AND ts.CityID = tvc.CityID
    JOIN TotalFixedCosts tfc ON ts.HouseholdID = tfc.HouseholdID AND ts.CityID = tfc.CityID
    WHERE
    ts.HouseholdName = '{name}'
    ORDER BY
    Profit DESC""")

    # Close cursor and communication with the database
    rows = cur.fetchall()

    # Get the column names
    column_names = [desc[0] for desc in cur.description]

    # Create a pandas DataFrame
    df = pd.DataFrame(rows, columns=column_names)
    df.to_csv(f"C://Datenbanken/transformed_data/{name}COL.csv", index = False)


    conn.commit()
    cur.close()
    conn.close()
    

# enter the file paths here
df_baseline = pd.read_csv(r"C://Datenbanken/transformed_data/BaselineCOL.csv")
df_single = pd.read_csv(r"C://Datenbanken/transformed_data/SingleCOL.csv")
df_couple = pd.read_csv(r"C://Datenbanken/transformed_data/Partner_DualSalaryCOL.csv")
df_couple_with_child = pd.read_csv(r"C://Datenbanken/transformed_data/Partner_withChildCOL.csv")

# creating a lsit of all dataframes
list_of_dfs = [df_baseline, df_single, df_couple, df_couple_with_child]

# iteration over the list of dfa to drop all rows with NaN values and adding
# a column with the relative profit
for df in list_of_dfs:
    df.dropna(axis=0, how='any', inplace=True)
    df["relative_profit"] = df["profit"]/df["totalsalaries"]
    df["normalized_salary"] = df["totalsalaries"]/df["totalsalaries"].max()
    
    # plotting the data

fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Top 10 cities with the highes household income after costs ", fontsize=16)

# Plot top and lowest 10 values
bar_width = 0.35
index = range(10)

# creating a list with all subplot titles
title_list = ["Baseline", "Single", "Couple", "Couple with Child"]
for i, df in enumerate(list_of_dfs):
    top_values = df["relative_profit"].nlargest(10).values
    top_values_index = df["relative_profit"].nlargest(10).index
    axs[i//2, i%2].bar(index, top_values, bar_width, color = "blue", label='Relative income after costs')
    axs[i//2, i%2].set_xticklabels(df.loc[top_values_index, "cityname"], rotation=45, ha="right")
    axs[i//2, i%2].set_xticks(index)
    axs[i//2, i%2].set_title(title_list[i])
    axs[i//2, i%2].plot(df.loc[top_values_index, "cityname"], df.loc[top_values_index,"normalized_salary"],
                        color='red', marker='o', linestyle='-', linewidth=2, label='Normalized average salary')
    axs[i//2, i%2].set_ylabel("relative income after costs")
    axs[i//2, i%2].set_xlabel("city")
    axs[0,1].set_ylim(0, 0.7)
    axs[1,0].set_ylim(0, 0.7)
    axs[1,1].set_ylim(0, 0.7)

    lines, labels = axs[0,0].get_legend_handles_labels()
    fig.legend(lines, labels, loc='upper right')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()