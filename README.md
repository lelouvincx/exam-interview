# Answers for the exam interview

### Question 1

1. The function
```python
import re

def def_word_cnt(string: str) -> dict:
    word_cnt = {}
    string = re.sub(r"[^\w\s]", "", string)

    for word in string.strip().lower().split():
        if word in word_cnt.keys():
            word_cnt[word] += 1
        else:
            word_cnt[word] = 1

    return word_cnt
```

2. Save the result.xml
```python
string = "Ban la thi sinh tuyet voi nhat ma toi tung gap. Ban qua xuat sac, qua tuyet voi!"
word_cnt = def_word_cnt(string)

# Save to result.xml
print("Writing to result.xml")
with open("result.xml", "w") as f:
    f.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
    f.write("<word_cnt>\n")
    for word, cnt in word_cnt.items():
        f.write(f"\t<word>\n\t\t<value>{word}</value>\n\t\t<count>{cnt}</count>\n\t</word>\n")
    f.write("</word_cnt>\n")
```

3. Generate 100 files result_n.xml
```python
# Generate a list of filenames
file_names = [f"results/result_{i}.xml" for i in range(1, 101)]
# Create folder name "results", if not exist
of.mkdir("results") if not os.path.exists("results") else None
# Create the result string
result_string = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<word_cnt>\n"
for word, cnt in word_cnt.items():
    result_string += f"\t<word>\n\t\t<value>{word}</value>\n\t\t<count>{cnt}</count>\n\t</word>\n"
result_string += "</word_cnt>\n"
# Write to local disk
print("Writing to local disk")
list(map(lambda x: open(x, "w").write(result_string), file_names))
```

### Question 2
I've heard about Slow Changing Dimension, and I think it relates to this question. But I don't know much about this.

### Question 3

1. SQL script
```SQL
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
```

2. Extract
```python
def extract(filename: str) -> pd.DataFrame:
    """
    Extracts the data from the given file and returns a list of dictionaries
    """

    employees = []
    with open(filename, 'r') as f:
        employees = json.load(f)

    # Create a dataframe from the list of dictionaries
    df = pd.DataFrame(employees)

    # Check the quality of the dataframe
    if not check_quality(df):
        raise Exception("The dataframe failed the quality check")

    logger.debug(f"Extracted dataframe:\n{df.shape}")
    logger.debug(df.head())

    return df
```

3. Transform
```python
def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms the given dataframe
    """

    # Convert join_date to datetime
    df['join_date'] = pd.to_datetime(df['join_date'])

    # Drop the id column
    df.drop('id', axis=1, inplace=True)

    # Check the quality of the dataframe
    if not check_quality(df):
        raise Exception("The dataframe failed the quality check")

    logger.debug(f"Transformed dataframe:\n{df.shape}")
    logger.debug(df.head())

    return df
```

4. Load
First create the SQL Server client (current OS: Ubuntu 23.04):
```python
@contextmanager
def connect_sql_server():
    """
    Returns a connection client to the SQL Server
    """

    # Create a connection to the SQL Server
    try:
        yield pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};' +
                            'Server=localhost,1433;' +
                            'Database=master;' +
                            'UID=SA;' +
                            'PWD=' + SA_PASSWORD + ';' +
                            'TrustedServerCertificate=yes;' +
                            'Encrypt=no;'
                            )
        logger.info("Successfully connected to the SQL Server")
    except Exception as e:
        logger.exception("Failed to connect to the SQL Server")
```

Then load into the database:
```python
def load(df: pd.DataFrame) -> None:
    """
    Loads the given dataframe to the SQL Server
    """

    # Create a connection to the SQL Server
    with connect_sql_server() as conn:
        cursor = conn.cursor()

        # Loop through the dataframe
        for index, row in df.iterrows():
            # Create the query
            query = f"""
                INSERT INTO [dbo].[Employees] 
                    ([name], [department], [salary], [join_date]) 
                    VALUES ('{row['name']}', '{row['department']}', {row['salary']}, '{row['join_date']}')
            """
            # Execute the query
            cursor.execute(query)

        # Commit the changes
        conn.commit()
```

Since the `id` is auto crementing, we removed them in the transform step.

5. Error handling and data quality
Error handling is in the file [./Q2.py](source code).

Data quality:
```python
def check_quality(df: pd.DataFrame) -> bool:
    """
    Checks the quality of the dataframe
    """

    logger.info("Checking the quality of the dataframe")

    # Check if the dataframe is empty
    if df.empty:
        logger.warning("The dataframe is empty")
        return False

    # Check if the dataframe has the correct columns
    if not set(['name', 'department', 'salary', 'join_date']).issubset(df.columns):
        logger.error("The dataframe does not have the correct columns")
        return False

    # Check if the dataframe has the correct data types
    if not df['name'].dtype == 'object':
        logger.warning("The 'name' column does not have the correct data type")
    if not df['department'].dtype == 'object':
        logger.warning("The 'department' column does not have the correct data type")
    if not df['salary'].dtype == 'int64':
        logger.warning("The 'salary' column does not have the correct data type")
    if not df['join_date'].dtype == 'datetime64[ns]':
        logger.warning("The 'join_date' column does not have the correct data type")

    # Check if the salary column is positive
    if not (df['salary'] >= 0).all():
        logger.error("The 'salary' column has negative values")
        return False

    logger.info("The dataframe passed the quality check.")
    return True
```

If there's a false, raise error about data quality:
```python
# Check the quality of the dataframe
if not check_quality(df):
    raise Exception("The dataframe failed the quality check")
```

### Question 4

1. Count number of unique client order and number of orders by order month.
```sql
SELECT COUNT(DISTINCT [Client_ID])
FROM [dbo].[Order];

SELECT MONTH([Date_Order]) AS [Month_Order], COUNT([Order_ID]) AS [Num_Orders]
FROM [dbo].[Order]
GROUP BY MONTH([Date_Order]);
```

2. Get list of client who have more than 10 orders in this year.
```sql
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
```

3. From the above list of client: get information of first and second last order of client (Order date, good type, and amount)
```sql
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
```

4. Calculate total good amount and Count number of Order which were delivered in Sep.2019
```sql
SELECT
    SUM(o.[Good_Amount]) AS Total_Good_Amount,
    COUNT(o.[Order_ID]) AS Num_Orders
FROM [dbo].[Order] o
    INNER JOIN [dbo].[Order_Delivery] d
    ON o.[Order_ID] = d.[Order_ID]
WHERE 
    YEAR(d.[Date_Delivery]) = 2019
    AND MONTH(d.[Date_Delivery]) = 9;
```

5. Assuming your 2 tables contain a huge amount of data and each join will take about 30 hours, while you need to do daily report, what is your solution?

- Use materialized views to pre-calculate the aggregated or joined data required for your my reports. Then write a stored procedure to run it daily.
- Denomalize the 2 tables into 1 and apply dimensional modeling. Hence the fact-orders will have information like total good amount, total order count, ... And dimension tables such as dim-date, dim-client, dim-good store additional information for analytics

### Question 5
Here's the program solved using python: [./Q5.py](program).