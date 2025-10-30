import requests

BASE_URL = "http://localhost:8000"

def print_response(response):
    print(f"Status code: {response.status_code}")
    try:
        print("Response JSON:")
        print(response.json())
    except requests.exceptions.RequestException:
        print("Response text:")
        print(response.text)
    print("="*50)

def main():
    # 1. Регистрация пользователя
    print("1. Register user")
    user_data = {"email": "user@example.com", "password": "password123"}
    r = requests.post(f"{BASE_URL}/user", json=user_data)
    print_response(r)
    if r.status_code != 200:
        return
    user_id = r.json()["id"]

    # 2. Логин (получение токена)
    print("2. Login user")
    r = requests.post(f"{BASE_URL}/login", json=user_data)
    print_response(r)
    if r.status_code != 200:
        return
    token = r.json()["access_token"]
    headers = {"x-token": token}

    # 3. Получение своего пользователя (GET /user/{user_id})
    print("3. Get user info")
    r = requests.get(f"{BASE_URL}/user/{user_id}", headers=headers)
    print_response(r)

    # 4. Создание объявления
    print("4. Create advertisement")
    ad_data = {"title": "Bike for sale", "description": "Almost new"}
    r = requests.post(f"{BASE_URL}/advertisement", json=ad_data, headers=headers)
    print_response(r)
    if r.status_code != 200:
        return
    ad_id = r.json()["id"]

    # 5. Получение объявления (GET)
    print("5. Get advertisement by ID")
    r = requests.get(f"{BASE_URL}/advertisement/{ad_id}")
    print_response(r)

    # 6. Обновление объявления (PATCH)
    print("6. Update advertisement")
    ad_update = {"title": "Updated Bike Title", "description": "Updated description"}
    r = requests.patch(f"{BASE_URL}/advertisement/{ad_id}", json=ad_update, headers=headers)
    print_response(r)

    # 7. Поиск объявлений (GET с параметром search)
    print("7. Search advertisements")
    r = requests.get(f"{BASE_URL}/advertisement", params={"search": "Bike"})
    print_response(r)

    # 8. Удаление объявления (DELETE)
    print("8. Delete advertisement")
    r = requests.delete(f"{BASE_URL}/advertisement/{ad_id}", headers=headers)
    print_response(r)

    # 9. Обновление пользователя (PATCH /user/{user_id})
    print("9. Update user")
    user_update = {"email": "newemail@example.com", "password": "newpassword123"}
    r = requests.patch(f"{BASE_URL}/user/{user_id}", json=user_update, headers=headers)
    print_response(r)

    # 10. Удаление пользователя (DELETE /user/{user_id})
    print("10. Delete user")
    r = requests.delete(f"{BASE_URL}/user/{user_id}", headers=headers)
    print_response(r)


if __name__ == "__main__":
    main()
