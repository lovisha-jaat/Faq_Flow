class FAQ:
    """
    FAQ Model
    Stores company FAQs.
    """

    def __init__(
        self,
        id=None,
        company_id=None,
        question="",
        answer="",
        category="",
        created_at=None
    ):
        self.id = id
        self.company_id = company_id
        self.question = question
        self.answer = answer
        self.category = category
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "created_at": self.created_at
        }