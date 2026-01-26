import argparse
import asyncio

from sqlalchemy import select

from app.auth import UserManager, password_helper
from app.core.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase


def _default_username(email: str) -> str:
    return email.split("@", 1)[0]


async def _run(args: argparse.Namespace) -> None:
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.email == args.email))
        user = result.scalars().first()

        if user:
            if args.password:
                user.hashed_password = password_helper.hash(args.password)
            if args.username:
                user.username = args.username
            if args.display_name:
                user.display_name = args.display_name
            user.is_superuser = True
            user.is_active = True
            session.add(user)
            await session.commit()
            print(f"Updated superuser: {user.email}")
            return

        if not args.password:
            raise SystemExit("Password is required when creating a new user.")

        username = args.username or _default_username(args.email)
        display_name = args.display_name or username
        user_db = SQLAlchemyUserDatabase(session, User)
        user_manager = UserManager(user_db, password_helper=password_helper)
        user_in = UserCreate(
            email=args.email,
            password=args.password,
            username=username,
            display_name=display_name,
        )
        user = await user_manager.create(user_in, safe=False)
        user.is_superuser = True
        user.is_active = True
        session.add(user)
        await session.commit()
        await session.refresh(user)
        print(f"Created superuser: {user.email}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update a superuser.")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--password", help="User password")
    parser.add_argument("--username", help="Username (optional)")
    parser.add_argument("--display-name", help="Display name (optional)")
    args = parser.parse_args()

    asyncio.run(_run(args))


if __name__ == "__main__":
    main()
