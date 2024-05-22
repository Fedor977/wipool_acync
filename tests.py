import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime
from core import process_messages, should_cancel_message, send_message, User


class TestProcessMessages(unittest.IsolatedAsyncioTestCase):
    async def test_process_messages(self):
        user1 = User(id=1, created_at=datetime.utcnow(), status='alive', status_updated_at=datetime.utcnow())
        session_mock = MagicMock()
        session_mock.query.return_value.filter.return_value.all.return_value = [user1]

        with patch('my_module.session', session_mock), \
                patch('my_module.should_cancel_message', return_value=False), \
                patch('my_module.send_message') as send_message_mock:
            await process_messages()

            # Проверяем, что функция send_message вызывалась дважды (для первого и второго сообщения)
            self.assertEqual(send_message_mock.call_count, 2)

    async def test_should_cancel_message(self):
        user_mock = MagicMock()
        user_mock.id = 1

        # Подготовим сообщения пользователя для теста
        user_messages = ["Привет, как дела?", "Это сообщение содержит слово 'прекрасно'", "Пока"]
        with patch('my_module.get_user_messages', return_value=user_messages):
            # Проверим, что функция должна вернуть True, так как в сообщениях есть ключевое слово
            self.assertTrue(await should_cancel_message(user_mock))

    async def test_send_message(self):
        user_mock = MagicMock()
        user_mock.id = 1

        # Проверим, что при успешной отправке сообщения функция должна вывести сообщение в консоль
        with patch('my_module.app.send_message') as send_message_mock:
            await send_message(user_mock, "Тестовое сообщение")
            send_message_mock.assert_called_once_with(user_mock.id, "Тестовое сообщение")


if __name__ == '__main__':
    unittest.main()
