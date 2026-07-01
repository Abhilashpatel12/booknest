from sqlalchemy.orm import Session
from app.models.activity import Activity

def log_activity(db: Session, user_id: int, action_type: str, description: str):
    
    new_activity = Activity(
        user_id=user_id,
        action_type=action_type,
        description=description
    )
    db.add(new_activity)
    db.commit()

    from app.api.websockets import manager
    import asyncio
    
    message = {
        "action_type": action_type,
        "description": description
    }
    
    manager.send_personal_message_sync(message, user_id)
