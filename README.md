# ETL Assessment Project

## Overview

This project is an ETL (Extract, Transform, Load) exercise to demonstrate data modeling and API development skills. It involves processing event data, defining a data model, and creating APIs.

### Main Features:

1. **Data Cleansing and Transformation**: 
   - Cleanses venue event data from a CSV file.
   - Splits event categories by semicolon (`;`).
   - Formats time ranges for venue operation hours.

2. **API Endpoints**:
   - Query venues by event category.
   - Query venues by day of the week.
   - Query venues with events happening at the current time.
  

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Docker** and **Docker Compose**

Ensure you have both Python and Docker installed on your machine.

### Project Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd etl_assessment
   ```

2. **Set Up the Environmen**:
Create a .env file in the root directory with the following variables:

    ```bash
    POSTGRES_DB=your_db_name
    POSTGRES_USER=your_db_user
    POSTGRES_PASSWORD=your_db_password
    ```
3. **Docker Compose**:
- The project includes a `Dockerfile` and `docker-compose.yml` for containerizing the FastAPI app and the Postgres database.
- To build and run the services, use the following command:
    ```bash
    docker-compose up --build
    ```

## API Endpoints
1. **Query Businesses by Category**
   - **URL**: `/businesses/category/{category_name}`
   - **Method**: `GET`
   - **Description**: Returns businesses hosting events in the specified category.
   - **Example**:
    ```bash
    curl http://localhost:8000/businesses/category/Music
    ```

2. **Query Businesses by Day of the Week**
   - **URL**: `/businesses/day/{day_of_week}`
   - **Method**: `GET`
   - **Description**: Returns businesses that have events scheduled on the specified day.
   - **Example**:
    ```bash
    curl http://localhost:8000/businesses/day/Tuesday
    ```

3. **Query Businesses Hosting Events Now**
   - **URL**: `/businesses/open-now`
   - **Method**: `GET`
   - **Description**: Returns businesses hosting events at the current time.
   - **Example**:
    ```bash
    curl http://localhost:8000/businesses/open-now
    ```

## Data Model
1. **Business Model**:

    - `id`: Primary Key
    - `timezone`: Timezone of the business
    - `rating`: Business rating
    - `max_rating`: Maximum possible rating
    - `review_count`: Total reviews
    - `Relationships`:
        - `categories`: Relationship to Category
        - `hours`: Relationship to BusinessHours

2. **Category Model**:

    - `id`: Primary Key
    - `category`: Category of the event
    - `business`: ForeignKey to Business

3. **BusinessHours Model**:

    - `id`: Primary Key
    - `business`: ForeignKey to Business
    - `day`: Day of the week (e.g., "Monday")
    - `shift1_start`, `shift1_end`, `shift2_start`, `shift2_end`: Operation hours of the business
  
## Testing the APIs
Once the services are up and running, you can test the API using the following methods:
1. **Using cURL**: Examples provided in the API section for each endpoint.
2. **Swagger UI**: FastAPI automatically generates an interactive API documentation. Navigate to the following URL in your browser to test endpoints:
    ```bash
    http://localhost:8000/docs
    ```

3. **Postman**: You can also import the endpoints into Postman and test the API.

## Development Notes
### Future Enhancements
- Implement error handling for more edge cases (e.g., CSV format changes).
- Expand API capabilities to include filtering by multiple categories and flexible time ranges.
- Add tests.