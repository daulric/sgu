-- Active: 1789401444062@@127.0.0.1@3306@northwind
-- 1. Provide a list of countries by name, that are represented in the customer database
SELECT `Country` 
FROM Customers
WHERE `Country` IS NOT NULL
GROUP BY `Country`;

-- 2. Provide a list of all such products with high quantities in stock, i.e., 50 or more.
SELECT `Products`.`ProductName`
FROM `Products`
INNER JOIN `Categories` 
ON `Products`.`CategoryID` = `Categories`.`CategoryID`
WHERE `Products`.`UnitsInStock` >= 50 AND `Categories`.`CategoryName` IN ('Beverages', 'Condiments', 'Confections');

-- 3. Which active products are at or below the minimum stock level (Hint: ReorderLevel) and have not been reordered yet?
SELECT `ProductName` 
FROM `Products`
WHERE `UnitsInStock` <= `ReorderLevel` AND `Discontinued` = 0 AND `UnitsOnOrder` = 0;

-- 4. Return the Product ID, Product Name and Price of products who name starts with ‘C’ and the price is between 18 and 22
SELECT `ProductID`, `ProductName`, `UnitPrice` 
FROM `Products`
WHERE `ProductName` LIKE "C%" AND `UnitPrice` BETWEEN 18 AND 22;

-- 5. Provide a list of all regions and the territories within the regions. Print only the names of regions and territories. Sort A-Z by region, then Z-A by territory.
SELECT `Region`.`RegionDescription` AS RegionName , `TerritoryDescription`
FROM `Territories`
INNER JOIN `Region` ON `Territories`.`RegionID` = `Region`.`RegionID`
ORDER BY `Region`.`RegionDescription` ASC, `Territories`.`TerritoryDescription` DESC;

-- 6. How many territories are there per region? List the region name and the amount of territories. Provide a proper name for the count of territories per region.
SELECT `Region`.`RegionDescription` AS RegionName ,COUNT(DISTINCT `Territories`.`TerritoryID`) as TerritoryCount
FROM `Territories`
JOIN `Region` ON `Territories`.`RegionID` = `Region`.`RegionID`
GROUP BY `Region`.`RegionDescription` ,`Region`.`RegionID`;

-- 7. Are there any territories for which there are no employees assigned? If so, list the names (only) of such territories and the corresponding region. Note: Use joins to accomplish this
SELECT `TerritoryDescription`, `Region`.`RegionDescription`
FROM `Territories`
LEFT JOIN `EmployeeTerritories` ON `Territories`.`TerritoryID` = `EmployeeTerritories`.`TerritoryID`
INNER JOIN `Region` ON `Territories`.`RegionID` = `Region`.`RegionID`
WHERE EmployeeTerritories.TerritoryID IS NULL;

-- 8. Show total number of products per category. Only include categories with at least 2 products.
SELECT `Categories`.`CategoryName`, COUNT(`Products`.`ProductID`) as TotalProducts
FROM `Products`
INNER JOIN `Categories` ON `Products`.`CategoryID` = `Categories`.`CategoryID`
GROUP BY `Categories`.`CategoryID`, `Categories`.`CategoryName`
HAVING COUNT(`Products`.`ProductID`) >= 2;

-- 9. Which shipper shipped the most orders? List the shipper name and the amount of orders shipped. Your query should return only the shipper that meets this requirement. Sorting in descending order does not suffice
SELECT `Shippers`.`CompanyName` AS `ShipperName`, COUNT(`Orders`.`OrderID`) AS `TotalOrders`
FROM `Shippers`
INNER JOIN `Orders` ON `Shippers`.`ShipperID` = `Orders`.`ShipVia`
GROUP BY `Shippers`.`ShipperID`, `Shippers`.`CompanyName`
HAVING COUNT(`Orders`.`OrderID`) = (
    SELECT MAX(`OrderCount`)
    FROM (
        SELECT COUNT(`OrderID`) AS `OrderCount`
        FROM `Orders`
        GROUP BY `ShipVia`
    ) AS `SubCounts`
);

-- 10. List all the products that were ever ordered by company ‘Ana Trujillo Emparedados y helados’
SELECT DISTINCT `Products`.`ProductName`
FROM `Customers`
INNER JOIN `Orders` 
    ON `Customers`.`CustomerID` = `Orders`.`CustomerID`
INNER JOIN `Order Details` 
    ON `Orders`.`OrderID` = `Order Details`.`OrderID`
INNER JOIN `Products` 
    ON `Order Details`.`ProductID` = `Products`.`ProductID`
WHERE `Customers`.`CompanyName` = 'Ana Trujillo Emparedados y helados';
