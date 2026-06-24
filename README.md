# Inventory Management System
A web-based Inventory Management System built using Flask, SQLite, HTML, and CSS.

## Features
- Add new inventory items
- Edit existing items
- Delete items
- Track stock in
- Track stock out
- View current inventory levels
- Dashboard for inventory overview

## Technologies Used
- Python
- Flask
- SQLite
- HTML
- CSS

## Project Structure
Inventory Management
|
|____static/
     |
     |____dashboard.css
     |_____stock_in.css
     |_____stock_out.css
     |_____sidebar.css
     |_____add_item.css
|
|____templates/
     |
     |____add_item_table.html
     |____add_item.html
     |____balance.html
     |____base.html
     |____edit_item.html
     |____home.html
     |____low_stock.html
     |____stock_in.html
     |____stock_in_table.html
     |____stock_out.html
     |____stock_out_table.html
|
|____app.py
|___db.py
|___gitignore
|___inventory.db
|___requirements.txt
|___schema.sql

## Installation

1. Clone the repository
 '''bash git clone https://github.com/hasijadishita-cell/job-application-tracker.git cd job-application-tracker

2. Install dependencies
pip install -r requirements.txt

3. Run the application
python app.py
For mac/Linux: 
python3 app.py

4. Open in your browser

## Future Improvements

- User authentication
- Sales reports
- Low stock alerts
- Barcode scanning
- Export inventory data to Excel/PDF

Author

Dishita Hasija
