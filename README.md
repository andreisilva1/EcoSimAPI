----------

# 🌱 Ecosystem Simulation API

A simulation API for ecosystems containing organisms, plants, and complex ecological interactions.  
Built with **FastAPI**, **SQLModel**, **SQLAlchemy**, **Pydantic**, and full async support.

----------

## 📌 Table of Contents

-   Description
    
-   Technologies
    
-   Project Structure
    
-   Installation
    
-   How to Run
    
-   Endpoints
    
-   System Models
    
-   Relationships
    
-   Testing
    
-   Future Updates
    
-   License
    

----------

## 🧩 Description

This API allows the creation and simulation of ecosystems composed of:

-   **Organisms** (e.g., lion, bee, wolf, hippopotamus)
    
-   **Plants**
    
-   **Ecological interactions**, such as:
    
    -   pollination (plants ↔ pollinators)
        
    -   organisms belonging to ecosystems
        
    -   lifecycle simulation (age, hunger, thirst, fertility, etc.)
        

The system provides:

-   Full CRUD for all entities
    
-   Integrity validation
    
-   Many-to-many relations between plants and pollinators
    
-   Clean database per test run
    
-   REST-standardized routing
    
-   Async-first design
    

----------

## ⚙️ Technologies


**FastAPI** - API framework

**SQLModel** - ORM + Pydantic model layer

**SQLAlchemy** - Advanced relationship handling

**SQLite** (dev) - Local and default database

**Pytest + pytest-asyncio** - Automated testing

**httpx** - Async integration testing

**Docker + PostgreSQL** - Production database

----------


## 🏗️Project Structure
```plaintext
app/
│   .env.example
│   .gitignore
│   docker-compose.yml
│   pyproject.toml
│   README.md
│
├── main.py
├── __init__.py
│
├── api/
│   ├── dependencies.py
│   ├── __init__.py
│   │
│   ├── exceptions/
│   │   ├── exceptions.py
│   │
│   ├── interactions/
│   │   ├── attack_interactions.py
│   │   ├── interaction_functions.py
│   │
│   ├── routers/
│   │   ├── ecosystem.py
│   │   ├── defaults.py
│   │   ├── organism.py
│   │   ├── plant.py
│   │   └── __init__.py
│   │
│   ├── schemas/
│   │   ├── ecosystem.py
│   │   ├── organism.py
│   │   ├── plant.py
│   │   └── __init__.py
│   │
│   ├── services/
│   │   ├── ecosystem.py
│   │   ├── organism.py
│   │   ├── plant.py
│   │
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_ecosystem.py
│   │   ├── test_organism.py
│   │   ├── test_plant.py
│   │
│   └── utils/
│       ├── defaults.py
│       └── utils.py
│
└── database/
    ├── enums.py
    ├── interactions_list.py
    ├── models.py
    ├── session.py
    └── __init__.py

```

----------

## 🚀 Installation

### 1. Clone the repository

`git clone https://github.com/andreisilva1/EcoSimAPI.git` 

### 2. Create and activate a virtual environment

Create the virtual environment: `python -m venv venv`

Activate (Linux/macOS): `source venv/bin/activate` 

Activate (Windows): ` venv\Scripts\activate`  

### 3. Install dependencies

`pip install -r requirements.txt` 

----------


## ▶️ How to Run

Run the Docker container: `docker compose up -d`

Copy the .env.example and modify the DATABASE_URL as necessary

Start the API: `uvicorn app.main:app --reload`

  

**OBS:** If you start the API without a **DATABASE_URL** set in the `.env` file, **SQLite** will be used as the default database. If you want to use PostgreSQL via Docker, make sure the **DATABASE_URL** is set and the container is running.

  

Swagger UI is available at:

`http://localhost:8000/` 

----------

## 🌐 Endpoints

## 🤖 Default Routes

| Method | Path                                                               | Name                                  | Description |
|--------|--------------------------------------------------------------------|----------------------------------------|-------------|
| POST    | `defaults/add_defaults`                     | add_default_organisms_and_plants           | Adds 20 default organisms and 10 default plants to test the system immediately! |


---

## 🌱 Ecosystem Routes

| Method | Path                                                               | Name                                  | Description |
|--------|--------------------------------------------------------------------|----------------------------------------|-------------|
| GET    | `/ecosystem/{ecosystem_name_or_id}/organisms`                     | get_all_ecosystem_organisms           | Get all organisms inside an ecosystem |
| GET    | `/ecosystem/{ecosystem_name_or_id}/plants`                        | get_all_ecosystem_plants              | Get all plants inside an ecosystem |
| GET    | `/ecosystem/{ecosystem_id}/simulate`                              | simulate                              | Run a simulation for the ecosystem |
| POST   | `/ecosystem/create`                                               | create_eco_system                     | Create a new ecosystem |
| POST   | `/ecosystem/organism/add`                                         | add_organism_to_a_eco_system          | Add an organism to an ecosystem |
| POST   | `/ecosystem/plant/add`                                            | add_plant_to_a_eco_system             | Add a plant to an ecosystem |
| PATCH  | `/ecosystem/organisms/{organism_name}/update`                     | update_ecosystem_organism             | Update all the organisms in an ecosystem with that name |
| PATCH  | `/ecosystem/plants/{plant_name}/update`                           | update_ecosystem_plant                | Update all the plants in an ecosystem with that name |
| PATCH  | `/ecosystem/{ecosystem_id}`                                       | update_ecosystem_infos                | Update ecosystem information |
| DELETE | `/ecosystem/{ecosystem_id}`                                       | delete_ecosystem                      | Delete an ecosystem |
| DELETE | `/ecosystem/{ecosystem_id}/organism/{organism_name_or_id}/remove`| remove_organism_from_a_ecosystem      | Remove an organism from an ecosystem |
| DELETE | `/ecosystem/{ecosystem_id}/plant/{plant_name_or_id}/remove`       | remove_plant_from_a_ecosystem         | Remove a plant from an ecosystem |


---

## 🐾 Organism Routes

| Method | Path                                               | Name            | Description |
|--------|----------------------------------------------------|------------------|-------------|
| GET    | `/organism/`                                      | get_organism     | Search organisms by name |
| POST   | `/organism/create`                                | create_organism  | Create a new organism |
| PATCH  | `/organism/{organism_id}/update`                  | update_organism  | Update organism information |
| DELETE | `/organism/{organism_id}/delete`                  | delete_organism  | Delete an organism |


---

## 🌿 Plant Routes

| Method | Path                                               | Name               | Description |
|--------|----------------------------------------------------|---------------------|-------------|
| GET    | `/plant/`                                   | get_plants_by_name  | Search plants by name |
| POST   | `/plant/create`                                   | create_plant        | Create a new plant |
| PATCH  | `/plant/{plant_name_or_id}/update`                | update_plant        | Update plant information |
| DELETE | `/plant/{plant_name_or_id}/delete`                | delete_plant        | Delete a plant |



----------

## 🧬 System Models

### Organism Model Example

`payload: {"name": "Ant","weight": 0.000003,"size": 0.01,"age": 0,"max_age": 1,"reproduction_age":"fertility_rate": 50,"water_consumption": 0.0001,"food_consumption": 0.0002},
 params: {"type": "omnivore","diet_type": "omnivore","activity_cycle": "diurnal","speed": "fast","social_behavior": "herd" }`  

### Plant Model Example

`payload: {"name": "Testing Plant", "weight": 2, "age": 1, "reproduction_age": 3,
"size": 0, "max_age": 15, "fertility_rate": 2, "water_need": 5}, params: "type": "tree"` 

### Ecosystem Model Example

`payload:{"name": "Ecosystem test", "water_available": 1000, "max_water_to_add_per_simulation": 200}`

----------

## 🔗 Relationships

### 🌼 Pollination (Many-to-Many)

`pollinationlink`
 `├── pollinator_id (FK → organism.id)`
 `└── plant_id      (FK → plant.id) UNIQUE(pollinator_id, plant_id)` 

### 🐾 Ecosystem → Organisms (One-to-Many)

### 🌿 Ecosystem → Plants (One-to-Many)

----------

## 🧪 Testing

Run all tests:

`pytest` 

Test features include:

-   `ASGITransport` + `httpx.AsyncClient`
    
-   In-memory database created fresh per test
    
-   Automatic fixture isolation
    
-   Full integration testing for ecosystem behavior
    

----------

## 🔮 Future Updates

- BackgroundTasks for quick responses in larger ecosystems

- More interactions to organisms and plants

- Randomized ecological events

- Different environment types for a ecosystem

- Decomposers: New type of organisms with new interactions
    
    

----------

## 📜 License

MIT License — free to use, modify, and extend.


