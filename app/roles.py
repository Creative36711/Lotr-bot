from collections import namedtuple
from typing import Optional, Set, List
import logging
from disnake.guild import Member


CONTENT_CREATOR_ROLE = 1369337199644119101
DEVELOPER_ROLE = 1375182529388085328


MAIN_ROLES = {
    CONTENT_CREATOR_ROLE,
    DEVELOPER_ROLE
}

RewardedRole = namedtuple('RewardedRole', ['role_id', 'min_balance'])

ROLES_REWARDS_BY_WITH_BALANCE = [
    RewardedRole(1375186997261500466, 50),
    RewardedRole(1375186878227284099, 150),
    RewardedRole(1375186534830968853, 300),
    RewardedRole(1375186363611086978, 500),
    RewardedRole(1375186176092143786, 800),
    RewardedRole(1375186051856990218, 1100),
    RewardedRole(1375185664257163284, 1500),
    RewardedRole(1375184067535962133, 1800),
    RewardedRole(1375183723133403228, 2100),
    RewardedRole(1375183112870559775, 2500),
]
REWARDED_ROLES = {x.role_id for x in ROLES_REWARDS_BY_WITH_BALANCE}


logger = logging.getLogger(__name__)


def member_has_main_role(member: Member) -> bool:
    return bool(MAIN_ROLES.intersection({role.id for role in member.roles}))


def get_role_id_member_should_have_if_balance(user_balance: int) -> Optional[int]:
    roles_ids_user_deserves = [x.role_id for x in ROLES_REWARDS_BY_WITH_BALANCE if user_balance >= x.min_balance]
    return roles_ids_user_deserves[-1] if roles_ids_user_deserves else None


async def remove_roles(member: Member, roles_ids: Set[int]) -> str:
    roles_ids_to_remove: Set[int] = roles_ids.intersection({role.id for role in member.roles})
    if roles_ids_to_remove:
        roles_to_remove = [member.guild.get_role(role_id) for role_id in roles_ids_to_remove]
        await member.remove_roles(*roles_to_remove)
        removed_roles_names = ', '.join([role.name for role in roles_to_remove])
        logger.info(member.name + ' теряет роли ' + removed_roles_names)
        return removed_roles_names
    return ''


async def add_roles(member: Member, roles_ids: Set[int]) -> str:
    roles_ids_to_add: Set[int] = roles_ids.difference({role.id for role in member.roles})
    if roles_ids_to_add:
        roles_to_add = [member.guild.get_role(role_id) for role_id in roles_ids_to_add]
        await member.add_roles(*roles_to_add)
        added_roles_names = ', '.join([role.name for role in roles_to_add])
        logger.info(member.name + ' получает роли ' + added_roles_names)
        return added_roles_names
    return ''


async def role_update(member: Member, user_balance: int):
    role_id_member_should_have = get_role_id_member_should_have_if_balance(user_balance)
    if role_id_member_should_have is None:
        await remove_roles(member, REWARDED_ROLES)
    else:
        await remove_roles(member, REWARDED_ROLES.difference({role_id_member_should_have}))
        return await add_roles(member, {role_id_member_should_have})
    return ''
