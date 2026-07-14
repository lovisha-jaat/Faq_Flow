class User:
    """
    User Model
    Represents a company employee/admin.
    """

    def __init__(
        self,
        id=None,
        name="",
        email="",
        password="",
        company_id=None,
        created_at=None
    ):
        self.id = id
        self.name = name
        self.email = email
        self.password = password
        self.company_id = company_id
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "company_id": self.company_id,
            "created_at": self.created_at
        }