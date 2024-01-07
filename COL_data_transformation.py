######################################################################
### In the following we splited the main csv file "cost-of-living_v2.csv" into 7 usable csv files for our database (Countries, Cities, Categories, Items, Price, Salaries).
### We also created 3 csv files on invented data to represent hypothetical needs for certain household types (Households, VariableCosts, FixedCosts).
### For comparision of the differnet cities we also created a intermediate table csv file in which we merged all unquie cityids with all available householdids (HouseholdsCities).
### When you run the code make sure the original csv file is placed in the right filepath "C://Datenbanken/" and is named correctly "cost-of-living_v2.csv".
### The code outputs all new csv files into a new folder "transformed_data" (10 in total) which then can be used for data ingestion in sql.
### If you want to include a new household, just adjust the code in line 244 (Name, Number of Persons, Number of Salaries), 851-997 (Selection and Amount of Items), 1137-1166 (Selection of Items). 
######################################################################

import pandas as pd
import numpy as np

# path to csv data
file_path = "C://Datenbanken/"
file_name = "cost-of-living_v2.csv"

# read cvs data to pandas dataframe
data = pd.read_csv(file_path + file_name)

# select only data with a valid quality level (923 datasets)
quality_data = data.loc[data["data_quality"] == 1]

# in later analysis we discovered that one datarow (Coquitlam, Canada) was missing the salary, so we excluded it
quality_data = quality_data[quality_data.city != "Coquitlam"]


######################################################################
### Transformation for Countires
######################################################################

# select the country column
countries = quality_data["country"]

# delete duplicates
unique_countries = countries.drop_duplicates()

# create countryid column and match the length of the unique countries
countryid = list(range(1, len(unique_countries) + 1))

# create new pandas df with countryid as with column and unique countires as second
countriesandids = pd.DataFrame({'countryID': countryid, 'unique_countries': unique_countries.values})

# rename "country" to "name" and export as csv
countries_csv = countriesandids.rename(columns={'unique_countries': 'name'})
countries_csv.to_csv(file_path + "transformed_data/" +  "Countries.csv", index = False)


######################################################################
### Transformation for Cities
######################################################################

# select the country and city column
citywithcountry = quality_data[["city" , "country"]]

# delete duplicate cities
unique_citywithcountry = citywithcountry.drop_duplicates(subset = "city")

# Merge of dataframes based on 'country'
citycountry = pd.merge(unique_citywithcountry, countriesandids, left_on='country', right_on='unique_countries', how='left')

# selection of the columns 'city' and 'countryID'
citiesandcountryids = citycountry[['city', 'countryID']]

# create cityid column and match the length of the unique citys
cityid = list(range(1, len (citiesandcountryids["city"]) + 1))
#print(f"cityidlänge{len(cityid)}")

# create dtaframe with city and the corresponding cityid
citiesandid = pd.DataFrame({'cityID': cityid, 'city': citiesandcountryids["city"].values})

# again merge the df's "citiesandcountryids" and "citiesandid"
citiesandallids = pd.merge(citiesandcountryids, citiesandid, on='city', how='left')

# only select the 3 columns cityID, city and country id
Cities_csv = citiesandallids[['cityID', 'city', 'countryID']]

# rename "city" to "name" and export as csv
Cities_csv.rename(columns={'city': 'name'}).to_csv(file_path + "transformed_data/" +  "Cities.csv", index = False)


######################################################################
### Transformation for Items & Categories
######################################################################

data_without_salary = quality_data.drop(["x54"], axis = 1)
id_vars = ['city', 'country']
value_vars = [col for col in data_without_salary.columns if col not in id_vars + ['data_quality']]

# transformation of dataframe to recive city, country, amount and description
transformed_item_data = pd.melt(data_without_salary, id_vars=id_vars, value_vars=value_vars, var_name='Item', value_name='amount')

# merge transformed_item_data and citiesandid to recive the city id
itemswithcityid = pd.merge(transformed_item_data, citiesandid, on='city', how='left')

# only select 'description', 'amount' and 'cityID'
Items_withoutid = itemswithcityid[['Item', 'amount', 'cityID']]

# dictionary with the corresponding categories for the items
item_categories = {"x1":"Restaurant", "x2":"Restaurant", "x3":"Restaurant", "x4":"Restaurant", "x5":"Restaurant", "x6":"Restaurant", "x7":"Restaurant", "x8":"Restaurant",
                   "x9":"Supermarket", "x10":"Supermarket", "x11":"Supermarket", "x12":"Supermarket", "x13":"Supermarket", "x14":"Supermarket", "x15":"Supermarket", "x16":"Supermarket", "x17":"Supermarket",
                   "x18":"Supermarket","x19":"Supermarket", "x20":"Supermarket", "x21":"Supermarket", "x22":"Supermarket", "x23":"Supermarket", "x24":"Supermarket","x25":"Supermarket", "x26":"Supermarket", "x27":"Supermarket", 
                   "x28":"Transport", "x29":"Transport", "x30":"Transport", "x31":"Transport", "x32":"Transport", "x33":"Transport", "x34":"Transport", "x35":"Transport",
                   "x36":"Utilities", "x37":"Utilities", "x38":"Utilities", "x39":"Leisure", "x40":"Leisure", "x41":"Leisure", "x42":"Education", "x43":"Education",
                   "x44":"Clothing", "x45":"Clothing", "x46":"Clothing", "x47":"Clothing", "x48":"Rent", "x49":"Rent", "x50":"Rent", "x51":"Rent", "x52":"House_Price", "x53":"House_Price", "x55":"Morgage_Rate"}

# inject dictionary into category column with keys as reference and values as values for the column
Items_withoutid["Category"] = Items_withoutid["Item"].map(item_categories)

# creating categoryid's for the categorys
categories = Items_withoutid["Category"].drop_duplicates()

# create countryid column and match the length of the unique countries
categoryid = list(range(1, len(categories) + 1))

# create new pandas df with CategoryID as column and name as second column
Category_csv = pd.DataFrame({'CategoryID': categoryid, 'Category': categories.values})

# export as csv
Category_csv.rename(columns={'Category': 'name'}).to_csv(file_path + "transformed_data/" + "Categories.csv", index = False)

# merge Items_withoutid and Category_csv on "Category"
Items_withcatid = pd.merge(Items_withoutid, Category_csv, on='Category', how='left')

# creating list of unique items and matching the length
items = Items_withcatid["Item"].drop_duplicates()
itemid = list(range(1, len (items) + 1))

# Creating new dataframe with itemid and item
# !Important because salary was removed from the items before, morgage_rate has the id 54 instead of 55
itemwithid = pd.DataFrame({'ItemID': itemid, 'Item': items.values})

# merge dataframe two times to get ItemID and CategoryID
itemwihtidandmore = pd.merge(itemwithid, Items_withoutid, on='Item', how='left')
itemswithshortdec = pd.merge(itemwihtidandmore, Category_csv, on='Category', how='left')

# reducing dataframe to "ItemID", 'Item', "CategoryID"
itemsbeforerenaming = itemswithshortdec[["ItemID", 'Item', "CategoryID"]]

# dictionary for renaming the items
item_rename = {"x1":"Meal Inexpensive Restaurant (USD)",
               "x2":"Meal for 2 People Mid-range Restaurant Three-course (USD)",
               "x3":"McMeal at McDonalds (or Equivalent Combo Meal) (USD)",
               "x4":"Domestic Beer (0.5 liter draught in restaurants) (USD)",
               "x5":"Imported Beer (0.33 liter bottle in restaurants) (USD)",
               "x6":"Cappuccino (regular in restaurants) (USD)",
               "x7":"Coke/Pepsi (0.33 liter bottle in restaurants) (USD)",
               "x8":"Water (0.33 liter bottle in restaurants) (USD)",
               "x9":"Milk (regular) (1 liter) (USD)",
               "x10":"Loaf of Fresh White Bread (500g) (USD)",
               "x11":"Rice (white) (1kg) (USD)",
               "x12":"Eggs (regular) (12) (USD)",
               "x13":"Local Cheese (1kg) (USD)",
               "x14":"Chicken Fillets (1kg) (USD)",
               "x15":"Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)",
               "x16":"Apples (1kg) (USD)",
               "x17":"Banana (1kg) (USD)",
               "x18":"Oranges (1kg) (USD)",
               "x19":"Tomato (1kg) (USD)",
               "x20":"Potato (1kg) (USD)",
               "x21":"Onion (1kg) (USD)",
               "x22":"Lettuce (1 head) (USD)",
               "x23":"Water (1.5 liter bottle at the market) (USD)",
               "x24":"Bottle of Wine (Mid-Range at the market) (USD)",
               "x25":"Domestic Beer (0.5 liter bottle at the market) (USD)",
               "x26":"Imported Beer (0.33 liter bottle at the market) (USD)",
               "x27":"Cigarettes 20 Pack (Marlboro) (USD)",
               "x28":"One-way Ticket (Local Transport) (USD)",
               "x29":"Monthly Pass (Regular Price) (USD)",
               "x30":"Taxi Start (Normal Tariff) (USD)",
               "x31":"Taxi 1km (Normal Tariff) (USD)",
               "x32":"Taxi 1hour Waiting (Normal Tariff) (USD)",
               "x33":"Gasoline (1 liter) (USD)",
               "x34":"Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)",
               "x35":"Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)",
               "x36":"Basic (Electricity Heating Cooling Water Garbage) for 85m2 Apartment (USD)",
               "x37":"1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)",
               "x38":"Internet (60 Mbps or More Unlimited Data Cable/ADSL) (USD)",
               "x39":"Fitness Club Monthly Fee for 1 Adult (USD)",
               "x40":"Tennis Court Rent (1 Hour on Weekend) (USD)",
               "x41":"Cinema International Release 1 Seat (USD)",
               "x42":"Preschool (or Kindergarten) Full Day Private Monthly for 1 Child (USD)",
               "x43":"International Primary School Yearly for 1 Child (USD)",
               "x44":"1 Pair of Jeans (Levis 501 Or Similar) (USD)",
               "x45":"1 Summer Dress in a Chain Store (Zara or H&M …) (USD)",
               "x46":"1 Pair of Nike Running Shoes (Mid-Range) (USD)",
               "x47":"1 Pair of Men Leather Business Shoes (USD)",
               "x48":"Apartment (1 bedroom) in City Centre (USD)",
               "x49":"Apartment (1 bedroom) Outside of Centre (USD)",
               "x50":"Apartment (3 bedrooms) in City Centre (USD)",
               "x51":"Apartment (3 bedrooms) Outside of Centre (USD)",
               "x52":"Price per Square Meter to Buy Apartment in City Centre (USD)",
               "x53":"Price per Square Meter to Buy Apartment Outside of Centre (USD)",
               "x54":"Average Monthly Net Salary (After Tax) (USD)",
               "x55":"Mortgage Interest Rate in Percentages (%) Yearly for 20 Years Fixed-Rate",
               }

# replace old item names with the ones of the dict
Items_csv = itemsbeforerenaming.replace({"Item": item_rename})
Items_csv = Items_csv.drop_duplicates(subset = "ItemID")

#rename columns and export to csv
Items_csv.rename(columns={'Item': 'Name'}).to_csv(file_path + "transformed_data/" + "Items.csv", index = False)

######################################################################
### Transformation for Price
######################################################################

Prices_csv = itemswithshortdec[["ItemID", 'amount', "cityID"]]

priceid = list(range(1, len(Prices_csv) + 1))

Prices_csv["SalaryID"] = priceid
Prices_csv = Prices_csv.reindex(columns=['SalaryID', 'ItemID', 'cityID', 'amount'])
Prices_csv.rename(columns={'amount': 'Price','cityID': 'CityID' }).to_csv(file_path + "transformed_data/" + "Prices.csv", index = False)


######################################################################
### Transformation for Salaries
######################################################################

# only selecting city and salary column
cityandsalary = quality_data[["city" , "x54"]]

# creating list based on salary length
salaryid = list(range(1, len (cityandsalary["x54"]) + 1))

# adding SalaryID to cityandsalary based on list salaryid
cityandsalary["SalaryID"] = salaryid

salarywithcityid = pd.merge(cityandsalary, citiesandid, on='city', how='left')

Salary_csv = salarywithcityid[["SalaryID", "x54", 'cityID']]

Salary_csv.rename(columns={"x54": "Salary"}).to_csv(file_path + "transformed_data/" + "Salaries.csv", index = False)


######################################################################
### Creation of Households
######################################################################
invented_data_households = [{"HouseholdID" : 1, "Name" : "Baseline", "NumberSalaries" : 1, "NumberInhabitants" : 1},
                    {"HouseholdID" : 2, "Name" : "Single", "NumberSalaries" : 1, "NumberInhabitants" : 1},
                    {"HouseholdID" : 3, "Name" : "Partner_DualSalary", "NumberSalaries" : 2, "NumberInhabitants" : 2},
                    {"HouseholdID" : 4, "Name" : "Partner_withChild", "NumberSalaries" : 2, "NumberInhabitants" : 3}]
#                    {"HouseholdID" : 5, "Name" : "xxx", "NumberSalaries" : 1, "NumberInhabitants" : 1}]

Households_without_cityid = pd.DataFrame(invented_data_households, columns=["HouseholdID", "Name", "NumberSalaries", "NumberInhabitants"])

Households_without_cityid.to_csv(file_path + "transformed_data/" + "Households.csv", index = False)

######################################################################
### Creation of VariableCosts
######################################################################
invented_data_variablecosts = [
    
                 ############################################################################
                 ######################### BASELINE HOUSEHOLD (ID:1)#########################
                 ############################################################################
                 
                 ############################## RESTAURANT/BAR ##############################
                 # ID:1 Meal, Inexpensive Restaurant (USD)
                 {"VaribaleCostID" : 1,"HouseholdID" : 1, "ItemID" : 1, "Amount" : 1 },
                 
                 # ID:2 Meal for 2 People, Mid-range Restaurant, Three-course (USD)
                 {"VaribaleCostID" : 2,"HouseholdID" : 1, "ItemID" : 2, "Amount" : 1 },
                 
                 # ID:3 McMeal at McDonalds (or Equivalent Combo Meal) (USD)
                 {"VaribaleCostID" : 3,"HouseholdID" : 1, "ItemID" : 3, "Amount" : 1 },
                 
                 # ID:4 Domestic Beer (0.5 liter draught, in restaurants) (USD)
                 {"VaribaleCostID" : 4,"HouseholdID" : 1, "ItemID" : 4, "Amount" : 1 },
                 
                 # ID:5 Imported Beer (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 5,"HouseholdID" : 1, "ItemID" : 5, "Amount" : 1 },
                 
                 # ID:6 Cappuccino (regular, in restaurants) (USD)
                 {"VaribaleCostID" : 6,"HouseholdID" : 1, "ItemID" : 6, "Amount" : 1 },
                 
                 # ID:7 Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 7,"HouseholdID" : 1, "ItemID" : 7, "Amount" : 1 },
                 
                 # ID:8 Water (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 8,"HouseholdID" : 1, "ItemID" : 8, "Amount" : 1 },
                 
                 ############################## SUPERMARKET ##############################
                 # ID:9 Milk (regular), (1 liter) (USD)
                 {"VaribaleCostID" : 9,"HouseholdID" : 1, "ItemID" : 9, "Amount" : 1 },
                 
                 # ID:10 Loaf of Fresh White Bread (500g) (USD)
                 {"VaribaleCostID" : 10,"HouseholdID" : 1, "ItemID" : 10, "Amount" : 1 },
                 
                 # ID:11 Rice (white), (1kg) (USD)
                 {"VaribaleCostID" : 11,"HouseholdID" : 1, "ItemID" : 11, "Amount" : 1 },
                 
                 # ID:12 Eggs (regular) (12) (USD)
                 {"VaribaleCostID" : 12,"HouseholdID" : 1, "ItemID" : 12, "Amount" : 1 },
                 
                 # ID:13 Local Cheese (1kg) (USD)
                 {"VaribaleCostID" : 13,"HouseholdID" : 1, "ItemID" : 13, "Amount" : 1 },
                 
                 # ID:14 Chicken Fillets (1kg) (USD)
                 {"VaribaleCostID" : 14,"HouseholdID" : 1, "ItemID" : 14, "Amount" : 1 },
                 
                 # ID:15 Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)
                 {"VaribaleCostID" : 15,"HouseholdID" : 1, "ItemID" : 15, "Amount" : 1 },
                 
                 # ID:16 Apples (1kg) (USD)
                 {"VaribaleCostID" : 16,"HouseholdID" : 1, "ItemID" : 16, "Amount" : 1 },
                 
                 # ID:17 Banana (1kg) (USD)
                 {"VaribaleCostID" : 17,"HouseholdID" : 1, "ItemID" : 17, "Amount" : 1 },
                 
                 # ID:18 Oranges (1kg) (USD)
                 {"VaribaleCostID" : 18,"HouseholdID" : 1, "ItemID" : 18, "Amount" : 1 },
                 
                 # ID:19 Tomato (1kg) (USD)
                 {"VaribaleCostID" : 19,"HouseholdID" : 1, "ItemID" : 19, "Amount" : 1 },
                 
                 # ID:20 Potato (1kg) (USD)
                 {"VaribaleCostID" : 20,"HouseholdID" : 1, "ItemID" : 20, "Amount" : 1 },
                 
                 # ID:21 Onion (1kg) (USD)
                 {"VaribaleCostID" : 21,"HouseholdID" : 1, "ItemID" : 21, "Amount" : 1 },
                 
                 # ID:22 Lettuce (1 head) (USD)
                 {"VaribaleCostID" : 22,"HouseholdID" : 1, "ItemID" : 22, "Amount" : 1 },
                 
                 # ID:23 Water (1.5 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 23,"HouseholdID" : 1, "ItemID" : 23, "Amount" : 1 },
                 
                 # ID:24 Bottle of Wine (Mid-Range, at the market) (USD)
                 {"VaribaleCostID" : 24,"HouseholdID" : 1, "ItemID" : 24, "Amount" : 1 },
                 
                 # ID:25 Domestic Beer (0.5 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 25,"HouseholdID" : 1, "ItemID" : 25, "Amount" : 1 },
                 
                 # ID:26 Imported Beer (0.33 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 26,"HouseholdID" : 1, "ItemID" : 26, "Amount" : 1 },
                 
                 # ID:27 Cigarettes 20 Pack (Marlboro) (USD)
                 {"VaribaleCostID" : 27,"HouseholdID" : 1, "ItemID" : 27, "Amount" : 1 },
                 
                 ############################## TRANSPORT ##############################
                 # ID:28 One-way Ticket (Local Transport) (USD)
                 {"VaribaleCostID" : 28,"HouseholdID" : 1, "ItemID" : 28, "Amount" : 1 },
                 
                 # ID:29 Monthly Pass (Regular Price) (USD)
                 {"VaribaleCostID" : 29,"HouseholdID" : 1, "ItemID" : 29, "Amount" : 1 },
                 
                 # ID:30 Taxi Start (Normal Tariff) (USD)
                 {"VaribaleCostID" : 30,"HouseholdID" : 1, "ItemID" : 30, "Amount" : 1 },
                 
                 # ID:31 Taxi 1km (Normal Tariff) (USD)
                 {"VaribaleCostID" : 31,"HouseholdID" : 1, "ItemID" : 31, "Amount" : 1 },
                 
                 # ID:32 Taxi 1hour Waiting (Normal Tariff) (USD)
                 {"VaribaleCostID" : 32,"HouseholdID" : 1, "ItemID" : 32, "Amount" : 1 },
                 
                 # ID:33 Gasoline (1 liter) (USD)
                 {"VaribaleCostID" : 33,"HouseholdID" : 1, "ItemID" : 33, "Amount" : 1 },
                 
                 # ID:34 Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)
                 #{"VaribaleCostID" : 34,"HouseholdID" : 1, "ItemID" : 34, "Amount" : 1 },
                 
                 # ID:35 Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)
                 #{"VaribaleCostID" : 35,"HouseholdID" : 1, "ItemID" : 35, "Amount" : 1 },
                 
                 # ID:37 1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)
                 {"VaribaleCostID" : 36,"HouseholdID" : 1, "ItemID" : 37, "Amount" : 1 },

                 ############################## LEISURE ##############################
                 # ID:39 Fitness Club, Monthly Fee for 1 Adult (USD)
                 {"VaribaleCostID" : 37,"HouseholdID" : 1, "ItemID" : 39, "Amount" : 1 },
                 
                 # ID:40 Tennis Court Rent (1 Hour on Weekend) (USD)
                 {"VaribaleCostID" : 38,"HouseholdID" : 1, "ItemID" : 40, "Amount" : 1 },
                 
                 # ID:41 Cinema, International Release, 1 Seat (USD)
                 {"VaribaleCostID" : 39,"HouseholdID" : 1, "ItemID" : 41, "Amount" : 1 },
                 
                 ############################## EDUCATION ##############################
                 # ID:42 Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)
                 {"VaribaleCostID" : 40,"HouseholdID" : 1, "ItemID" : 42, "Amount" : 1 },
                 
                 # ID:43 International Primary School, Yearly for 1 Child (USD)
                 {"VaribaleCostID" : 41,"HouseholdID" : 1, "ItemID" : 43, "Amount" : 1 },
                 
                 ############################## CLOTHING ##############################
                 # ID:44 1 Pair of Jeans (Levis 501 Or Similar) (USD)
                 {"VaribaleCostID" : 42,"HouseholdID" : 1, "ItemID" : 44, "Amount" : 1 },
                 
                 # ID:45 1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)
                 {"VaribaleCostID" : 43,"HouseholdID" : 1, "ItemID" : 45, "Amount" : 1 },
                 
                 # ID:46 1 Pair of Nike Running Shoes (Mid-Range) (USD)
                 {"VaribaleCostID" : 44,"HouseholdID" : 1, "ItemID" : 46, "Amount" : 1 },
                 
                 # ID:47 1 Pair of Men Leather Business Shoes (USD)
                 {"VaribaleCostID" : 45,"HouseholdID" : 1, "ItemID" : 47, "Amount" : 1 },
                 
                 # ID:54 Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate
                 #{"VaribaleCostID" : 46,"HouseholdID" : 1, "ItemID" : 54, "Amount" : 1 },

    
                 ############################################################################
                 ########################## SINGLE HOUSEHOLD (ID:2)##########################
                 ############################################################################
                 
                 ############################## RESTAURANT/BAR ##############################
                 # ID:1 Meal, Inexpensive Restaurant (USD)
                 {"VaribaleCostID" : 47,"HouseholdID" : 2, "ItemID" : 1, "Amount" : 6 },
                 
                 # ID:2 Meal for 2 People, Mid-range Restaurant, Three-course (USD)
                 {"VaribaleCostID" : 48,"HouseholdID" : 2, "ItemID" : 2, "Amount" : 2 },
                 
                 # ID:3 McMeal at McDonalds (or Equivalent Combo Meal) (USD)
                 {"VaribaleCostID" : 49,"HouseholdID" : 2, "ItemID" : 3, "Amount" : 2 },
                 
                 # ID:4 Domestic Beer (0.5 liter draught, in restaurants) (USD)
                 {"VaribaleCostID" : 50,"HouseholdID" : 2, "ItemID" : 4, "Amount" : 10 },
                 
                 # ID:5 Imported Beer (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 51,"HouseholdID" : 2, "ItemID" : 5, "Amount" : 2 },
                 
                 # ID:6 Cappuccino (regular, in restaurants) (USD)
                 {"VaribaleCostID" : 52,"HouseholdID" : 2, "ItemID" : 6, "Amount" : 5 },
                 
                 # ID:7 Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 53,"HouseholdID" : 2, "ItemID" : 7, "Amount" : 4 },
                 
                 # ID:8 Water (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 54,"HouseholdID" : 2, "ItemID" : 8, "Amount" : 4 },
                 
                 ############################## SUPERMARKET ##############################
                 # ID:9 Milk (regular), (1 liter) (USD)
                 {"VaribaleCostID" : 55,"HouseholdID" : 2, "ItemID" : 9, "Amount" : 8 },
                 
                 # ID:10 Loaf of Fresh White Bread (500g) (USD)
                 {"VaribaleCostID" : 56,"HouseholdID" : 2, "ItemID" : 10, "Amount" : 4 },
                 
                 # ID:11 Rice (white), (1kg) (USD)
                 {"VaribaleCostID" : 57,"HouseholdID" : 2, "ItemID" : 11, "Amount" : 2 },
                 
                 # ID:12 Eggs (regular) (12) (USD)
                 {"VaribaleCostID" : 58,"HouseholdID" : 2, "ItemID" : 12, "Amount" : 2 },
                 
                 # ID:13 Local Cheese (1kg) (USD)
                 {"VaribaleCostID" : 59,"HouseholdID" : 2, "ItemID" : 13, "Amount" : 1 },
                 
                 # ID:14 Chicken Fillets (1kg) (USD)
                 {"VaribaleCostID" : 60,"HouseholdID" : 2, "ItemID" : 14, "Amount" : 1 },
                 
                 # ID:15 Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)
                 {"VaribaleCostID" : 61,"HouseholdID" : 2, "ItemID" : 15, "Amount" : 1 },
                 
                 # ID:16 Apples (1kg) (USD)
                 {"VaribaleCostID" : 62,"HouseholdID" : 2, "ItemID" : 16, "Amount" : 1 },
                 
                 # ID:17 Banana (1kg) (USD)
                 {"VaribaleCostID" : 63,"HouseholdID" : 2, "ItemID" : 17, "Amount" : 1 },
                 
                 # ID:18 Oranges (1kg) (USD)
                 {"VaribaleCostID" : 64,"HouseholdID" : 2, "ItemID" : 18, "Amount" : 1 },
                 
                 # ID:19 Tomato (1kg) (USD)
                 {"VaribaleCostID" : 65,"HouseholdID" : 2, "ItemID" : 19, "Amount" : 1 },
                 
                 # ID:20 Potato (1kg) (USD)
                 {"VaribaleCostID" : 66,"HouseholdID" : 2, "ItemID" : 20, "Amount" : 1 },
                 
                 # ID:21 Onion (1kg) (USD)
                 {"VaribaleCostID" : 67,"HouseholdID" : 2, "ItemID" : 21, "Amount" : 1 },
                 
                 # ID:22 Lettuce (1 head) (USD)
                 {"VaribaleCostID" : 68,"HouseholdID" : 2, "ItemID" : 22, "Amount" : 1 },
                 
                 # ID:23 Water (1.5 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 69,"HouseholdID" : 2, "ItemID" : 23, "Amount" : 3 },
                 
                 # ID:24 Bottle of Wine (Mid-Range, at the market) (USD)
                 {"VaribaleCostID" : 70,"HouseholdID" : 2, "ItemID" : 24, "Amount" : 3 },
                 
                 # ID:25 Domestic Beer (0.5 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 71,"HouseholdID" : 2, "ItemID" : 25, "Amount" : 10 },
                 
                 # ID:26 Imported Beer (0.33 liter bottle, at the market) (USD)
                 # {"VaribaleCostID" : 72,"HouseholdID" : 2, "ItemID" : 26, "Amount" : 0 },
                 
                 # ID:27 Cigarettes 20 Pack (Marlboro) (USD)
                 # {"VaribaleCostID" : 73,"HouseholdID" : 2, "ItemID" : 27, "Amount" : 0 },
                 
                 ############################## TRANSPORT ##############################
                 # ID:28 One-way Ticket (Local Transport) (USD)
                 # {"VaribaleCostID" : 74,"HouseholdID" : 2, "ItemID" : 28, "Amount" : 0 },
                 
                 # ID:29 Monthly Pass (Regular Price) (USD)
                 {"VaribaleCostID" : 75,"HouseholdID" : 2, "ItemID" : 29, "Amount" : 1 },
                 
                 # ID:30 Taxi Start (Normal Tariff) (USD)
                 {"VaribaleCostID" : 76,"HouseholdID" : 2, "ItemID" : 30, "Amount" : 3 },
                 
                 # ID:31 Taxi 1km (Normal Tariff) (USD)
                 {"VaribaleCostID" : 77,"HouseholdID" : 2, "ItemID" : 31, "Amount" : 10 },
                 
                 # ID:32 Taxi 1hour Waiting (Normal Tariff) (USD)
                 {"VaribaleCostID" : 78,"HouseholdID" : 2, "ItemID" : 32, "Amount" : 1 },
                 
                 # ID:33 Gasoline (1 liter) (USD)
                 {"VaribaleCostID" : 79,"HouseholdID" : 2, "ItemID" : 33, "Amount" : 20 },
                 
                 # ID:34 Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)
                 # {"VaribaleCostID" : 80,"HouseholdID" : 2, "ItemID" : 34, "Amount" : 0 },
                 
                 # ID:35 Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)
                 # {"VaribaleCostID" : 81,"HouseholdID" : 2, "ItemID" : 35, "Amount" : 0 },
                 
                 # ID:37 1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)
                 {"VaribaleCostID" : 82,"HouseholdID" : 2, "ItemID" : 37, "Amount" : 60 },

                 ############################## LEISURE ##############################
                 # ID:39 Fitness Club, Monthly Fee for 1 Adult (USD)
                 {"VaribaleCostID" : 83,"HouseholdID" : 2, "ItemID" : 39, "Amount" : 1 },
                 
                 # ID:40 Tennis Court Rent (1 Hour on Weekend) (USD)
                 # {"VaribaleCostID" : 84,"HouseholdID" : 2, "ItemID" : 40, "Amount" : 0 },
                 
                 # ID:41 Cinema, International Release, 1 Seat (USD)
                 {"VaribaleCostID" : 85,"HouseholdID" : 2, "ItemID" : 41, "Amount" : 2 },
                 
                 ############################## EDUCATION ##############################
                 # ID:42 Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)
                 # {"VaribaleCostID" : 86,"HouseholdID" : 2, "ItemID" : 42, "Amount" : 1 },
                 
                 # ID:43 International Primary School, Yearly for 1 Child (USD)
                 # {"VaribaleCostID" : 87,"HouseholdID" : 2, "ItemID" : 43, "Amount" : 1 },
                 
                 ############################## CLOTHING ##############################
                 # ID:44 1 Pair of Jeans (Levis 501 Or Similar) (USD)
                 {"VaribaleCostID" : 88,"HouseholdID" : 2, "ItemID" : 44, "Amount" : 0.5 },
                 
                 # ID:45 1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)
                 {"VaribaleCostID" : 89,"HouseholdID" : 2, "ItemID" : 45, "Amount" : 1 },
                 
                 # ID:46 1 Pair of Nike Running Shoes (Mid-Range) (USD)
                 {"VaribaleCostID" : 90,"HouseholdID" : 2, "ItemID" : 46, "Amount" : 0.1 },
                 
                 # ID:47 1 Pair of Men Leather Business Shoes (USD)
                 {"VaribaleCostID" : 91,"HouseholdID" : 2, "ItemID" : 47, "Amount" : 0.05 },
                 
                 # ID:54 Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate
                 # {"VaribaleCostID" : 92,"HouseholdID" : 2, "ItemID" : 54, "Amount" : 1 }


                 ############################################################################
                 #################### PARTNER DUALSALARY HOUSEHOLD (ID:3)####################
                 ############################################################################
                 
                 ############################## RESTAURANT/BAR ##############################
                 # ID:1 Meal, Inexpensive Restaurant (USD)
                 {"VaribaleCostID" : 93,"HouseholdID" : 3, "ItemID" : 1, "Amount" : 2 },
                 
                 # ID:2 Meal for 2 People, Mid-range Restaurant, Three-course (USD)
                 {"VaribaleCostID" : 94,"HouseholdID" : 3, "ItemID" : 2, "Amount" : 8 },
                 
                 # ID:3 McMeal at McDonalds (or Equivalent Combo Meal) (USD)
                 {"VaribaleCostID" : 95,"HouseholdID" : 3, "ItemID" : 3, "Amount" : 2 },
                 
                 # ID:4 Domestic Beer (0.5 liter draught, in restaurants) (USD)
                 {"VaribaleCostID" : 96,"HouseholdID" : 3, "ItemID" : 4, "Amount" : 10 },
                 
                 # ID:5 Imported Beer (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 97,"HouseholdID" : 3, "ItemID" : 5, "Amount" : 2 },
                 
                 # ID:6 Cappuccino (regular, in restaurants) (USD)
                 {"VaribaleCostID" : 98,"HouseholdID" : 3, "ItemID" : 6, "Amount" : 10 },
                 
                 # ID:7 Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 99,"HouseholdID" : 3, "ItemID" : 7, "Amount" : 8 },
                 
                 # ID:8 Water (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 100,"HouseholdID" : 3, "ItemID" : 8, "Amount" : 8 },
                 
                 ############################## SUPERMARKET ##############################
                 # ID:9 Milk (regular), (1 liter) (USD)
                 {"VaribaleCostID" : 101,"HouseholdID" : 3, "ItemID" : 9, "Amount" : 12 },
                 
                 # ID:10 Loaf of Fresh White Bread (500g) (USD)
                 {"VaribaleCostID" : 102,"HouseholdID" : 3, "ItemID" : 10, "Amount" : 6 },
                 
                 # ID:11 Rice (white), (1kg) (USD)
                 {"VaribaleCostID" : 103,"HouseholdID" : 3, "ItemID" : 11, "Amount" : 3 },
                 
                 # ID:12 Eggs (regular) (12) (USD)
                 {"VaribaleCostID" : 104,"HouseholdID" : 3, "ItemID" : 12, "Amount" : 2 },
                 
                 # ID:13 Local Cheese (1kg) (USD)
                 {"VaribaleCostID" : 105,"HouseholdID" : 3, "ItemID" : 13, "Amount" : 1 },
                 
                 # ID:14 Chicken Fillets (1kg) (USD)
                 {"VaribaleCostID" : 106,"HouseholdID" : 3, "ItemID" : 14, "Amount" : 2 },
                 
                 # ID:15 Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)
                 {"VaribaleCostID" : 107,"HouseholdID" : 3, "ItemID" : 15, "Amount" : 2 },
                 
                 # ID:16 Apples (1kg) (USD)
                 {"VaribaleCostID" : 108,"HouseholdID" : 3, "ItemID" : 16, "Amount" : 1 },
                 
                 # ID:17 Banana (1kg) (USD)
                 {"VaribaleCostID" : 109,"HouseholdID" : 3, "ItemID" : 17, "Amount" : 1 },
                 
                 # ID:18 Oranges (1kg) (USD)
                 {"VaribaleCostID" : 110,"HouseholdID" : 3, "ItemID" : 18, "Amount" : 1 },
                 
                 # ID:19 Tomato (1kg) (USD)
                 {"VaribaleCostID" : 111,"HouseholdID" : 3, "ItemID" : 19, "Amount" : 1 },
                 
                 # ID:20 Potato (1kg) (USD)
                 {"VaribaleCostID" : 112,"HouseholdID" : 3, "ItemID" : 20, "Amount" : 2 },
                 
                 # ID:21 Onion (1kg) (USD)
                 {"VaribaleCostID" : 113,"HouseholdID" : 3, "ItemID" : 21, "Amount" : 1 },
                 
                 # ID:22 Lettuce (1 head) (USD)
                 {"VaribaleCostID" : 114,"HouseholdID" : 3, "ItemID" : 22, "Amount" : 1 },
                 
                 # ID:23 Water (1.5 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 115,"HouseholdID" : 3, "ItemID" : 23, "Amount" : 6 },
                 
                 # ID:24 Bottle of Wine (Mid-Range, at the market) (USD)
                 {"VaribaleCostID" : 116,"HouseholdID" : 3, "ItemID" : 24, "Amount" : 4 },
                 
                 # ID:25 Domestic Beer (0.5 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 117,"HouseholdID" : 3, "ItemID" : 25, "Amount" : 10 },
                 
                 # ID:26 Imported Beer (0.33 liter bottle, at the market) (USD)
                 #{"VaribaleCostID" : 118,"HouseholdID" : 3, "ItemID" : 26, "Amount" : 1 },
                 
                 # ID:27 Cigarettes 20 Pack (Marlboro) (USD)
                 #{"VaribaleCostID" : 119,"HouseholdID" : 3, "ItemID" : 27, "Amount" : 1 },
                 
                 ############################## TRANSPORT ##############################
                 # ID:28 One-way Ticket (Local Transport) (USD)
                 #{"VaribaleCostID" : 120,"HouseholdID" : 3, "ItemID" : 28, "Amount" : 1 },
                 
                 # ID:29 Monthly Pass (Regular Price) (USD)
                 {"VaribaleCostID" : 121,"HouseholdID" : 3, "ItemID" : 29, "Amount" : 2 },
                 
                 # ID:30 Taxi Start (Normal Tariff) (USD)
                 {"VaribaleCostID" : 122,"HouseholdID" : 3, "ItemID" : 30, "Amount" : 3 },
                 
                 # ID:31 Taxi 1km (Normal Tariff) (USD)
                 {"VaribaleCostID" : 123,"HouseholdID" : 3, "ItemID" : 31, "Amount" : 10 },
                 
                 # ID:32 Taxi 1hour Waiting (Normal Tariff) (USD)
                 {"VaribaleCostID" : 124,"HouseholdID" : 3, "ItemID" : 32, "Amount" : 1 },
                 
                 # ID:33 Gasoline (1 liter) (USD)
                 {"VaribaleCostID" : 125,"HouseholdID" : 3, "ItemID" : 33, "Amount" : 20 },
                 
                 # ID:34 Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)
                 #{"VaribaleCostID" : 126,"HouseholdID" : 3, "ItemID" : 34, "Amount" : 1 },
                 
                 # ID:35 Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)
                 #{"VaribaleCostID" : 127,"HouseholdID" : 3, "ItemID" : 35, "Amount" : 1 },
                 
                 # ID:37 1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)
                 {"VaribaleCostID" : 128,"HouseholdID" : 3, "ItemID" : 37, "Amount" : 120 },

                 ############################## LEISURE ##############################
                 # ID:39 Fitness Club, Monthly Fee for 1 Adult (USD)
                 {"VaribaleCostID" : 129,"HouseholdID" : 3, "ItemID" : 39, "Amount" : 2 },
                 
                 # ID:40 Tennis Court Rent (1 Hour on Weekend) (USD)
                 #{"VaribaleCostID" : 130,"HouseholdID" : 3, "ItemID" : 40, "Amount" : 1 },
                 
                 # ID:41 Cinema, International Release, 1 Seat (USD)
                 {"VaribaleCostID" : 131,"HouseholdID" : 3, "ItemID" : 41, "Amount" : 4 },
                 
                 ############################## EDUCATION ##############################
                 # ID:42 Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)
                 #{"VaribaleCostID" : 132,"HouseholdID" : 3, "ItemID" : 42, "Amount" : 1 },
                 
                 # ID:43 International Primary School, Yearly for 1 Child (USD)
                 #{"VaribaleCostID" : 133,"HouseholdID" : 3, "ItemID" : 43, "Amount" : 1 },
                 
                 ############################## CLOTHING ##############################
                 # ID:44 1 Pair of Jeans (Levis 501 Or Similar) (USD)
                 {"VaribaleCostID" : 134,"HouseholdID" : 3, "ItemID" : 44, "Amount" : 1 },
                 
                 # ID:45 1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)
                 {"VaribaleCostID" : 135,"HouseholdID" : 3, "ItemID" : 45, "Amount" : 2 },
                 
                 # ID:46 1 Pair of Nike Running Shoes (Mid-Range) (USD)
                 {"VaribaleCostID" : 136,"HouseholdID" : 3, "ItemID" : 46, "Amount" : 0.2 },
                 
                 # ID:47 1 Pair of Men Leather Business Shoes (USD)
                 {"VaribaleCostID" : 137,"HouseholdID" : 3, "ItemID" : 47, "Amount" : 0.1 },
                 
                 # ID:54 Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate
                 #{"VaribaleCostID" : 138,"HouseholdID" : 3, "ItemID" : 54, "Amount" : 1 },
                 
                 
                 ############################################################################
                 ######################### Partner_withChild (ID:4)##########################
                 ############################################################################
                 
                 ############################## RESTAURANT/BAR ##############################
                 # ID:1 Meal, Inexpensive Restaurant (USD)
                 {"VaribaleCostID" : 139,"HouseholdID" : 4, "ItemID" : 1, "Amount" : 2 },
                 
                 # ID:2 Meal for 2 People, Mid-range Restaurant, Three-course (USD)
                 {"VaribaleCostID" : 140,"HouseholdID" : 4, "ItemID" : 2, "Amount" : 6 },
                 
                 # ID:3 McMeal at McDonalds (or Equivalent Combo Meal) (USD)
                 {"VaribaleCostID" : 141,"HouseholdID" : 4, "ItemID" : 3, "Amount" : 9 },
                 
                 # ID:4 Domestic Beer (0.5 liter draught, in restaurants) (USD)
                 {"VaribaleCostID" : 142,"HouseholdID" : 4, "ItemID" : 4, "Amount" : 8 },
                 
                 # ID:5 Imported Beer (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 143,"HouseholdID" : 4, "ItemID" : 5, "Amount" : 2 },
                 
                 # ID:6 Cappuccino (regular, in restaurants) (USD)
                 {"VaribaleCostID" : 144,"HouseholdID" : 4, "ItemID" : 6, "Amount" : 10 },
                 
                 # ID:7 Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 145,"HouseholdID" : 4, "ItemID" : 7, "Amount" : 15 },
                 
                 # ID:8 Water (0.33 liter bottle, in restaurants) (USD)
                 {"VaribaleCostID" : 146,"HouseholdID" : 4, "ItemID" : 8, "Amount" : 9 },
                 
                 ############################## SUPERMARKET ##############################
                 # ID:9 Milk (regular), (1 liter) (USD)
                 {"VaribaleCostID" : 147,"HouseholdID" : 4, "ItemID" : 9, "Amount" : 16 },
                 
                 # ID:10 Loaf of Fresh White Bread (500g) (USD)
                 {"VaribaleCostID" : 148,"HouseholdID" : 4, "ItemID" : 10, "Amount" : 9 },
                 
                 # ID:11 Rice (white), (1kg) (USD)
                 {"VaribaleCostID" : 149,"HouseholdID" : 4, "ItemID" : 11, "Amount" : 4 },
                 
                 # ID:12 Eggs (regular) (12) (USD)
                 {"VaribaleCostID" : 150,"HouseholdID" : 4, "ItemID" : 12, "Amount" : 3 },
                 
                 # ID:13 Local Cheese (1kg) (USD)
                 {"VaribaleCostID" : 151,"HouseholdID" : 4, "ItemID" : 13, "Amount" : 1.5 },
                 
                 # ID:14 Chicken Fillets (1kg) (USD)
                 {"VaribaleCostID" : 152,"HouseholdID" : 4, "ItemID" : 14, "Amount" : 2.5 },
                 
                 # ID:15 Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)
                 {"VaribaleCostID" : 153,"HouseholdID" : 4, "ItemID" : 15, "Amount" : 2.5 },
                 
                 # ID:16 Apples (1kg) (USD)
                 {"VaribaleCostID" : 154,"HouseholdID" : 4, "ItemID" : 16, "Amount" : 1.5 },
                 
                 # ID:17 Banana (1kg) (USD)
                 {"VaribaleCostID" : 155,"HouseholdID" : 4, "ItemID" : 17, "Amount" : 1.5 },
                 
                 # ID:18 Oranges (1kg) (USD)
                 {"VaribaleCostID" : 156,"HouseholdID" : 4, "ItemID" : 18, "Amount" : 1.2 },
                 
                 # ID:19 Tomato (1kg) (USD)
                 {"VaribaleCostID" : 157,"HouseholdID" : 4, "ItemID" : 19, "Amount" : 1.2 },
                 
                 # ID:20 Potato (1kg) (USD)
                 {"VaribaleCostID" : 158,"HouseholdID" : 4, "ItemID" : 20, "Amount" : 2.5 },
                 
                 # ID:21 Onion (1kg) (USD)
                 {"VaribaleCostID" : 159,"HouseholdID" : 4, "ItemID" : 21, "Amount" : 1.5 },
                 
                 # ID:22 Lettuce (1 head) (USD)
                 {"VaribaleCostID" : 160,"HouseholdID" : 4, "ItemID" : 22, "Amount" : 1.2 },
                 
                 # ID:23 Water (1.5 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 161,"HouseholdID" : 4, "ItemID" : 23, "Amount" : 10 },
                 
                 # ID:24 Bottle of Wine (Mid-Range, at the market) (USD)
                 {"VaribaleCostID" : 162,"HouseholdID" : 4, "ItemID" : 24, "Amount" : 4 },
                 
                 # ID:25 Domestic Beer (0.5 liter bottle, at the market) (USD)
                 {"VaribaleCostID" : 163,"HouseholdID" : 4, "ItemID" : 25, "Amount" : 10 },
                 
                 # ID:26 Imported Beer (0.33 liter bottle, at the market) (USD)
                 #{"VaribaleCostID" : 164,"HouseholdID" : 4, "ItemID" : 26, "Amount" : 1 },
                 
                 # ID:27 Cigarettes 20 Pack (Marlboro) (USD)
                 #{"VaribaleCostID" : 165,"HouseholdID" : 4, "ItemID" : 27, "Amount" : 1 },
                 
                 ############################## TRANSPORT ##############################
                 # ID:28 One-way Ticket (Local Transport) (USD)
                 #{"VaribaleCostID" : 166,"HouseholdID" : 4, "ItemID" : 28, "Amount" : 1 },
                 
                 # ID:29 Monthly Pass (Regular Price) (USD)
                 {"VaribaleCostID" : 167,"HouseholdID" : 4, "ItemID" : 29, "Amount" : 2.5 },
                 
                 # ID:30 Taxi Start (Normal Tariff) (USD)
                 {"VaribaleCostID" : 168,"HouseholdID" : 4, "ItemID" : 30, "Amount" : 3 },
                 
                 # ID:31 Taxi 1km (Normal Tariff) (USD)
                 {"VaribaleCostID" : 169,"HouseholdID" : 4, "ItemID" : 31, "Amount" : 10 },
                 
                 # ID:32 Taxi 1hour Waiting (Normal Tariff) (USD)
                 {"VaribaleCostID" : 170,"HouseholdID" : 4, "ItemID" : 32, "Amount" : 1 },
                 
                 # ID:33 Gasoline (1 liter) (USD)
                 {"VaribaleCostID" : 171,"HouseholdID" : 4, "ItemID" : 33, "Amount" : 40 },
                 
                 # ID:34 Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)
                 #{"VaribaleCostID" : 172,"HouseholdID" : 4, "ItemID" : 34, "Amount" : 1 },
                 
                 # ID:35 Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)
                 #{"VaribaleCostID" : 173,"HouseholdID" : 4, "ItemID" : 35, "Amount" : 1 },
                 
                 # ID:37 1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)
                 {"VaribaleCostID" : 174,"HouseholdID" : 4, "ItemID" : 37, "Amount" : 150 },

                 ############################## LEISURE ##############################
                 # ID:39 Fitness Club, Monthly Fee for 1 Adult (USD)
                 #{"VaribaleCostID" : 175,"HouseholdID" : 4, "ItemID" : 39, "Amount" : 1 },
                 
                 # ID:40 Tennis Court Rent (1 Hour on Weekend) (USD)
                 #{"VaribaleCostID" : 176,"HouseholdID" : 4, "ItemID" : 40, "Amount" : 1 },
                 
                 # ID:41 Cinema, International Release, 1 Seat (USD)
                 {"VaribaleCostID" : 177,"HouseholdID" : 4, "ItemID" : 41, "Amount" : 5 },
                 
                 ############################## EDUCATION ##############################
                 # ID:42 Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)
                 #{"VaribaleCostID" : 178,"HouseholdID" : 4, "ItemID" : 42, "Amount" : 1 },
                 
                 # ID:43 International Primary School, Yearly for 1 Child (USD)
                 {"VaribaleCostID" : 179,"HouseholdID" : 4, "ItemID" : 43, "Amount" : 0.084 },
                 
                 ############################## CLOTHING ##############################
                 # ID:44 1 Pair of Jeans (Levis 501 Or Similar) (USD)
                 {"VaribaleCostID" : 180,"HouseholdID" : 4, "ItemID" : 44, "Amount" : 2 },
                 
                 # ID:45 1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)
                 {"VaribaleCostID" : 181,"HouseholdID" : 4, "ItemID" : 45, "Amount" : 4 },
                 
                 # ID:46 1 Pair of Nike Running Shoes (Mid-Range) (USD)
                 {"VaribaleCostID" : 182,"HouseholdID" : 4, "ItemID" : 46, "Amount" : 1 },
                 
                 # ID:47 1 Pair of Men Leather Business Shoes (USD)
                 {"VaribaleCostID" : 183,"HouseholdID" : 4, "ItemID" : 47, "Amount" : 0.5 },
                 
                 # ID:54 Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate
                 #{"VaribaleCostID" : 184,"HouseholdID" : 4, "ItemID" : 54, "Amount" : 1 },
                

                 ############################################################################
                 ######################### NEW HOUSEHOLD (ID:5)#########################
                 ############################################################################
                 
                 ############################## RESTAURANT/BAR ##############################
                #  # ID:1 Meal, Inexpensive Restaurant (USD)
                #  {"VaribaleCostID" : 185,"HouseholdID" : 5, "ItemID" : 1, "Amount" : 1 },
                 
                #  # ID:2 Meal for 2 People, Mid-range Restaurant, Three-course (USD)
                #  {"VaribaleCostID" : 186,"HouseholdID" : 5, "ItemID" : 2, "Amount" : 1 },
                 
                #  # ID:3 McMeal at McDonalds (or Equivalent Combo Meal) (USD)
                #  {"VaribaleCostID" : 187,"HouseholdID" : 5, "ItemID" : 3, "Amount" : 1 },
                 
                #  # ID:4 Domestic Beer (0.5 liter draught, in restaurants) (USD)
                #  {"VaribaleCostID" : 187,"HouseholdID" : 5, "ItemID" : 4, "Amount" : 1 },
                 
                #  # ID:5 Imported Beer (0.33 liter bottle, in restaurants) (USD)
                #  {"VaribaleCostID" : 188,"HouseholdID" : 5, "ItemID" : 5, "Amount" : 1 },
                 
                #  # ID:6 Cappuccino (regular, in restaurants) (USD)
                #  {"VaribaleCostID" : 189,"HouseholdID" : 5, "ItemID" : 6, "Amount" : 1 },
                 
                #  # ID:7 Coke/Pepsi (0.33 liter bottle, in restaurants) (USD)
                #  {"VaribaleCostID" : 190,"HouseholdID" : 5, "ItemID" : 7, "Amount" : 1 },
                 
                #  # ID:8 Water (0.33 liter bottle, in restaurants) (USD)
                #  {"VaribaleCostID" : 191,"HouseholdID" : 5, "ItemID" : 8, "Amount" : 1 },
                 
                #  ############################## SUPERMARKET ##############################
                #  # ID:9 Milk (regular), (1 liter) (USD)
                #  {"VaribaleCostID" : 192,"HouseholdID" : 5, "ItemID" : 9, "Amount" : 1 },
                 
                #  # ID:10 Loaf of Fresh White Bread (500g) (USD)
                #  {"VaribaleCostID" : 193,"HouseholdID" : 5, "ItemID" : 10, "Amount" : 1 },
                 
                #  # ID:11 Rice (white), (1kg) (USD)
                #  {"VaribaleCostID" : 194,"HouseholdID" : 5, "ItemID" : 11, "Amount" : 1 },
                 
                #  # ID:12 Eggs (regular) (12) (USD)
                #  {"VaribaleCostID" : 195,"HouseholdID" : 5, "ItemID" : 12, "Amount" : 1 },
                 
                #  # ID:13 Local Cheese (1kg) (USD)
                #  {"VaribaleCostID" : 196,"HouseholdID" : 5, "ItemID" : 13, "Amount" : 1 },
                 
                #  # ID:14 Chicken Fillets (1kg) (USD)
                #  {"VaribaleCostID" : 197,"HouseholdID" : 5, "ItemID" : 14, "Amount" : 1 },
                 
                #  # ID:15 Beef Round (1kg) (or Equivalent Back Leg Red Meat) (USD)
                #  {"VaribaleCostID" : 198,"HouseholdID" : 5, "ItemID" : 15, "Amount" : 1 },
                 
                #  # ID:16 Apples (1kg) (USD)
                #  {"VaribaleCostID" : 199,"HouseholdID" : 5, "ItemID" : 16, "Amount" : 1 },
                 
                #  # ID:17 Banana (1kg) (USD)
                #  {"VaribaleCostID" : 200,"HouseholdID" : 5, "ItemID" : 17, "Amount" : 1 },
                 
                #  # ID:18 Oranges (1kg) (USD)
                #  {"VaribaleCostID" : 201,"HouseholdID" : 5, "ItemID" : 18, "Amount" : 1 },
                 
                #  # ID:19 Tomato (1kg) (USD)
                #  {"VaribaleCostID" : 202,"HouseholdID" : 5, "ItemID" : 19, "Amount" : 1 },
                 
                #  # ID:20 Potato (1kg) (USD)
                #  {"VaribaleCostID" : 203,"HouseholdID" : 5, "ItemID" : 20, "Amount" : 1 },
                 
                #  # ID:21 Onion (1kg) (USD)
                #  {"VaribaleCostID" : 204,"HouseholdID" : 5, "ItemID" : 21, "Amount" : 1 },
                 
                #  # ID:22 Lettuce (1 head) (USD)
                #  {"VaribaleCostID" : 205,"HouseholdID" : 5, "ItemID" : 22, "Amount" : 1 },
                 
                #  # ID:23 Water (1.5 liter bottle, at the market) (USD)
                #  {"VaribaleCostID" : 206,"HouseholdID" : 5, "ItemID" : 23, "Amount" : 1 },
                 
                #  # ID:24 Bottle of Wine (Mid-Range, at the market) (USD)
                #  {"VaribaleCostID" : 207,"HouseholdID" : 5, "ItemID" : 24, "Amount" : 1 },
                 
                #  # ID:25 Domestic Beer (0.5 liter bottle, at the market) (USD)
                #  {"VaribaleCostID" : 208,"HouseholdID" : 5, "ItemID" : 25, "Amount" : 1 },
                 
                #  # ID:26 Imported Beer (0.33 liter bottle, at the market) (USD)
                #  {"VaribaleCostID" : 209,"HouseholdID" : 5, "ItemID" : 26, "Amount" : 1 },
                 
                #  # ID:27 Cigarettes 20 Pack (Marlboro) (USD)
                #  {"VaribaleCostID" : 210,"HouseholdID" : 5, "ItemID" : 27, "Amount" : 1 },
                 
                #  ############################## TRANSPORT ##############################
                #  # ID:28 One-way Ticket (Local Transport) (USD)
                #  {"VaribaleCostID" : 211,"HouseholdID" : 5, "ItemID" : 28, "Amount" : 1 },
                 
                #  # ID:29 Monthly Pass (Regular Price) (USD)
                #  {"VaribaleCostID" : 212,"HouseholdID" : 5, "ItemID" : 29, "Amount" : 1 },
                 
                #  # ID:30 Taxi Start (Normal Tariff) (USD)
                #  {"VaribaleCostID" : 213,"HouseholdID" : 5, "ItemID" : 30, "Amount" : 1 },
                 
                #  # ID:31 Taxi 1km (Normal Tariff) (USD)
                #  {"VaribaleCostID" : 214,"HouseholdID" : 5, "ItemID" : 31, "Amount" : 1 },
                 
                #  # ID:32 Taxi 1hour Waiting (Normal Tariff) (USD)
                #  {"VaribaleCostID" : 215,"HouseholdID" : 5, "ItemID" : 32, "Amount" : 1 },
                 
                #  # ID:33 Gasoline (1 liter) (USD)
                #  {"VaribaleCostID" : 216,"HouseholdID" : 5, "ItemID" : 33, "Amount" : 1 },
                 
                #  # ID:34 Volkswagen Golf 1.4 90 KW Trendline (Or Equivalent New Car) (USD)
                #  {"VaribaleCostID" : 217,"HouseholdID" : 5, "ItemID" : 34, "Amount" : 1 },
                 
                #  # ID:35 Toyota Corolla Sedan 1.6l 97kW Comfort (Or Equivalent New Car) (USD)
                #  {"VaribaleCostID" : 218,"HouseholdID" : 5, "ItemID" : 35, "Amount" : 1 },
                 
                #  # ID:37 1 min. of Prepaid Mobile Tariff Local (No Discounts or Plans) (USD)
                #  {"VaribaleCostID" : 219,"HouseholdID" : 5, "ItemID" : 37, "Amount" : 1 },

                #  ############################## LEISURE ##############################
                #  # ID:39 Fitness Club, Monthly Fee for 1 Adult (USD)
                #  {"VaribaleCostID" : 220,"HouseholdID" : 5, "ItemID" : 39, "Amount" : 1 },
                 
                #  # ID:40 Tennis Court Rent (1 Hour on Weekend) (USD)
                #  {"VaribaleCostID" : 221,"HouseholdID" : 5, "ItemID" : 40, "Amount" : 1 },
                 
                #  # ID:41 Cinema, International Release, 1 Seat (USD)
                #  {"VaribaleCostID" : 222,"HouseholdID" : 5, "ItemID" : 41, "Amount" : 1 },
                 
                #  ############################## EDUCATION ##############################
                #  # ID:42 Preschool (or Kindergarten), Full Day, Private, Monthly for 1 Child (USD)
                #  {"VaribaleCostID" : 223,"HouseholdID" : 5, "ItemID" : 42, "Amount" : 1 },
                 
                #  # ID:43 International Primary School, Yearly for 1 Child (USD)
                #  {"VaribaleCostID" : 224,"HouseholdID" : 5, "ItemID" : 43, "Amount" : 1 },
                 
                #  ############################## CLOTHING ##############################
                #  # ID:44 1 Pair of Jeans (Levis 501 Or Similar) (USD)
                #  {"VaribaleCostID" : 225,"HouseholdID" : 5, "ItemID" : 44, "Amount" : 1 },
                 
                #  # ID:45 1 Summer Dress in a Chain Store (Zara, H&M, …) (USD)
                #  {"VaribaleCostID" : 226,"HouseholdID" : 5, "ItemID" : 45, "Amount" : 1 },
                 
                #  # ID:46 1 Pair of Nike Running Shoes (Mid-Range) (USD)
                #  {"VaribaleCostID" : 227,"HouseholdID" : 5, "ItemID" : 46, "Amount" : 1 },
                 
                #  # ID:47 1 Pair of Men Leather Business Shoes (USD)
                #  {"VaribaleCostID" : 228,"HouseholdID" : 5, "ItemID" : 47, "Amount" : 1 },
                 
                #  # ID:54 Mortgage Interest Rate in Percentages (%), Yearly, for 20 Years Fixed-Rate
                #   {"VaribaleCostID" : 229,"HouseholdID" : 5, "ItemID" : 54, "Amount" : 1 },
                
                ]

VariableCosts = pd.DataFrame(invented_data_variablecosts, columns=["VaribaleCostID", "HouseholdID", "ItemID", "Amount"])

VariableCosts.to_csv(file_path + "transformed_data/" + "VariableCosts.csv", index = False)

######################################################################
### Creation of FixedCosts
######################################################################

invented_data_fixedcosts = [
                 ############################################################################
                 ######################### BASELINE HOUSEHOLD (ID:1)#########################
                 ############################################################################
                 
                 ############################## BASIC NEEDS ##############################
                 #ID:36	Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)
                 {"FixedCostID" : 1,"HouseholdID" : 1, "ItemID" : 36},
                 
                 #ID:38 Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)
                 {"FixedCostID" : 2,"HouseholdID" : 1, "ItemID" : 38},
                 
                 ############################## RENT ##############################
                 #ID:48 Apartment (1 bedroom) in City Centre (USD)
                 {"FixedCostID" : 3,"HouseholdID" : 1, "ItemID" : 48},
                 
                 #ID:49 Apartment (1 bedroom) Outside of Centre (USD)
                 {"FixedCostID" : 4,"HouseholdID" : 1, "ItemID" : 49},
                 
                 #ID:50 Apartment (3 bedrooms) in City Centre (USD)
                 {"FixedCostID" : 5,"HouseholdID" : 1, "ItemID" : 50},
                 
                 #ID:51 Apartment (3 bedrooms) Outside of Centre (USD)
                 {"FixedCostID" : 6,"HouseholdID" : 1, "ItemID" : 51},
                 
                 ############################## HOUSE PRICE ##############################
                 #ID:52 Price per Square Meter to Buy Apartment in City Centre (USD)
                 #{"FixedCostID" : 7,"HouseholdID" : 1, "ItemID" : 52},
                 
                 #ID:53 Price per Square Meter to Buy Apartment Outside of Centre (USD)
                 #{"FixedCostID" : 8,"HouseholdID" : 1, "ItemID" : 53},
                 
                 
                 ############################################################################
                 ########################## SINGLE HOUSEHOLD (ID:2)##########################
                 ############################################################################
                 
                 ############################## BASIC NEEDS ##############################
                 #ID:36	Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)
                 {"FixedCostID" : 9,"HouseholdID" : 2, "ItemID" : 36},
                 # This needs to be halfed in later calculation
                 
                 #ID:38 Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)
                 {"FixedCostID" : 10,"HouseholdID" : 2, "ItemID" : 38},
                 
                 ############################## RENT ##############################
                 #ID:48 Apartment (1 bedroom) in City Centre (USD)
                 {"FixedCostID" : 11,"HouseholdID" : 2, "ItemID" : 48},
                 
                 #ID:49 Apartment (1 bedroom) Outside of Centre (USD)
                 #{"FixedCostID" : 12,"HouseholdID" : 2, "ItemID" : 49},
                 
                 #ID:50 Apartment (3 bedrooms) in City Centre (USD)
                 #{"FixedCostID" : 13,"HouseholdID" : 2, "ItemID" : 50},
                 
                 #ID:51 Apartment (3 bedrooms) Outside of Centre (USD)
                 #{"FixedCostID" : 14,"HouseholdID" : 2, "ItemID" : 51},
                 
                 ############################## HOUSE PRICE ##############################
                 #ID:52 Price per Square Meter to Buy Apartment in City Centre (USD)
                 #{"FixedCostID" : 15,"HouseholdID" : 2, "ItemID" : 52},
                 
                 #ID:53 Price per Square Meter to Buy Apartment Outside of Centre (USD)
                 #{"FixedCostID" : 16,"HouseholdID" : 2, "ItemID" : 53},
                 
                 ############################################################################
                 #################### PARTNER DUALSALARY HOUSEHOLD (ID:3)####################
                 ############################################################################
                 
                 ############################## BASIC NEEDS ##############################
                 #ID:36	Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)
                 {"FixedCostID" : 17,"HouseholdID" : 3, "ItemID" : 36},
                 
                 #ID:38 Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)
                 {"FixedCostID" : 18,"HouseholdID" : 3, "ItemID" : 38},
                 
                 ############################## RENT ##############################
                 #ID:48 Apartment (1 bedroom) in City Centre (USD)
                 #{"FixedCostID" : 19,"HouseholdID" : 3, "ItemID" : 48},
                 
                 #ID:49 Apartment (1 bedroom) Outside of Centre (USD)
                 #{"FixedCostID" : 20,"HouseholdID" : 3, "ItemID" : 49},
                 
                 #ID:50 Apartment (3 bedrooms) in City Centre (USD)
                 {"FixedCostID" : 21,"HouseholdID" : 3, "ItemID" : 50},
                 
                 #ID:51 Apartment (3 bedrooms) Outside of Centre (USD)
                 #{"FixedCostID" : 22,"HouseholdID" : 3, "ItemID" : 51},
                 
                 ############################## HOUSE PRICE ##############################
                 #ID:52 Price per Square Meter to Buy Apartment in City Centre (USD)
                 #{"FixedCostID" : 23,"HouseholdID" : 3, "ItemID" : 52},
                 
                 #ID:53 Price per Square Meter to Buy Apartment Outside of Centre (USD)
                 #{"FixedCostID" : 24,"HouseholdID" : 3, "ItemID" : 53},

                 ############################################################################
                 ######################### Partner_withChild (ID:4)##########################
                 ############################################################################
                 
                 ############################## BASIC NEEDS ##############################
                 #ID:36	Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)
                 {"FixedCostID" : 25,"HouseholdID" : 4, "ItemID" : 36},
                 
                 #ID:38 Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)
                 {"FixedCostID" : 26,"HouseholdID" : 4, "ItemID" : 38},
                 
                 ############################## RENT ##############################
                 #ID:48 Apartment (1 bedroom) in City Centre (USD)
                 #{"FixedCostID" : 27,"HouseholdID" : 4, "ItemID" : 48},
                 
                 #ID:49 Apartment (1 bedroom) Outside of Centre (USD)
                 #{"FixedCostID" : 28,"HouseholdID" : 4, "ItemID" : 49},
                 
                 #ID:50 Apartment (3 bedrooms) in City Centre (USD)
                 {"FixedCostID" : 29,"HouseholdID" : 4, "ItemID" : 50},
                 
                 #ID:51 Apartment (3 bedrooms) Outside of Centre (USD)
                 #{"FixedCostID" : 30,"HouseholdID" : 4, "ItemID" : 51},
                 
                 ############################## HOUSE PRICE ##############################
                 #ID:52 Price per Square Meter to Buy Apartment in City Centre (USD)
                 #{"FixedCostID" : 31,"HouseholdID" : 4, "ItemID" : 52},
                 
                 #ID:53 Price per Square Meter to Buy Apartment Outside of Centre (USD)
                 #{"FixedCostID" : 32,"HouseholdID" : 4, "ItemID" : 53},   
                

                 ############################################################################
                 ######################### NEW HOUSEHOLD (ID:5)#########################
                 ############################################################################
                 
                 ############################## BASIC NEEDS ##############################
                #  #ID:36	Basic (Electricity, Heating, Cooling, Water, Garbage) for 85m2 Apartment (USD)
                #  {"FixedCostID" : 33,"HouseholdID" : 5, "ItemID" : 36},
                 
                #  #ID:38 Internet (60 Mbps or More, Unlimited Data, Cable/ADSL) (USD)
                #  {"FixedCostID" : 34,"HouseholdID" : 5, "ItemID" : 38},
                 
                #  ############################## RENT ##############################
                #  #ID:48 Apartment (1 bedroom) in City Centre (USD)
                #  {"FixedCostID" : 35,"HouseholdID" : 5, "ItemID" : 48},
                 
                #  #ID:49 Apartment (1 bedroom) Outside of Centre (USD)
                #  {"FixedCostID" : 36,"HouseholdID" : 5, "ItemID" : 49},
                 
                #  #ID:50 Apartment (3 bedrooms) in City Centre (USD)
                #  {"FixedCostID" : 37,"HouseholdID" : 5, "ItemID" : 50},
                 
                #  #ID:51 Apartment (3 bedrooms) Outside of Centre (USD)
                #  {"FixedCostID" : 38,"HouseholdID" : 5, "ItemID" : 51},
                 
                #  ############################## HOUSE PRICE ##############################
                #  #ID:52 Price per Square Meter to Buy Apartment in City Centre (USD)
                #  {"FixedCostID" : 39,"HouseholdID" : 5, "ItemID" : 52},
                 
                #  #ID:53 Price per Square Meter to Buy Apartment Outside of Centre (USD)
                #  {"FixedCostID" : 40,"HouseholdID" : 5, "ItemID" : 53},
                 ]

FixedCosts = pd.DataFrame(invented_data_fixedcosts, columns=["FixedCostID", "HouseholdID", "ItemID"])
FixedCosts.to_csv(file_path + "transformed_data/" + "FixedCosts.csv", index = False)

######################################################################
### Creation of HouseholdsCities
######################################################################
#HouseholdsCities = pd.DataFrame(columns = ["HouseholdID", "Name", "CityID" "NumberSalaries", "NumberInhabitants"])

data_to_append = []

for _, row in Households_without_cityid.iterrows():
    for city in cityid:
        data = {
            "HouseholdID": row["HouseholdID"],
            "Name": row["Name"],
            "CityID": city,
            "NumberSalaries": row["NumberSalaries"],
            "NumberInhabitants": row["NumberInhabitants"]
        }
        data_to_append.append(data)

HouseholdsCities = pd.DataFrame(data_to_append, columns=["HouseholdID", "CityID"])

HouseholdsCitiesid = list(range(1, len (HouseholdsCities) + 1))

# adding SalaryID to cityandsalary based on list salaryid
HouseholdsCities["HouseholdsCityID"] = HouseholdsCitiesid

HouseholdsCities = HouseholdsCities.reindex(columns=["HouseholdsCityID", "HouseholdID", "CityID"])
HouseholdsCities.to_csv(file_path + "transformed_data/" + "HouseholdsCities.csv", index = False)