DROP TABLE IF EXISTS Countries, Cities, Salaries, Categories, Items, Prices, Households, HouseholdsCities, VariableCosts, FixedCosts;

CREATE TABLE Countries (
    CountryID INT PRIMARY KEY,
    Name VARCHAR(256)
);

CREATE TABLE Cities (
    CityID INT PRIMARY KEY,
    Name VARCHAR(256),
    CountryID INT REFERENCES Countries (CountryID)
);

CREATE TABLE Salaries (
  SalaryID INT PRIMARY KEY,
  Salary FLOAT,
  CityID INT REFERENCES Cities (CityID)
);

CREATE TABLE Categories (
  CategoryID INT PRIMARY KEY,
  Name VARCHAR (256)
);

CREATE TABLE Items (
  ItemID INT PRIMARY KEY,
  Name VARCHAR(256),
  CategoryID INT REFERENCES Categories (CategoryID)
);

CREATE TABLE Prices (
  PriceID INT PRIMARY KEY,
  ItemID INT REFERENCES Items (ItemID),
  CityID INT REFERENCES Cities (CityID),
  Price FLOAT
);

CREATE TABLE Households (
  HouseholdID INT PRIMARY KEY,
  Name VARCHAR(256),
  NumberSalaries INT,
  NumberInhabitants INT
);

CREATE TABLE HouseholdsCities (
    HouseholdsCitiesID INT PRIMARY KEY,
    HouseholdID INT REFERENCES Households (HouseholdID),
    CityID INT REFERENCES Cities (CityID)
);

CREATE TABLE VariableCosts (
  VariableCostID INT PRIMARY KEY,
  HouseholdID INT REFERENCES Households (HouseholdID),
  ItemID INT REFERENCES Items (ItemID),
  Amount FLOAT
);

CREATE TABLE FixedCosts (
  FixedCostID INT PRIMARY KEY,
  HouseholdID INT REFERENCES Households (HouseholdID),
  ItemID INT REFERENCES Items (ItemID)
);
