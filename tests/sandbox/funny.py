import requests


def get_available_cur_pool() -> None:
    curs = requests.get("https://api.frankfurter.dev/v1/currencies").json()
    print(curs.keys())


if __name__ == "__main__":
    get_available_cur_pool()
