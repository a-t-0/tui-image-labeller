class ReceiptQuestionnaire:
    def __init__(self, parent_date: datetime):
        self.parent_date = parent_date
        self.base_questions = self.create_base_questions()
        self.verify_unique_questions(self.base_questions)

    def create_base_questions(self):
        return [
            InputValidationQuestionData(
                caption="Receipt owner address (optional): ",
                input_type=InputType.LETTERS,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Shop name: ",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Shop address: ",
                input_type=InputType.LETTERS,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Subtotal (Optional, press enter to skip): ",
                input_type=InputType.FLOAT,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Total tax (Optional, press enter to skip): ",
                input_type=InputType.FLOAT,
                ans_required=False,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Payed total:",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            MultipleChoiceQuestionData(
                question="Transaction type",
                choices=[pt.value for pt in PaymentTypes],
                ai_suggestions=[
                    AISuggestion(PaymentTypes.CASH.value, 0.99, "ReadAI"),
                    AISuggestion(PaymentTypes.CARD.value, 0.1, "SomeAI"),
                    AISuggestion(PaymentTypes.BOTH.value, 0.97, "AnotherAI"),
                ],
            ),
        ]

    def verify_unique_questions(self, questions):
        seen = set()
        for q in questions:
            caption = getattr(q, "caption", getattr(q, "question", None))
            if caption is None:
                raise ValueError("Question object missing caption/question")
            if caption in seen:
                raise ValueError(f"Duplicate question caption: '{caption}'")
            seen.add(caption)
