# A simple script using built-in features to make a mock text file acting as our document asset
mock_data = """
INVOICE / PURCHASE ORDER
-------------------------------------
Document Reference: PO-998241
Vendor Alpha Distribution Channels
Date: July 11, 2026

LINE ITEMS:
SKU77281    500    12.50
SKU99104    1200   45.00
SKU11029    50     110.00

Total Amount Due: $66,250.00
-------------------------------------
Terms: Net 30 days. Authorized delivery signature required.
"""

with open("sample_invoice.txt", "w") as f:
    f.write(mock_data)
print("Generated sample_invoice.txt file successfully in your project directory.")