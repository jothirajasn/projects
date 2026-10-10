import pandas as pd
import mysql.connector

mydb = mysql.connector.connect (
    user = 'root',
    password = 'admin',
    database = 'company_db'
)

if mydb.is_connected:
    print('Database Connected')
else:
    print('Problem : Database not connected')

df = pd.read_csv("sales_orders_raw.csv")


# Display the first ten records
# print(df.head(10))

# Display the number of rows and columns
# print(df.shape)

# Display the column names
# print(df.columns)

# Remove unwanted spaces from text values
text_columns = ['customer_name', 'email', 'city', 'product', 'status'] 

for col in text_columns:
    df[col] = df[col].str.strip()

df = df[df["customer_name"] != ""]


# Remove unwanted spaces from middle of the text values
df["customer_name"] = (
    df["customer_name"]
    .str.strip()                                # leading/trailing spaces
    .str.replace(r"\s+", " ", regex=True)       # multiple spaces in the middle -> one space
)

# print(df[col])
# print(df['customer_name'])

numeric_columns = ['order_id', 'quantity', 'unit_price']

for col in numeric_columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# print('\nMissing values:')
# print(df.isna().sum())

print("\nRecords before cleaning:", len(df))
print(df)

df = df.drop_duplicates()
print("\ncount of df after dropped duplicates:", len(df))


df = df.dropna(subset=['order_id', 'customer_name', 'unit_price', 'quantity'])
print("\ncount of df after dropped mandatory fields:", len(df))

# print(df[df.duplicated()])

# df['customer_name'] = df['customer_name'].fillna('Unknown User')
# df['order_id'] = df['order_id'].fillna(0)

df['email'] = df['email'].fillna('email id not mentioned')
df['city'] = df['city'].fillna('City not mentioned')
df['product'] = df['product'].fillna('product name not mentioned')
df['order_date'] = df['order_date'].fillna('Date Not mentioned')
df['status'] = df['status'].fillna('status not mentioned')

# print(df['customer_name'].fillna('Unknown User'))
# print(df.isna().sum())

print("\nRecords after cleaning:", len(df))

# print(df)

# print(df[df.duplicated(subset=['order_id'], keep='first')])

cursor = mydb.cursor()

sql = '''
insert into sales_order
(order_id,customer_name,email,city,product,quantity,unit_price,order_date,status)
values
(%s, %s, %s, %s, %s, %s, %s, %s, %s)

'''

columns = ['order_id','customer_name','email','city','product','quantity','unit_price','order_date','status']

data = [
    tuple(None if pd.isna(v) else v for v in row)
    for row in df[columns].itertuples(index=False, name=None)
]

try:
    cursor.executemany(sql, data)
    mydb.commit()
    print(f'Loaded records{cursor.rowcount} successfully')

except Exception:
    mydb.rollback()
    raise

finally:
    cursor.close
    mydb.close

