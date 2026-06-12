from sqlalchemy.orm import Session

from app.database.models import LearningMemory


class HolographicMemory:

    def __init__(self, db: Session):
        self.db = db

    def save_memory(
        self,
        user_id: int,
        topic: str,
        mastery_level: float,
        confidence_score: float
    ):

        memory = LearningMemory(
            user_id=user_id,
            topic=topic,
            mastery_level=mastery_level,
            confidence_score=confidence_score
        )

        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)

        return memory

    def get_user_memory(
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

        return memories

    def get_weak_topics(
        self,
        user_id: int
    ):

        weak_topics = (
            self.db.query(LearningMemory)
            .filter(
                LearningMemory.user_id == user_id,
                LearningMemory.mastery_level < 70
            )
            .all()
        )

        return weak_topics

    def update_mastery(
        self,
        memory_id: int,
        mastery_level: float
    ):

        memory = (
            self.db.query(LearningMemory)
            .filter(
                LearningMemory.id == memory_id
            )
            .first()
        )

        if memory:

            memory.mastery_level = mastery_level

            self.db.commit()

            self.db.refresh(memory)

        return memory