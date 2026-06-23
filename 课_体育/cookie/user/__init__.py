class User:
    def __init__(self, user_name="2025061020000219", user_pwd="060916Ljj"):
        self.__user_name = user_name
        self.__user_pwd = user_pwd

    @property
    def user_name(self):
        return self.__user_name

    @user_name.setter
    def user_name(self, value):
        self.__user_name = value

    @property
    def user_pwd(self):
        return self.__user_pwd

    @user_pwd.setter
    def user_pwd(self, value):
        self.__user_pwd = value

    def __repr__(self):
        return f"User(user_name={self.__user_name!r})"
