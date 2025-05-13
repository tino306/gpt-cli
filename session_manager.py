import json
import os
# from uuid import uuid4

SESSIONSDIR = os.path.join(os.path.expanduser("~"), ".gpt", "sessions")
UUID_NAME_MAP = os.path.join(SESSIONSDIR, "uuid_name_map.json")
NAME_UUID_MAP= os.path.join(SESSIONSDIR, "name_uuid_map.json")

class SessionManager:
    def __init__(self):
        if not os.path.exists(SESSIONSDIR):
            os.makedirs(SESSIONSDIR)
        self.session_file: str = ""
        # self.uuid_name_map: dict[str, str] = {}
        # self.name_uuid_map: dict[str, str] = {}

    # def get_uuid(self, name: str) -> str:
    #
    #     return self.name_uuid_map[name]
    #
    # def get_name(self, uuid: str) -> str:
    #
    #     return self.uuid_name_map[uuid]
    #
    # def save_maps(self):
    #     with open(UUID_NAME_MAP, 'w') as file:
    #         json.dump(self.uuid_name_map, file)
    #     with open(NAME_UUID_MAP, 'w') as file:
    #         json.dump(self.name_uuid_map, file)
    #
    # def load_maps(self):
    #     sessions = self.get_session_list()
    #     for session in sessions:
    #         if session not in self.name_uuid_map.keys():
    #             uuid = str(uuid4())
    #             self.name_uuid_map.update({session: uuid})
    #             self.uuid_name_map.update({uuid: session})
    #     if not os.path.isfile(UUID_NAME_MAP):
    #         with open(UUID_NAME_MAP, 'w') as file:
    #             json.dump(self.uuid_name_map, file)
    #     else:
    #         with open(UUID_NAME_MAP, 'r') as file:
    #             self.uuid_name_map.update(json.load(file))
    #     if not os.path.isfile(NAME_UUID_MAP):
    #         with open(NAME_UUID_MAP, 'w') as file:
    #             json.dump(self.name_uuid_map, file)
    #     else:
    #         with open(NAME_UUID_MAP, 'r') as file:
    #             self.name_uuid_map.update(json.load(file))

    def save_session(self, messages: list[dict[str, str]], name: str):
        if not os.path.exists(SESSIONSDIR):
            os.makedirs(SESSIONSDIR)
        sessionfile = os.path.join(SESSIONSDIR, name)
        with open(sessionfile, 'w') as file:
            json.dump(messages, file)
        if self.session_file != "":
            os.remove(self.session_file)
            self.session_file = ""
        print("session '{}' saved".format(name)) 

    def load_session(self, filename: str):
        sessionfile = os.path.join(SESSIONSDIR, filename)
        if os.path.isfile(sessionfile):
            self.session_file = sessionfile
            with open(sessionfile, 'r') as file:
                return json.load(file)
        else:
            print("invalid session filename '{}'\n".format(filename))

    def get_session_list(self) -> list[str]:

        return os.listdir(SESSIONSDIR)
