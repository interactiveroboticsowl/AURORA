import logging

from ..utils.kubernetes import (    
    cleanup_participation,    
    create_user_participation_object,
)

logging.basicConfig(level=logging.INFO)


async def deploy_task(survey_name: str, user_id: str):
    deployment_successful = await create_user_participation_object(survey_name, user_id)

    if not deployment_successful:
        logging.error(
            f"Creation of participation for {user_id} in {survey_name} failed"
        )
        return

    logging.info(f"Creation of participation of {user_id} in {survey_name} successful!")


async def cleanup_task(user_id: str, survey_name: str):
    cleanup_successful = await cleanup_participation(user_id, survey_name)

    if not cleanup_successful:
        logging.error(f"Cleanup for session {user_id} failed")
        return

    logging.info(f"Cleanup for session {user_id} successful!")
