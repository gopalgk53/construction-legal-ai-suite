from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database.dependency import get_db
from schemas.milestone import (
    MilestoneCreate,
    MilestonePatch,
    MilestoneResponse,
    MilestoneUpdate,
)
from services.milestone_service import (
    create_milestone,
    delete_milestone,
    get_milestone_by_id,
    get_milestones,
    patch_milestone,
    update_milestone,
)


router = APIRouter(
    prefix="/projects/{project_id}/milestones",
    tags=["Milestones"],
)


@router.post(
    "",
    response_model=MilestoneResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_milestone_route(
    project_id: int,
    milestone_data: MilestoneCreate,
    db: Session = Depends(get_db),
):
    return create_milestone(
        db,
        project_id,
        milestone_data,
    )


@router.get(
    "",
    response_model=list[MilestoneResponse],
)
def get_milestones_route(
    project_id: int,
    db: Session = Depends(get_db),
):
    return get_milestones(
        db,
        project_id,
    )


@router.get(
    "/{milestone_id}",
    response_model=MilestoneResponse,
)
def get_milestone_route(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
):
    return get_milestone_by_id(
        db,
        project_id,
        milestone_id,
    )


@router.put(
    "/{milestone_id}",
    response_model=MilestoneResponse,
)
def update_milestone_route(
    project_id: int,
    milestone_id: int,
    milestone_data: MilestoneUpdate,
    db: Session = Depends(get_db),
):
    return update_milestone(
        db,
        project_id,
        milestone_id,
        milestone_data,
    )


@router.patch(
    "/{milestone_id}",
    response_model=MilestoneResponse,
)
def patch_milestone_route(
    project_id: int,
    milestone_id: int,
    milestone_data: MilestonePatch,
    db: Session = Depends(get_db),
):
    return patch_milestone(
        db,
        project_id,
        milestone_id,
        milestone_data,
    )


@router.delete("/{milestone_id}")
def delete_milestone_route(
    project_id: int,
    milestone_id: int,
    db: Session = Depends(get_db),
):
    return delete_milestone(
        db,
        project_id,
        milestone_id,
    )