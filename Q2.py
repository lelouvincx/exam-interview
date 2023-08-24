import pandas as pd
import pyodbc
from contextlib import contextmanager
from datetime import datetime
from dotenv import load_dotenv
import logging
import json
import os


# Load the environment variables
load_dotenv()
SA_PASSWORD = os.getenv('SA_PASSWORD')


# Setup the logger
logger = logging.getLogger(__name__)
# Create a stream and a file handler
stream_handler = logging.StreamHandler()
file_handler = logging.FileHandler('Q2.log')
# Set the level of the handlers
stream_handler.setLevel(logging.DEBUG)
file_handler.setLevel(logging.WARNING)
# Create a formatter and add it to the handlers
formatter = logging.Formatter('[%(asctime)s - %(levelname)s] %(message)s')
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
# Add the handlers to the logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


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


def main():
    # Extract, transform and load the data
    employees_df = extract('employees.json')
    employees_df = transform(employees_df)
    load(employees_df)


if __name__ == '__main__':
    main()