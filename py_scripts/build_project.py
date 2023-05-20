import getpass
import platform
import os

isSystemWindows = platform.system() == "Windows"

def get_user_input(text, list, force_to=None):
    print(text)
    for i in range(len(list)):
        print(str(i) + " - " + list[i])
    if (force_to == None):
        user_input = input()
    else:
        user_input = force_to
    user_input = int(user_input)
    print("you choose: " + list[user_input])
    return user_input

def create_dotEnv(port, email, passwd):
    dotEnv = '''
# port configuration
DIRECTUS_PORT=''' + port + '''

# postgres (database) settings
POSTGRES_DB=directusDB
POSTGRES_USER=directus_user
POSTGRES_PASSWORD=directus_password''' + generateSecret() + '''

# directus settings
DIRECTUS_SECRET=''' + generateSecret() + '''
DIRECTUS_KEY=''' + generateSecret() + '''

# admin user settings
DIRECTUS_ADMIN_EMAIL=''' + email + '''
DIRECTUS_ADMIN_PASSWORD=''' + passwd + '''
'''
    with open("./.env", "w") as file:
        file.write(dotEnv)
        
def create_run_build_files():
    fileContent = "docker compose --env-file ./.env --profile production up -d"
    
    sufix = ".bat" if isSystemWindows else ""
    with open("./run"+sufix, "w") as file:
        file.write(fileContent)
    with open("./build"+sufix, "w") as file:
        file.write(fileContent+" --build")
        
def create_clear_file():
    fileContent = "python ./py_scripts/clear.py"
    
    sufix = ".bat" if isSystemWindows else ""
    with open("./clean"+sufix, "w") as file:
        file.write(fileContent)
        
def create_docker_compose(cache):
    redis_cache = '''
  redis-cache:
    image: redis:6
    networks:
      - directus
    profiles:
      - production''' if cache == 1 else ""
    redis_extend = '''
    depends_on:
      - redis-cache
    environment:
      CACHE_ENABLED: 'true'
      CACHE_STORE: 'redis'
      CACHE_REDIS: 'redis://cache:6379' ''' if cache == 1 else ""

    fileContent = '''
version: '3'
services:
  # --------------------------------------
  # BASE SERVICES
  # --------------------------------------
  postgresql-database:
    image: postgis/postgis:13-master
    volumes:
      - ./app_data/database:/var/lib/postgresql/data
    networks:
      - directus
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    profiles: 
      - production
      - dev
''' + redis_cache + '''

  directus-cms-base:
    image: directus/directus:10
    ports:
      - ${DIRECTUS_PORT}:8055
    volumes:
      - ./app_data/directus/uploads:/directus/uploads
      - ./app_data/directus/extensions:/directus/extensions
      - ./app_data/directus/database:/directus/database
    networks:
      - directus
    depends_on:
      - postgresql-database
    environment:
      #admin user
      ADMIN_EMAIL: ${DIRECTUS_ADMIN_EMAIL}
      ADMIN_PASSWORD: ${DIRECTUS_ADMIN_PASSWORD}
      #secrets
      KEY: ${DIRECTUS_KEY}
      SECRET: ${DIRECTUS_SECRET}

      #database
      DB_CLIENT: 'pg'
      DB_HOST: 'postgresql-database'
      DB_PORT: '5432'
      DB_DATABASE: ${POSTGRES_DB}
      DB_USER: ${POSTGRES_USER}
      DB_PASSWORD: ${POSTGRES_PASSWORD}

      #storage
      STORAGE_LOCATIONS: 'local'
      STORAGE_LOCAL_ROOT: './uploads'

      #app
      TZ: "Europe/Warsaw"
      CORS_ENABLED: true
    restart: unless-stopped
    profiles:
      - norun

  # --------------------------------------
  # PRODUCTION SERVICES
  # --------------------------------------
  directus-prod:
    extends:
      service: directus-cms-base'''+ redis_extend + '''
    profiles:
      - production

networks:
  directus:
'''
    with open("./docker-compose.yml", "w") as file:
        file.write(fileContent)

def generateSecret():
    import random
    import string
    secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(50))
    return secret

if __name__ == "__main__":
    dbs = ["postgreSQL"]
    # db = get_user_input("Select database: ", dbs, 0)
    cache = 0 # cache = get_user_input("Did you want to use DB cache (redis)? ", ["no", "yes"])
    port = input("Directus PORT: ")
    email = input("Admin valid email: ")
    passwd = getpass.getpass("New admin password: ***")
    
    create_dotEnv(port, email, passwd)
    print("env file created")
    create_run_build_files()
    print("run and build files created")
    create_clear_file()
    print("clear file created")
    create_docker_compose(cache)
    print("docker-compose file created")
    
    print("done")
    if (get_user_input("you want to build and run project now?", ["no", "yes"]) == 1):
        if (isSystemWindows):
            os.system("build")
        else:
            os.system("./build")