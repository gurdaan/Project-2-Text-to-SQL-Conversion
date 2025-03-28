from autogen import AssistantAgent, UserProxyAgent, register_function, GroupChatManager, GroupChat
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


config_list = [
    {
        'model': os.getenv('LLM_MODEL'),
        'api_key': os.getenv('LLM_API_KEY')
    }
]
LLM_CONFIG = {
    "config_list": config_list,
    "temperature": int(os.getenv('LLM_TEMPERATURE')),
}
async def create_query(user_query):
    SQL_Agent = AssistantAgent(
        name="SQL_Agent",
        system_message="""You are a specialized SQL query generator with knowledge of the following database schema:

        ### Database Schema ###
        Categories(CategoryID[PK], CategoryName, Description, Picture)
        Products(ProductID[PK], ProductName, SupplierID[FK], CategoryID, QuantityPerUnit, UnitPrice, UnitsInStock, UnitsOnOrder, ReorderLevel, Discontinued)
        Suppliers(ShipperID[PK], CompanyName, Phone)
        Employees(EmployeeID[PK], LastName, FirstName,Title, TitleOfCourtesy, BirthDate, HireDate, Address, City, Region, PostalCode, Country, HomePhone, Extension, Photo, Notes, ReportsTo[FK], PhotoPath)
        Employee_Territories(EmployeeID[PK/FK], TerritoryID[PK/FK], ...)
        Order_Details(OrderID[PK/FK], ProductID[PK/FK], UnitPrice, Quantity, Discount)
        Customers(CustomerID[PK], CompanyName, ContactName, ContactTitle, Address, City, Region, PostalCode, Country, Phone, Fax)
        Orders(OrderID[PK], CustomerID[FK], EmployeeID[FK], OrderDate, RequiredDate, ShippedDate, ShipVia[FK], Freight, ShipName, ShipAddress, ShipCity, ShipRegion, ShipPostalCode, ShipCountry)
        US_States(us_state_id[PK], state_name, state_abbr, state_region)

        Key Relationships:
        - Products.supplier_id → Suppliers.supplier_id
        - Orders.customer_id → Customers.customer_id
        - Orders.employer_id → Employees.employee_id
        - Order_Details references both Orders and Products
        - Employee_Territories references Employees

        Your task is to:
        1. Analyze the user's natural language query
        2. Generate the most appropriate SQL query based on the schema
        3. Handle joins, filters, and aggregations as needed
        4. Return ONLY the SQL query with no additional commentary
        5. If the query is ambiguous or cannot be answered with the given schema, return "ERROR: [reason]"

        Example:
        User: "Show me all products in the Beverages category"
        Output: SELECT p.* FROM Products p JOIN Categories c ON p.category_id = c.category_id WHERE c.category_name = 'Beverages';
        """,
        llm_config=LLM_CONFIG
    )


    user_proxy = UserProxyAgent(
        name="UserProxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        is_termination_msg=lambda msg: isinstance(msg, dict) and msg.get("content", "").strip().startswith(("SELECT", "INSERT", "UPDATE", "DELETE", "ERROR:")),
    )


    # Initialize chat and get response
    chat_result = await user_proxy.a_initiate_chat(
        SQL_Agent,
        message=user_query,
        max_turns=2,
    )

    # Extract the last message and clean it
    response = chat_result.chat_history[-1].get("content", "").strip()
    
    # Validate it's a proper SQL query or error message
    if not (response.startswith(("SELECT", "INSERT", "UPDATE", "DELETE")) or response.startswith("ERROR:")):
        response = f"ERROR: Invalid response format - {response}"
    
    return response