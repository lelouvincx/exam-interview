USE master
GO

CREATE TABLE Employees (
    [id] INT IDENTITY(1, 1) PRIMARY KEY,
    [name] VARCHAR(50) NOT NULL,
    [department] CHAR(10) NOT NULL,
    [salary] INT NOT NULL,
    [join_date] DATETIME2
);
GO

ALTER TABLE [dbo].[Employees]
    ADD CONSTRAINT CHK_SalaryPositive
    CHECK (salary > 0);
GO

SELECT * FROM [dbo].[Employees];
GO

CREATE TABLE [Order] (
    [Order_ID] INT PRIMARY KEY,
    [Date_Order] DATETIME2 NOT NULL,
    [Good_Type] VARCHAR(50),
    [Good_Amount] INT NOT NULL,
    [Client_ID] INT NOT NULL
)

CREATE TABLE [Order_Delivery] (
    [Order_ID] INT NOT NULL,
    [Date_Delivery] DATETIME2 NOT NULL,
    [Delivery_Employee_Code] CHAR(2) NOT NULL
)
GO

ALTER TABLE [dbo].[Order_Delivery]
    ADD CONSTRAINT FK_Order_Delivery_Order
    FOREIGN KEY ([Order_ID])
    REFERENCES [dbo].[Order] ([Order_ID]);
GO

-- Insert rows into table 'Order' in schema '[dbo]'
INSERT INTO [dbo].[Order]
    ( [Order_ID], [Date_Order], [Good_Type], [Good_Amount], [Client_ID] )
    VALUES 
        ( 10, '2019-05-01', 'Computer', 10000000, 88 ), 
        ( 24, '2020-06-06', 'Laptop', 8000000, 123 ),
        ( 35, '2020-10-07', 'Monitor', 3000000, 10 );
GO

-- Insert rows into table 'Order_Delivery' in schema [dbo]
INSERT INTO [dbo].[Order_Delivery]
    ( [Order_ID], [Date_Delivery], [Delivery_Employee_Code] )
    VALUES
        ( 10, '2020-07-06', '1a' ),
        ( 24, '2017-04-22', '5c' ),
        ( 35, '2018-11-09', '6e' )
GO

-- 1. Count number of unique client order and number of orders by order month.
SELECT COUNT(DISTINCT [Client_ID])
FROM [dbo].[Order];

SELECT MONTH([Date_Order]) AS [Month_Order], COUNT([Order_ID]) AS [Num_Orders]
FROM [dbo].[Order]
GROUP BY MONTH([Date_Order]);

-- 2. Get list of client who have more than 10 orders in this year.
CREATE TABLE #Temp_Clients (
    [Client_ID] INT PRIMARY KEY
);
GO

INSERT INTO #Temp_Clients ([Client_ID])
SELECT DISTINCT [Client_ID]
FROM [dbo].[Order]
WHERE YEAR([Date_Order]) = YEAR(GETDATE())
GROUP BY [Client_ID]
HAVING COUNT([Order_ID]) > 10;

-- 3. From the above list of client: get information of first and second last order of client (Order date, good type, and amount)
WITH Client_Order_Details AS (
    SELECT
        c.Client_ID,
        o.Order_ID,
        o.Date_Order,
        o.Good_Type,
        o.Good_Amount,
        ROW_NUMBER() OVER (PARTITION BY c.Client_ID ORDER BY o.Date_Order) AS Order_Rank_ASC,
        ROW_NUMBER() OVER (PARTITION BY c.Client_ID ORDER BY o.Date_Order DESC) AS Order_Rank_DESC
    FROM #Temp_Clients c
        INNER JOIN [dbo].[Order] o
        ON c.Client_ID = o.Client_ID
)
SELECT Client_ID, Order_ID, Date_Order, Good_Type, Good_Amount, Order_Rank_ASC, Order_Rank_DESC
FROM Client_Order_Details
WHERE
    Order_Rank_ASC = 1
    OR Order_Rank_DESC = 2;

-- 4. Calculate total good amount and Count number of Order which were delivered in Sep.2019
SELECT
    SUM(o.[Good_Amount]) AS Total_Good_Amount,
    COUNT(o.[Order_ID]) AS Num_Orders
FROM [dbo].[Order] o
    INNER JOIN [dbo].[Order_Delivery] d
    ON o.[Order_ID] = d.[Order_ID]
WHERE 
    YEAR(d.[Date_Delivery]) = 2019
    AND MONTH(d.[Date_Delivery]) = 9;