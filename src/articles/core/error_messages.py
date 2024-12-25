from enum import Enum


class ErrorMessages(Enum):
    NOT_FOUND = "Entity Not Found"
    NOT_AUTHORIZED_TO_MODIFY = "Not Authorized to Modify"
    USERNAME_ALREADY_EXISTS = "Username Already Exists"
    INVALID_ACCESS_TOKEN = "Invalid Access Token"
    NOT_AUTHORIZED = "Not Authorized"
