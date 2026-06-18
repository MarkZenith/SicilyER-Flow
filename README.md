# SicilyER-Flow
**An end-to-end data platform for monitoring and estimating emergency room wait times in Sicily.**

## Project Overview
SicilyER-Flow is a comprehensive data engineering and machine learning project designed to simulate, ingest, transform, and analyze hospital emergency room (ER) data in real-time. This project addresses a high-impact social use case by applying modern data architectures to healthcare logistics.

### Architecture & Tech Stack
* **Data Generation:** Python mock API simulating realistic ER admissions across Sicilian hospitals.
* **Cloud Storage:** AWS S3 for landing raw JSON payloads.
* **Data Warehouse:** Snowflake (Medallion Architecture: Bronze, Silver, Gold).
* **Data Transformation:** dbt (data build tool) for scheduled ETL processes.
* **Machine Learning:** Snowpark for training and deploying wait-time prediction models natively within Snowflake.
* **Data Visualization:** Streamlit in Snowflake for real-time dashboards and KPI monitoring.

---

## License & Intellectual Property
The code, architecture, and logic presented in this repository (SicilyER-Flow) are the exclusive property of the author. This project is made public **strictly for portfolio showcase, peer review, and educational purposes**.

No part of this repository may be reproduced, distributed, or modified for commercial, operational, or derivative purposes without prior written permission.

Reach out to me on [LinkedIn](https://it.linkedin.com/in/marco-governale) or via email
