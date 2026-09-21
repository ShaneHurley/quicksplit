"""Profile CRUD + unlock + theme."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.profile import Profile, ProfileSettings
from app.schemas.profile import (
    ProfileCreate,
    ProfileRead,
    ProfileSettingsRead,
    ProfileSettingsUpdate,
    ProfileUnlock,
    ProfileUpdate,
)
from app.services.passwords import hash_password, verify_password

router = APIRouter(prefix="/profiles", tags=["profiles"])


def _to_read(profile: Profile) -> ProfileRead:
    return ProfileRead(
        id=profile.id,
        display_name=profile.display_name,
        avatar_emoji=profile.avatar_emoji,
        accent_hue=profile.accent_hue,
        theme=profile.theme or "dark",
        has_password=bool(profile.password_hash),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        settings=ProfileSettingsRead.model_validate(profile.settings)
        if profile.settings
        else None,
    )


@router.get("", response_model=list[ProfileRead])
def list_profiles(db: Session = Depends(get_db)) -> list[ProfileRead]:
    rows = db.query(Profile).order_by(Profile.created_at.asc()).all()
    return [_to_read(p) for p in rows]


@router.post("", response_model=ProfileRead, status_code=201)
def create_profile(body: ProfileCreate, db: Session = Depends(get_db)) -> ProfileRead:
    profile = Profile(
        display_name=body.display_name.strip(),
        accent_hue=body.accent_hue,
        avatar_emoji=body.avatar_emoji,
        theme=body.theme,
        password_hash=hash_password(body.password) if body.password else None,
    )
    profile.settings = ProfileSettings()
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return _to_read(profile)


@router.post("/{profile_id}/unlock", response_model=ProfileRead)
def unlock_profile(
    profile_id: str, body: ProfileUnlock, db: Session = Depends(get_db)
) -> ProfileRead:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(404, "Profile not found")
    if not profile.password_hash:
        return _to_read(profile)
    if not verify_password(body.password, profile.password_hash):
        raise HTTPException(401, "Incorrect password")
    return _to_read(profile)


@router.patch("/{profile_id}", response_model=ProfileRead)
def update_profile(
    profile_id: str, body: ProfileUpdate, db: Session = Depends(get_db)
) -> ProfileRead:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(404, "Profile not found")
    data = body.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    for k, v in data.items():
        setattr(profile, k, v)
    if password is not None:
        profile.password_hash = hash_password(password) if password else None
    db.commit()
    db.refresh(profile)
    return _to_read(profile)


@router.delete("/{profile_id}", status_code=204)
def delete_profile(profile_id: str, db: Session = Depends(get_db)) -> None:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(404, "Profile not found")
    db.delete(profile)
    db.commit()


@router.get("/{profile_id}/settings", response_model=ProfileSettingsRead)
def get_settings(profile_id: str, db: Session = Depends(get_db)) -> ProfileSettings:
    profile = db.get(Profile, profile_id)
    if profile is None or profile.settings is None:
        raise HTTPException(404, "Settings not found")
    return profile.settings


@router.patch("/{profile_id}/settings", response_model=ProfileSettingsRead)
def patch_settings(
    profile_id: str, body: ProfileSettingsUpdate, db: Session = Depends(get_db)
) -> ProfileSettings:
    profile = db.get(Profile, profile_id)
    if profile is None or profile.settings is None:
        raise HTTPException(404, "Settings not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(profile.settings, k, v)
    db.commit()
    db.refresh(profile.settings)
    return profile.settings
