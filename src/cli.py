"""src/cli.py."""

import asyncio
import logging
import click
from src.apps.auth.schemas import UserCreateBase
from src.apps.users.models import UserRole
from src.apps.users.repositories.user_profile import UserRepository
from src.core.security.password import PasswordHandler
from src.infrastructure.database.setup import async_session_factory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """Command line utilities for Swipe Real Estate API."""


@cli.command()
@click.option("--email", default="moderator@moderator.com", help="Moderator email")
@click.option("--password", default="moderator", help="Moderator password")
@click.option("--phone", default="+80009998877", help="Moderator phone")
def create_moderator(email, password, phone):
    """
    Creates a default moderator (or administrator).
    """

    async def _run():
        async with async_session_factory() as session:
            user_repo = UserRepository(session)

            # Check existence
            if await user_repo.get_by_email(email):
                click.echo(f"User with email {email} already exists.")
                return

            click.echo(f"Creating moderator {email}...")

            try:
                user_data = UserCreateBase(
                    email=email,
                    password=password,
                    first_name="System",
                    last_name="Moderator",
                    phone=phone,
                )

                hashed_password = PasswordHandler.get_password_hash(password)

                await user_repo.create_user(
                    data=user_data,
                    hashed_password=hashed_password,
                    role=UserRole.MODERATOR,
                )
                await session.commit()
                click.echo(click.style("Moderator created successfully!", fg="green"))

            except Exception as e:  # pylint: disable=broad-exception-caught
                click.echo(click.style(f"Failed to create moderator: {e}", fg="red"))

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
