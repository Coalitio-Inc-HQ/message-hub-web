from core import ChatDTO


class TestData:
    def __init__(self):
        self.test_waiting_chats = [
            ChatDTO(id=1, name="1"),
            ChatDTO(id=2, name="2"),
            ChatDTO(id=3, name="3"),
            ChatDTO(id=4, name="4")
        ]
        self.test_waiting_chats_dict = [
            chat.model_dump() for chat in self.test_waiting_chats
        ]
        self.wrong_type_test_waiting_chats_dict = [
            {'chat_id': 1, 'chat_name': '1'},
            {'chat_id': 2, 'chat_name': '2'},
            {'chat_id': 3, 'chat_name': '3'},
            {'chat_id': 4, 'chat_name': '4'}
        ]
        self.test_user_chats = [
            ChatDTO(id=55, name="fff"),
            ChatDTO(id=6, name="fgsdfg")
        ]
