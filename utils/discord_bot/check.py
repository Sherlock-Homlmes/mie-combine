from discord import Interaction


def is_admin(interaction: Interaction) -> bool:
    """Check if user has admin role."""
    from core.conf.bot.conf import server_info

    return interaction.user.get_role(server_info.role_ids.admin) is not None
