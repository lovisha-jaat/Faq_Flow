class Query:
    """
    Query Model
    Stores chatbot conversations.
    """

    def __init__(
        self,
        id=None,
        company_id=None,
        user_question="",
        bot_answer="",
        status="",
        created_at=None
    ):
        self.id = id
        self.company_id = company_id
        self.user_question = user_question
        self.bot_answer = bot_answer
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "user_question": self.user_question,
            "bot_answer": self.bot_answer,
            "status": self.status,
            "created_at": self.created_at
        }