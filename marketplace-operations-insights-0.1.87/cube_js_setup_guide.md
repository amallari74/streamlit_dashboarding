### Setup Guide: Run Nonproduction Cube SQL Locally (macOS)

Follow these steps to connect your local app to the nonproduction Cube SQL endpoint.

1) Prerequisites
- AWS CLI v2, kubectl, Homebrew
- Install kubefwd (for Kubernetes DNS on your Mac) and psql (for testing)
  ```bash
  brew install txn2/tap/kubefwd libpq
  echo 'export PATH="/opt/homebrew/opt/libpq/bin:$PATH"' >> ~/.zshrc && source ~/.zshrc
  ```

2) Authenticate to AWS via SSO and create a profile
- When prompted, choose the nonproduction account and role (e.g., mog-dev-386726749336)
  ```bash
  aws configure sso --profile nonproduction
  # SSO start URL: https://d-90674c9a86.awsapps.com/start
  # SSO region: us-east-1
  # Default region: us-east-1
  # Output: json
  aws sso login --profile nonproduction
  aws sts get-caller-identity --profile nonproduction
  ```
  
3) Point kubectl at the nonproduction EKS cluster
```bash
AWS_PROFILE=nonproduction aws eks --region us-east-1 update-kubeconfig --name nonproduction-us-east-1-a
kubectl get ns
kubectl -n cube-js get svc cube-js -o wide
```

4) Choose your local routing method
- Option A: kubefwd (recommended when you want to use service names)
  ```bash
  sudo kubefwd services -n cube-js cube-js
  # Keep this window running; verify hostnames were added:
  sudo grep -i cube-js /etc/hosts
  ```
  Use host `cube-js` in your DB URL.

- Option B: plain kubectl port-forward (simple localhost)
  ```bash
  kubectl -n cube-js port-forward svc/cube-js 5432:5432
  ```
  Use host `localhost` in your DB URL.

5) Configure Streamlit secrets for Cube SQL
- The username/password must match your Cube SQL settings (often user `cube` and password is the Cube API secret). If your password has special characters, URL-encode it.
- kubefwd host (service name):
  ```toml
  [connections.cube]
  type = "sql"
  url = "postgresql+psycopg2://<user>:<urlencoded_password>@cube-js:5432/cube?sslmode=prefer"
  ```
- port-forward host (localhost):
  ```toml
  [connections.cube]
  type = "sql"
  url = "postgresql+psycopg2://<user>:<urlencoded_password>@localhost:5432/cube?sslmode=prefer"
  ```
- Restart Streamlit after editing `.streamlit/secrets.toml`.

6) Sanity-check connectivity
```bash
# Host reachability
nc -vz cube-js 5432        # or localhost if port-forwarding

# DB handshake with same creds as secrets, if you need nonproduction credentials then hit up Isaac or Data Engeineering. This set can be bypassed if there is 
# psql will securely prompt for the password
psql -h cube-js -p 5432 -U <user> -d cube -c "select 1"
```

Password handling for psql
- psql does NOT read `.streamlit/secrets.toml`; it will prompt for the password securely.
- Optional (to avoid interactive prompts): use a `.pgpass` file.
  ```bash
  echo "cube-js:5432:cube:<user>:<password>" >> ~/.pgpass
  chmod 600 ~/.pgpass
  # then you can run without an interactive prompt:
  psql -h cube-js -p 5432 -U <user> -d cube -c "select 1"
  ```

7) Query from the app
- Use the existing utility with `db="cube"`:
  ```python
  df = db_util.query("select 1 as ok", db="cube", ttl=60)
  ```

Troubleshooting
- SSO token expired:
  ```bash
  AWS_PROFILE=nonproduction aws sso login
  AWS_PROFILE=nonproduction aws eks --region us-east-1 update-kubeconfig --name nonproduction-us-east-1-a
  # restart kubefwd or port-forward
  ```
- DNS doesn’t resolve:
  - Ensure kubefwd is running with sudo and not closed
  - Check `/etc/hosts` for `cube-js` entries
- Connection refused:
  - Forwarder died; restart kubefwd/port-forward
  - Confirm service exposes port 5432:
    ```bash
    kubectl -n cube-js get svc cube-js -o wide
    ```
- Password authentication failed:
  - Wrong Cube SQL user/password or database
  - Use the Cube SQL user (often `cube`), not a Postgres system user
  - URL-encode password in the connection URL

### Quick Restart After It’s Already Set Up
If you’ve already configured your SSO profile and forwarding, use these quick steps next time:

1) Refresh AWS SSO and kube context
```bash
export AWS_PROFILE=nonproduction
aws sso login
aws eks --region us-east-1 update-kubeconfig --name nonproduction-us-east-1-a
```

2) Start forwarding (pick ONE)
- kubefwd (recommended for service DNS and testing in against nonproduction):
  ```bash
  sudo kubefwd services -n cube-js cube-js
  ```
- OR plain port-forward (localhost):
  ```bash
  kubectl -n cube-js port-forward svc/cube-js 5432:5432
  ```

3) Verify connectivity
```bash
sudo grep -i cube-js /etc/hosts   # should show entries if kubefwd
nc -vz cube-js 5432               # or localhost if port-forwarding
```

4) Run the app
- Ensure `.streamlit/secrets.toml` points to:
  - `cube-js` with kubefwd, or
  - `localhost` with port-forward.
- Restart Streamlit to reload secrets.


### Examples of Implementation
1) Use the same pattern as Redshift/Postgres:
- Define the SQL in a model function (accept filter params as needed).
- Call the function with `db="cube"` (or set `database="cube"` inside it).

'''
def cube_test(start_date: datetime, end_date: datetime, db: str = None, database: str = None)-> pd.DataFrame:
    query = f""" 
        select 
            * 
        from order_transactions 
        where opd_provision_start_date between :start_date and :end_date
    
    """
    df = db_util.query(
            query, 
            params={"start_date": start_date, "end_date": end_date},
            db=db if db is not None else database, 
            ttl=60
        )
    return df
'''

2) Display on a page
- Import the model function into the page (e.g., `from models import cube_test`).
- Call it with the required params; wrap the render in `@st.fragment` and guard with input checks so it doesn’t run on page load.
- Confirm the DataFrame or visualization renders.

'''

@st.fragment
def render_cube_test(start_date, end_date):
    cube_test_df = cube_test(start_date=start_date, end_date=end_date, db="cube")
    cube_test_df_st = st.dataframe(cube_test_df)
    return cube_test_df_st

'''

''' 
with tab5:
    st.markdown("""
        #### Cube Test
        This section tests the cube test function.
    """, unsafe_allow_html=True)
    st.divider()
    if start_date and end_date and tab5.active:
        render_cube_test(start_date, end_date)
    else:
        st.error("Please select a start date to view the cube test")

'''

### Testing with a local cube 

When developing locally, you can test against a local Cube.js instance running in Docker from the cube-js repository.

#### Prerequisites

- Docker and Docker Compose installed
- Access to the cube-js repository
- Navigate to the cube-js repository directory

#### Steps to Start and Verify Local Cube.js

1. **Start the Cube.js container:**

```bash
docker compose up -d
```

This starts the Cube.js service in detached mode.

2. **Wait for the service to initialize:**

```bash
sleep 8
```

Give the container time to fully start up and initialize all services.

3. **Verify the service is ready:**

```bash
curl -sI http://localhost:4000/ready
```

Expected output: `200 OK` status in the response headers. This confirms the Cube.js API is ready to accept requests.

4. **Verify database credentials are configured:**

```bash
docker exec -it cube-js-cube-1 sh -lc 'echo "$CUBEJS_DB_USER"; [ -n "$CUBEJS_DB_PASS" ] && echo PASS_SET || echo NO_PASS'
```

This command checks:
- The database username is set (`CUBEJS_DB_USER`)
- The database password is configured (shows `PASS_SET` if present, `NO_PASS` if missing)

#### Quick Verification Script

You can run all verification steps in one go:

```bash
docker compose up -d && \
sleep 8 && \
curl -sI http://localhost:4000/ready && \
docker exec -it cube-js-cube-1 sh -lc 'echo "$CUBEJS_DB_USER"; [ -n "$CUBEJS_DB_PASS" ] && echo PASS_SET || echo NO_PASS'
```

#### Connecting from Streamlit

Once your local Cube.js instance is running and verified, update your `.streamlit/secrets.toml` to connect directly to the Cube.js PostgreSQL database:

```
[connections.cube]
type = "sql"
url = "postgresql+psycopg2://cube-js:(nonproduction password)@localhost:5432/cube?sslmode=disable"
```

**Note:** Replace `(nonproduction password)` with the actual password from your local Cube.js setup. This connects Streamlit directly to the Cube.js database on port 5432, not the Cube.js API endpoint.

#### Troubleshooting

- **Container not starting:** Check Docker logs with `docker compose logs -f`
- **Ready endpoint returns error:** Ensure port 4000 is not in use by another service
- **Database credentials missing:** Check your `.env` file in the cube-js repository for `CUBEJS_DB_USER` and `CUBEJS_DB_PASS`
- **Connection refused from Streamlit:** Verify the Cube.js container is running with `docker ps`

