# -*- coding: utf-8 -*-
from os import getenv
from typing import List

from fastapi import APIRouter
from langsmith import Client
from langsmith.schemas import Run

from app.schemas.message_schema import FeedbackLangchain, FeedbackSourceBaseLangchain, IFeedback

router = APIRouter()


@router.post("/feedback")
async def send_feedback(
    feedback: IFeedback,
) -> FeedbackLangchain:
    """Send feedback to the Langsmith API."""
    client = Client()
    runs: List[Run] = list(
        client.list_runs(
            project_name=getenv("LANGCHAIN_PROJECT"),
            filter=f'has(tags, "message_id={feedback.message_id}")',
            execution_order=1,
        )
    )
    run: Run = runs[0]

    if feedback.previous_id:
        client.delete_feedback(feedback.previous_id)

    feedback_res = client.create_feedback(
        run.id,
        feedback.key,
        score=feedback.score,
        comment=feedback.comment,
        source_info={
            "user": feedback.user,
            "conversation_id": feedback.conversation_id,
            "message_id": feedback.message_id,
            "settings_version": feedback.settings.version if feedback.settings is not None else "N/A",
        },
    )

    feedback_pydanticv2 = FeedbackLangchain(
        **feedback_res.dict(),
        feedback_source=(
            FeedbackSourceBaseLangchain(**feedback_res.feedback_source.dict()) if feedback_res.feedback_source else None
        ),
    )
    return feedback_pydanticv2
