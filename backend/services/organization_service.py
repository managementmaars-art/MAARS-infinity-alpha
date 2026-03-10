"""Organization Service — Multi-tenancy, teams, and org management."""
from datetime import datetime, timezone
from bson import ObjectId
from db import db


async def create_organization(user_id, data):
    """Create a new organization/workspace."""
    now = datetime.now(timezone.utc).isoformat()
    org = {
        "org_id": f"org_{ObjectId()}",
        "name": data.get("name", "My Organization"),
        "slug": data.get("slug", "").lower().replace(" ", "-"),
        "owner_id": user_id,
        "members": [{"user_id": user_id, "role": "owner", "joined_at": now}],
        "settings": {
            "max_members": data.get("max_members", 25),
            "shared_agents": True,
            "shared_campaigns": True,
            "shared_integrations": True,
        },
        "created_at": now,
        "updated_at": now,
    }
    await db.organizations.insert_one(org)
    org.pop("_id", None)
    await db.users.update_one({"user_id": user_id}, {"$set": {"org_id": org["org_id"]}})
    return org


async def get_organization(user_id):
    """Get user's organization."""
    user = await db.users.find_one({"user_id": user_id}, {"_id": 0, "org_id": 1})
    if not user or not user.get("org_id"):
        return None
    return await db.organizations.find_one({"org_id": user["org_id"]}, {"_id": 0})


async def invite_member(user_id, org_id, invite_data):
    """Invite a member to the organization."""
    org = await db.organizations.find_one({"org_id": org_id, "owner_id": user_id}, {"_id": 0})
    if not org:
        return None

    now = datetime.now(timezone.utc).isoformat()
    invite = {
        "invite_id": f"inv_{ObjectId()}",
        "org_id": org_id,
        "org_name": org["name"],
        "email": invite_data.get("email"),
        "role": invite_data.get("role", "member"),
        "invited_by": user_id,
        "status": "pending",
        "created_at": now,
    }
    await db.org_invites.insert_one(invite)
    invite.pop("_id", None)
    return invite


async def get_org_members(user_id):
    """Get organization members."""
    org = await get_organization(user_id)
    if not org:
        return []
    return org.get("members", [])


async def update_member_role(user_id, org_id, target_user_id, new_role):
    """Update a member's role in the organization."""
    await db.organizations.update_one(
        {"org_id": org_id, "owner_id": user_id, "members.user_id": target_user_id},
        {"$set": {"members.$.role": new_role}}
    )
    return await get_organization(user_id)


async def remove_member(user_id, org_id, target_user_id):
    """Remove a member from the organization."""
    await db.organizations.update_one(
        {"org_id": org_id, "owner_id": user_id},
        {"$pull": {"members": {"user_id": target_user_id}}}
    )
    await db.users.update_one({"user_id": target_user_id}, {"$unset": {"org_id": ""}})
    return True
