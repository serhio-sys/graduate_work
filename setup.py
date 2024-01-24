"""import os"""
import os


if __name__ == "__main__":
    os.system("python manage.py loaddata data/data.json")
    os.system("python manage.py loaddata data/dungeon_data.json")
    os.system("python manage.py loaddata data/effects_data.json")
