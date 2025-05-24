# from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Body
# from sqlalchemy.orm import Session
# from typing import List, Optional
# from datetime import date

# from app.core.dependencies import get_current_user
# from app.db.session import get_db
# from app.crud import portfolio as crud
# from app.crud import transaction as crud_tx
# from app.schemas.portfolio import PortfolioCreate, PortfolioOut, PositionCreate, PositionOut
# from app.schemas.transaction import Transaction, TransactionCreate, TransactionUpdate
# from app.services.portfolio_service import compute_portfolio_value
# from app.services.portfolio_pnl_service import compute_pnl

# router = APIRouter(
#     prefix="/portfolios",
#     tags=["Portfolios"],
#     dependencies=[Depends(get_current_user)],
# )

# @router.post(
#     "/",
#     response_model=PortfolioOut,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_portfolio(
#     data: PortfolioCreate,
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     return crud.create_portfolio(db, current_user.id, data)

# @router.get("/", response_model=List[PortfolioOut])
# def list_portfolios(
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     return crud.get_portfolios(db, current_user.id)

# @router.post(
#     "/{pf_id}/positions",
#     response_model=PositionOut,
#     status_code=status.HTTP_201_CREATED,
# )
# def add_position(
#     pf_id: int = Path(..., gt=0),
#     data: PositionCreate = Body(...),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     p = crud.get_portfolio(db, pf_id)
#     if not p or p.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     return crud.create_position(db, pf_id, data)

# @router.get("/{pf_id}/positions", response_model=List[PositionOut])
# def list_positions(
#     pf_id: int = Path(..., gt=0),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     p = crud.get_portfolio(db, pf_id)
#     if not p or p.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     return crud.get_positions(db, pf_id)

# @router.get("/{pf_id}/value")
# async def get_portfolio_value(
#     pf_id: int = Path(..., gt=0),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     p = crud.get_portfolio(db, pf_id)
#     if not p or p.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     value = await compute_portfolio_value(db, pf_id)
#     return {"portfolio_id": pf_id, "value": value}

# # ——— Transaction endpoints —————————————————————

# @router.post(
#     "/{pf_id}/transactions",
#     response_model=Transaction,
#     status_code=status.HTTP_201_CREATED,
# )
# def add_transaction(
#     pf_id: int = Path(..., gt=0),
#     tx_in: TransactionCreate = Body(...),         
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     p = crud.get_portfolio(db, pf_id)
#     if not p or p.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     return crud_tx.create_transaction(db, pf_id, tx_in)

# @router.get("/{pf_id}/transactions", response_model=List[Transaction])
# def list_transactions(
#     pf_id: int = Path(..., gt=0),
#     skip: int = Query(0, ge=0),
#     limit: int = Query(50, gt=0, le=200),
#     start: Optional[date] = Query(None),
#     end: Optional[date] = Query(None),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     p = crud.get_portfolio(db, pf_id)
#     if not p or p.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     return crud_tx.get_transactions(
#         db,
#         pf_id,
#         skip=skip,
#         limit=limit,
#         start=start.isoformat() if start else None,
#         end=end.isoformat() if end else None,
#     )

# @router.put("/{pf_id}/transactions/{tx_id}", response_model=Transaction)
# def update_transaction(
#     pf_id: int = Path(..., gt=0),
#     tx_id: int = Path(..., gt=0),
#     tx_in: TransactionUpdate = Body(...),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     p = crud.get_portfolio(db, pf_id)
#     if not p or p.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     tx = crud_tx.update_transaction(db, tx_id, tx_in)
#     if not tx:
#         raise HTTPException(status_code=404, detail="Transaction not found")
#     return tx

# @router.delete(
#     "/{pf_id}/transactions/{tx_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def delete_transaction(
#     pf_id: int = Path(..., gt=0),
#     tx_id: int = Path(..., gt=0),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     p = crud.get_portfolio(db, pf_id)
#     if not p or p.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     success = crud_tx.delete_transaction(db, tx_id)
#     if not success:
#         raise HTTPException(status_code=404, detail="Transaction not found")
#     return None

# # ——— PnL endpoint ———————————————————————————

# @router.get("/{pf_id}/pnl")
# async def get_portfolio_pnl(
#     pf_id: int = Path(..., gt=0),
#     db: Session = Depends(get_db),
#     current_user=Depends(get_current_user),
# ):
#     p = crud.get_portfolio(db, pf_id)
#     if not p or p.user_id != current_user.id:
#         raise HTTPException(status_code=404, detail="Portfolio not found")
#     return await compute_pnl(db, pf_id)
# app/routers/transactions.py

from typing import List, Optional
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status, Body
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.crud import portfolio as crud_pf, transaction as crud_tx
from app.schemas.portfolio import PortfolioCreate, PortfolioOut, PositionCreate, PositionOut
from app.schemas.transaction import Transaction, TransactionCreate, TransactionUpdate
from app.services.portfolio_service import compute_portfolio_value
from app.services.portfolio_pnl_service import compute_pnl

router = APIRouter(
    prefix="/portfolios",
    tags=["Portfolios"],
    dependencies=[Depends(get_current_user)],
)

@router.post(
    "/",
    response_model=PortfolioOut,
    status_code=status.HTTP_201_CREATED,
)
def create_portfolio(
    data: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud_pf.create_portfolio(db, current_user.id, data)

@router.get("/", response_model=List[PortfolioOut])
def list_portfolios(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return crud_pf.get_portfolios(db, current_user.id)

@router.post(
    "/{pf_id}/positions",
    response_model=PositionOut,
    status_code=status.HTTP_201_CREATED,
)
def add_position(
    pf_id: int = Path(..., gt=0),
    data: PositionCreate = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = crud_pf.get_portfolio(db, pf_id)
    if not p or p.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return crud_pf.create_position(db, pf_id, data)

@router.get("/{pf_id}/positions", response_model=List[PositionOut])
def list_positions(
    pf_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = crud_pf.get_portfolio(db, pf_id)
    if not p or p.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return crud_pf.get_positions(db, pf_id)

@router.get("/{pf_id}/value")
async def get_portfolio_value(
    pf_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = crud_pf.get_portfolio(db, pf_id)
    if not p or p.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    value = await compute_portfolio_value(db, pf_id)
    return {"portfolio_id": pf_id, "value": value}


# ——— Transaction endpoints —————————————————————

@router.post(
    "/{pf_id}/transactions",
    response_model=Transaction,
    status_code=status.HTTP_201_CREATED,
)
def add_transaction(
    pf_id: int = Path(..., gt=0),
    tx_in: TransactionCreate = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = crud_pf.get_portfolio(db, pf_id)
    if not p or p.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return crud_tx.create_transaction(db, pf_id, tx_in)


@router.get(
    "/{pf_id}/transactions",
    response_model=List[Transaction],
)
def list_transactions(
    pf_id: int = Path(..., gt=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, gt=0, le=200),
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = crud_pf.get_portfolio(db, pf_id)
    if not p or p.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return crud_tx.get_transactions(
        db,
        pf_id,
        skip=skip,
        limit=limit,
        start=start.isoformat() if start else None,
        end=end.isoformat() if end else None,
    )


@router.put(
    "/{pf_id}/transactions/{tx_id}",
    response_model=Transaction,
)
def update_transaction(
    pf_id: int = Path(..., gt=0),
    tx_id: int = Path(..., gt=0),
    tx_in: TransactionUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = crud_pf.get_portfolio(db, pf_id)
    if not p or p.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    tx = crud_tx.update_transaction(db, tx_id, tx_in)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.delete(
    "/{pf_id}/transactions/{tx_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    pf_id: int = Path(..., gt=0),
    tx_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = crud_pf.get_portfolio(db, pf_id)
    if not p or p.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    success = crud_tx.delete_transaction(db, tx_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return None


# ——— PnL endpoint ———————————————————————————

@router.get("/{pf_id}/pnl")
async def get_portfolio_pnl(
    pf_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    p = crud_pf.get_portfolio(db, pf_id)
    if not p or p.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return await compute_pnl(db, pf_id)
