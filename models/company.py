class Company:
    """
    Company Model
    Stores company details.
    """

    def __init__(
        self,
        id=None,
        company_name="",
        website="",
        description="",
        created_at=None
    ):
        self.id = id
        self.company_name = company_name
        self.website = website
        self.description = description
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "company_name": self.company_name,
            "website": self.website,
            "description": self.description,
            "created_at": self.created_at
        }