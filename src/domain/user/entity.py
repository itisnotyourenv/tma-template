from dataclasses import dataclass

from .vo import UserId, FirstName, LastName, Username, Bio


@dataclass
class User:
    id: UserId
    first_name: FirstName
    last_name: LastName | None
    username: Username
    bio: Bio | None
