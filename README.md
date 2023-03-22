# Warbler
Flask back end for a twitter clone.

Made with Flask, SQLalchemy, WTForms and Bcrypt

## Set Up
1. Create virtual environment and install dependencies
```py
  python3 -m venv venv
  source venv/bin/activate
  pip3 install -r requirements.txt
```
2. Set up PSQL database and seed data
```sql
  CREATE DATABASE warbler;
```
```py
  python3 seed.py
```

3. Create .env file and set up environment variables
```py
  SECRET_KEY=[YOUR SECRET KEY]
  DATABASE_URL=postgresql:///warbler
```

4. Run server `flask run -p 5001`
