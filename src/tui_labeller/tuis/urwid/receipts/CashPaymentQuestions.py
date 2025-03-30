class CashPaymentQuestions:
    def __init__(self):
        self.questions = [
            InputValidationQuestionData(
                caption="Amount paid in cash: ",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
            InputValidationQuestionData(
                caption="Change returned (cash): ",
                input_type=InputType.FLOAT,
                ans_required=True,
                ai_suggestions=[],
                history_suggestions=[],
            ),
        ]
