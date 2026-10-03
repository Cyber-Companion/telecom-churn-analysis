"""Download the IBM telco customer churn dataset (open data).

Source: https://github.com/IBM/telco-customer-churn-on-icp4d
Run from the project root:  python python/download_data.py
"""
import os
import urllib.request

URL = ("https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d"
       "/master/data/Telco-Customer-Churn.csv")

os.makedirs("data/raw", exist_ok=True)
dest = "data/raw/Telco-Customer-Churn.csv"
if os.path.exists(dest):
    print("exists, skipping")
else:
    print("downloading...")
    urllib.request.urlretrieve(URL, dest)
print("done:", dest)
