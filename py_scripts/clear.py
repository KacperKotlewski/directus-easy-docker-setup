import platform
import os

isSystemWindows = platform.system() == "Windows"

def clear_docker_containers():
    os.system("docker compose --profile production down --rmi all --volumes")
    
def clear_database_files():
    if("yes" == input("are you sure to delete database? [yes/no]: ")):
        os.system("rmdir /S /Q app_data")
        print("data base is deleted")
    else:
        print("database is save")
    
def clear_scripts():
    os.system("rm -f docker-compose.* .env")
    if isSystemWindows:
        os.system("rm -f run.bat clean.bat build.bat")
    else:
        os.system("rm -f run clean build")
              
if __name__ == "__main__":
    while True:
        options = ["exit", "clear database", "clear docker", "clear scripts", "clear docker & scripts", "clear all"]
        
        for i, option in enumerate(options):
            print(f"{i} - {option}")
        
        i = int(input("your choice: "))
        if (i == 0) :
            quit()
        if (i in [1,5]):
            clear_database_files()
        if (i in [2,4,5]):
            clear_docker_containers()
        if (i in [3,4,5]):
            clear_scripts()