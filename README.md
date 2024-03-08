
# parser_base

Сервер, объединяющий онлайн парсеры, занимающиеся добрым делом.


## Запуск сервера

Загрузка с гитхаба

```bash
  git clone https://github.com/e32885717/parser_base
```

Вход в директорию

```bash
  cd parser_base
```

Установка зависимостей

```bash
  pip install -r requirements.txt
```

Создание стандартного пользователя

```bash
  python create_user.py -d
```

Запуск сервера

```bash
  python main.py
```
## Как вписать сервер в парсер?

В `config.py` в пункте `api_url` установить путь к вашему серверу. Если сервер запущен на том же компьютере, что и парсер, и вы поставили дефолтные логин и пароль, то строчками ниже замените соответствующие в файле `config.py` парсера.

```python
api_url = "http://127.0.0.1:7000"
login = "public"
password = "public"
```

## Как добавлять пользователей?

Выполните: 
```bash
  python create_user.py
```
## Описание API

### Авторизация

```http
  GET /auth
```
Логин и пароль передаются через HTTP Basic Auth

В ответе:
| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `ok`      | `boolean`| Успех или нет                  |
| `token`   | `string` | Временный токен                |
| `version` | `int`    | Версия сервера                 |
| `desc`    | `string` | Описание ошибки если ok=false  |

### Получение свободной задачи

```http
  GET /getFreeTask
```
**Получает никем не занятую задачу для парсинга**

В ответе - данные задачи

### Приват задачи

```http
  GET /privateTask
```
**Делает задачу заприваченной, другие пользователи не смогут получить ее**

Параметры запроса:

| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `token`   | `string` | Временный токен                |
| `task_id` | `string` | ID задачи                      |

В ответе:
| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `ok`      | `boolean`| Успех или нет                  |
| `desc`    | `string` | Описание ошибки если ok=false  |

### Пинг задачи

```http
  GET /pingTask
```
**Если задача была давно (2 минуты) запривачена и до сих пор не закончена, то она может расприватиться. Чтобы такого не происходило, задачу надо иногда обновлять, для этого и есть этот запрос**

Параметры запроса:

| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `token`   | `string` | Временный токен                |
| `task_id` | `string` | ID задачи                      |

В ответе:
| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `ok`      | `boolean`| Успех или нет                  |
| `desc`    | `string` | Описание ошибки если ok=false  |

### Закрытие задачи

```http
  POST /closeTask
```
**Закрывает задачу, загружает сети в базу**

Параметры запроса:

| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `token`   | `string` | Временный токен                |
| `task_id` | `string` | ID задачи                      |
| `result`   | `string`| Массив данных сетей            |

В ответе:
| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `ok`      | `boolean`| Успех или нет                  |
| `desc`    | `string` | Описание ошибки если ok=false  |

### Анонимная загрузка сетей

```http
  POST /anonymousUpload
```
**Загружает сети, не привязанные к задаче, в базу**

Параметры запроса:

| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `result`   | `string`| Массив данных сетей            |

В ответе:
| Parameter | Type     | Description                    |
| :-------- | :------- | :----------------------------- |
| `ok`      | `boolean`| Успех или нет                  |
| `desc`    | `string` | Описание ошибки если ok=false  |

### Статистика

```http
  GET /stats
```
**Получает статистику, обновляется раз в 10 секунд**

В ответе - статистика
