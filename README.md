# MySQL_HeatWave_NL2SQL
Materials related to MySQL HeatWave GenAI NL2SQL features on https://dasini.net/blog/
---
With the Natural Language to SQL feature in MySQL HeatWave, we’re witnessing a major shift in how we interact with databases. This technology empowers a broader range of users—from business analysts to product managers—to access and analyze data without needing deep SQL expertise. By simply using plain English, anyone can now translate a business question into an executable SQL query. This not only democratizes data access but also significantly accelerates the time from question to insight.


----


## Ask Your Database Anything: Natural Language to SQL in MySQL HeatWave
https://dasini.net/blog/2025/09/30/ask-your-database-anything-natural-language-to-sql-in-mysql-heatwave/

----


## Let Your AI DBA Assistant Write Your MySQL Queries


> The code (nl2sql4dba.py), is provided for illustrative purposes only. It may contain errors or limitations. Please use it at your own risk and adapt it to your specific needs (also feel free to share back).
----
## Usage
Update the ```config/config_heatwave.py``` file accordingly.

Ex:
```
DB_CONFIG = {
    "host": "10.1.0.123",           # MySQL HeatWave IP
    "user": "MyAppUser",            # MySQL HeatWave user name
    "password": "SeCr3(P4$$W0rd!",  # MySQL HeatWave User password
    "database": "nl2sql",           # MySQL Database name
    "port": 3306                    # MySQL HeatWave port
}

```
