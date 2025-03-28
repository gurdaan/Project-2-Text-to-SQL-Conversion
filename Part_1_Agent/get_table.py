import asyncio
import pyodbc
from typing import List, Dict, Union, Optional
import pandas as pd

async def execute_northwind_query(
    query: str, 
    server: str = 'GURDAAN_WALIA\SQLEXPRESS',
    database: str = 'Northwind',
    username: Optional[str] = None, 
    password: Optional[str] = None,
    trusted_connection: bool = True,
    as_dataframe: bool = False,
    timeout: int = 30,
    driver: str = 'SQL Server'
) -> Union[List[Dict], pd.DataFrame, Dict[str, int], None]:
    """
    Async version: Executes a SQL query against the Northwind database.
    
    Uses asyncio.to_thread to run blocking ODBC operations in a separate thread.
    """
    def _sync_execute():
        """Helper function for synchronous database operations"""
        connection = None
        cursor = None
        try:
            # Create connection string
            conn_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server};"
                f"DATABASE={database};"
            )
            
            if trusted_connection:
                conn_str += "Trusted_Connection=yes;"
            else:
                if not username or not password:
                    raise ValueError("Username and password required when trusted_connection is False")
                conn_str += f"UID={username};PWD={password};"
            
            # Establish connection
            connection = pyodbc.connect(conn_str, timeout=timeout)
            cursor = connection.cursor()
            
            # Execute query
            cursor.execute(query)
            
            # Process results
            if query.strip().upper().startswith('SELECT'):
                columns = [column[0] for column in cursor.description]
                data = cursor.fetchall()
                return pd.DataFrame.from_records(data, columns=columns) if as_dataframe else [dict(zip(columns, row)) for row in data]
            else:
                connection.commit()
                return {"rows_affected": cursor.rowcount}
                
        except pyodbc.Error as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    try:
        # Run the synchronous database operations in a separate thread
        return await asyncio.to_thread(_sync_execute)
    except pyodbc.Error as e:
        raise Exception(f"Database error: {str(e)}")
    except Exception as e:
        raise Exception(f"Error executing query: {str(e)}")

# def main():
#     try:
#         # Test connection with a simple query
#         print("Testing connection...")
#         result = execute_northwind_query("SELECT TOP 5 CompanyName FROM Customers")
#         print("Connection successful! First 5 customers:")
#         for row in result:
#             print(row['CompanyName'])
            
#     except Exception as e:
#         print(f"Connection failed: {str(e)}")
#         print("\nTroubleshooting tips:")
#         print("1. Verify SQL Server is running")
#         print("2. Check the server name is correct (GURDAAN_WALIA\\SQLEXPRESS)")
#         print("3. Ensure Windows Authentication is enabled")
#         print("4. Verify Northwind database exists on this server")
#         print("5. Check if SQL Server allows remote connections")

# if __name__ == "__main__":
#     main()