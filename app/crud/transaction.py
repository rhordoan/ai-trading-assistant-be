# app/crud/transaction.py

from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session

from app.models.transaction import Transaction as TxModel
from app.schemas.transaction import TransactionCreate, TransactionUpdate

def create_transaction(
    db: Session, portfolio_id: int, tx_in: TransactionCreate
) -> TxModel:
    tx = TxModel(portfolio_id=portfolio_id, **tx_in.dict())
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def get_transactions(
    db: Session,
    portfolio_id: int,
    skip: int = 0,
    limit: int = 50,
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> List[TxModel]:
    q = db.query(TxModel).filter(TxModel.portfolio_id == portfolio_id)
    if start:
        q = q.filter(TxModel.timestamp >= start)
    if end:
        q = q.filter(TxModel.timestamp <= end)
    return (
        q.order_by(TxModel.timestamp.desc())
         .offset(skip)
         .limit(limit)
         .all()
    )

def update_transaction(
    db: Session,
    tx_id: int,
    tx_in: Union[TransactionUpdate, Dict[str, Any]],
) -> Optional[TxModel]:
    tx = db.query(TxModel).filter(TxModel.id == tx_id).first()
    if not tx:
        return None

    # Only include fields actually sent by the client
    if isinstance(tx_in, dict):
        updates = tx_in
    else:
        updates = tx_in.dict(exclude_unset=True)

    for field, value in updates.items():
        setattr(tx, field, value)

    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx

def delete_transaction(db: Session, tx_id: int) -> bool:
    tx = db.query(TxModel).filter(TxModel.id == tx_id).first()
    if not tx:
        return False
    db.delete(tx)
    db.commit()
    return True
