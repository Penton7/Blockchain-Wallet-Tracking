from typing import Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
import json
import time

class Wallets(SQLModel, table=True):
    id: Optional[int] = Field(default=None)
    address: str = Field(primary_key=True)
    chat_ids: str
    last_check: str
    address_name: str

class Jobs(SQLModel, table=True):
    address: str = Field(primary_key=True, foreign_key=Wallets.address)

engine = create_engine("postgresql://postgres:postgres@localhost:5432/wallet")

def edit_last_check(address, last_check):
    with Session(engine) as session:
        statement = select(Wallets).where(Wallets.address == address)
        info = session.exec(statement)
        update_last_check = info.one()
        update_last_check.last_check = last_check
        session.add(update_last_check)
        session.commit()
        session.refresh(update_last_check)
        return "last_check Updated!!!"



def add_address(address, chat_id, last_check):
    with Session(engine) as session:
        already_exist = session.get(Wallets, address)
        if not already_exist:
            list = []
            list.append(chat_id)
            new_address = Wallets(address=address, chat_ids=json.dumps(list), last_check=last_check)
            session.add(new_address)
            session.commit()
            session.get(Jobs, address)
            new_address_job = Jobs(address=address)
            session.add(new_address_job)
            session.commit()
            print("New Address Added! -", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
        else:
            statement = select(Wallets).where(Wallets.address == address)
            info = session.exec(statement)
            check_ids = info.first()
            print(check_ids.chat_ids, )
            old_ids = check_ids.chat_ids
            new_ids = old_ids + [chat_id]
            res = [*set(new_ids)]
            info = session.exec(statement)
            update_address = info.one()
            update_address.chat_ids = json.dumps(res)
            session.add(update_address)
            session.commit()
            session.refresh(update_address)
            print("Address Already Exist! -", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))


def check_1(wallet):
    with Session(engine) as session:
        statement = select(Wallets).where(Wallets.address == wallet)
        info = session.exec(statement).first()
        return json.dumps(info.last_check, sort_keys=True)
def all_from_job():
    with Session(engine) as session:
        statement = select(Jobs.address)
        info = session.exec(statement).all()
        return info
def all_chat_ids(wallet):
    with Session(engine) as session:
        statement = select(Wallets).where(Wallets.address == wallet)
        info = session.exec(statement).first()
        return info.chat_ids
# with Session(engine) as session:
#     statement = select(Wallets).where(Wallets.address == "0xccd2bEcBe9cE4Fb7a45CF7d0DB263c2eC744Fc73")
#     hero = session.exec(statement).first()
#     print(hero.last_check)
