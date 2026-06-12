# Running Digital Twin AI System in Docker

This guide explains how to build, configure, and run the Personal Digital Twin application (FastAPI backend + Vite/React frontend + Redis cache) using Docker and Docker Compose.

---

## 1. Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- **SQL Server Connection Setup (Required):**
  Since the backend container runs in Linux, Windows Authentication (`trusted_connection=yes`) will **not** work. You must configure SQL Server Authentication:
  1. Open **SQL Server Management Studio (SSMS)**.
  2. Right-click the server instance name -> click **Properties** -> click **Security** -> select **SQL Server and Windows Authentication mode** under *Server authentication*.
  3. Expand **Security** -> click **Logins** -> right-click **sa** (or create a new user login) -> click **Properties**. Set a strong password, and in the *Status* page, make sure the login is **Enabled** and permission to connect is **Granted**.
  4. Ensure SQL Server is configured to allow TCP/IP connections (open **SQL Server Configuration Manager**, enable TCP/IP under *SQL Server Network Configuration -> Protocols*, and verify the TCP Port under *IP Addresses*, which is typically `1433`).
  5. Restart the SQL Server Windows service.

---

## 2. Environment Configuration

Open the [DigitalTwin.API/.env](file:///c:/Users/User/OneDrive/Desktop/4th%20year/Semester%208/mini%20Project/agentic%20project/Artificial-Personal-Digital-Twin/DigitalTwin.API/.env) file and adjust the database configurations for Docker:

```properties
# 1. Mongo DB (Atlas Uri works automatically inside Docker)
MONGO_URI=mongodb+srv://...

# 2. Redis Configuration (Docker Compose overrides host to 'redis')
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 3. SQL Server (Connect to Host database via docker gateway)
DB_HOST=host.docker.internal
DB_NAME=DigitalTwin
DB_AUTH=sql
DB_USER=sa
DB_PASSWORD=YourSQLServerPassword
```

> [!NOTE]
> `host.docker.internal` is a special DNS name that resolves to the internal IP address used by the host machine. This enables the Docker container to connect directly to the SQL Server database running on your Windows host.

---

## 3. How to Run with Docker Compose

Open a terminal in the root directory (where `docker-compose.yml` is located) and run:

### Build and Start Containers
```bash
docker compose up --build -d
```
- `--build`: Forces Docker to build/re-build images.
- `-d`: Runs containers in the background (detached mode).

### Accessing the Applications
- **Frontend Dashboard:** Open your web browser and go to [http://localhost](http://localhost) (port 80).
- **Backend API Interactive Docs:** Go to [http://localhost:8000/docs](http://localhost:8000/docs).

### View logs
To view the output of the running containers:
```bash
docker compose logs -f
```

### Stop Containers
```bash
docker compose down
```

---

## 4. Troubleshooting

### Firewall Blocked Connection to SQL Server
If the backend logs show a connection timeout or failure to connect to `host.docker.internal`, Windows Firewall may be blocking incoming requests on port 1433.
1. Open **Windows Defender Firewall with Advanced Security**.
2. Click **Inbound Rules** -> click **New Rule...** (in the Actions panel).
3. Select **Port** -> click **Next**.
4. Select **TCP**, and under *Specific local ports* type `1433` -> click **Next**.
5. Select **Allow the connection** -> click **Next**.
6. Check **Domain**, **Private**, and **Public** -> click **Next**.
7. Name the rule (e.g. `SQL Server Docker Access`) and click **Finish**.
