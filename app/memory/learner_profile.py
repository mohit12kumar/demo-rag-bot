from sqlalchemy.orm import Session

from app.database.models import (
    QuizResult,
    LearningMemory
)


class LearnerProfile:

    def __init__(self, db: Session):
        self.db = db

    def get_quiz_history(
        self,
        user_id: int
    ):

        return (
            self.db.query(QuizResult)
            .filter(
                QuizResult.user_id == user_id
            )
            .all()
        )

    def get_average_score(
        self,
        user_id: int
    ):

        quizzes = (
            self.db.query(QuizResult)
            .filter(
                QuizResult.user_id == user_id
            )
            .all()
        )

        if not quizzes:
            return 0

        total = sum(
            quiz.score
            for quiz in quizzes
        )

        return round(
            total / len(quizzes),
            2
        )

    def get_learning_progress(
        self,
        user_id: int
    ):

        memories = (
            self.db.query(LearningMemory)
            .filter(
                LearningMemory.user_id == user_id
            )
            .all()
        )

        return [
            {
                "topic": memory.topic,
                "mastery": memory.mastery_level,
                "confidence": memory.confidence_score
            }
            for memory in memories
        ]

    def get_dashboard(
        self,
        user_id: int
    ):

        return {
            "average_score":
                self.get_average_score(user_id),

            "progress":
                self.get_learning_progress(user_id),

            "quiz_attempts":
                len(
                    self.get_quiz_history(user_id)
                )
        }