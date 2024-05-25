import requests
from creds import get_creds
iam_token, folder_id = get_creds()
def text_to_speech(data):
    # iam_token, folder_id для доступа к Yandex SpeechKit
    # Указываем параметры запроса
    params = "&".join([
        "topic=general",  # используем основную версию модели
        f"folderId={folder_id}",
        "lang=ru-RU"  # распознаём голосовое сообщение на русском язык
    ])
    # Аутентификация через IAM-токен
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
        # Выполняем запрос
    response = requests.post(
            f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}",
        headers=headers, 
        data=data
    )
    # Читаем json в словарь
    decoded_data = response.json()
    # Проверяем, не произошла ли ошибка при запросе

    if decoded_data.get("error_code") is None:
        return True, decoded_data.get("result")  # Возвращаем статус и текст из аудио
    else:
        return False, "При запросе в SpeechKit возникла ошибка" 