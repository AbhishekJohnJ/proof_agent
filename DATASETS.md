# ProofAI — Datasets & Data Pipeline Documentation

This document describes synthetic sample datasets used for development, testing, and benchmark evaluation.

> [!NOTE]
> All sample datasets included in `datasets/sample/` are synthetically generated under permissive licenses for development and testing purposes.

---

## Included Sample Datasets

### 1. `customers.csv`
* **Purpose**: Primary customer directory for relational joins.
* **Schema**:
  - `customer_id` (string/int): Unique customer identifier.
  - `name` (string): Customer full name.
  - `region` (string): Geographic region (North, South, East, West).
  - `signup_date` (ISO date): ISO-formatted signup date.
  - `tier` (string): Customer tier (Basic, Premium, Enterprise).

### 2. `orders.csv`
* **Purpose**: Transactional orders for relational joins with `customers.csv`.
* **Schema**:
  - `order_id` (string/int): Unique order identifier.
  - `customer_id` (string/int): Foreign key to `customers.csv`.
  - `order_date` (ISO date): Order date.
  - `amount` (float): Order value.
  - `status` (string): Order status (completed, pending, cancelled).

### 3. `sales.csv`
* **Purpose**: Clean tabular sales data for aggregation queries.
* **Schema**:
  - `transaction_id` (string): Unique transaction ID.
  - `date` (ISO date): Transaction date.
  - `region` (string): Sales region.
  - `category` (string): Product category.
  - `revenue` (float): Revenue amount.
  - `units_sold` (int): Number of units.

### 4. `messy_sales.csv`
* **Purpose**: Complex trap dataset for testing data quality engine, duplicate detection, ambiguous dates, and mixed currencies.
* **Contains Intentional Data Traps**:
  - Duplicated transaction rows.
  - Missing revenue/amount values (`NaN`, null, empty strings).
  - Ambiguous dates (`01/02/2024` vs `2024-02-01`).
  - Mixed currency values (`$100`, `€90`, `100 USD`, `JPY 15000`).
  - Constant/unusable columns (`company_name` constant across all rows).

---

## Dataset Quality Check Specifications

The Data Quality Engine ([backend/profiling/quality.py](file:///Users/Jivithesh/Desktop/PROJECTS/proof_agent/backend/profiling/quality.py)) automatically evaluates datasets for:
1. **Missing values**: Ratio and exact counts per column.
2. **Duplicate rows**: Full row duplication and primary key candidate duplication.
3. **Mixed Currency / Units**: Detection of currency symbols or strings within numerical fields.
4. **Ambiguous Dates**: Identification of date strings with ambiguous month/day ordering.
5. **Schema Anomalies**: Single-value columns, zero-variance columns, unparseable headers.

---

## License & Usage

All sample datasets are provided under the MIT License and contain no PII or real-world proprietary data.
