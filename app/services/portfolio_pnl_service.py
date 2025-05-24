from sqlalchemy.orm import Session
from typing import Tuple
from app.crud.transaction import get_transactions
from app.services.portfolio_service import compute_portfolio_value

async def compute_pnl(db: Session, portfolio_id: int) -> dict:
    """
    Calculate the realized and unrealized P&L for a given portfolio.
    Realized P&L is calculated based on the transactions in the portfolio,
    while unrealized P&L is based on the current market value of the portfolio.
    """
    txs = get_transactions(db, portfolio_id)

    realized = 0.0
    holdings = {}

    # calculate realized P&L and build current holdings
    for tx in txs:
        qty = tx.quantity if tx.type == tx.type.BUY else -tx.quantity
        avg = tx.price
        holdings.setdefault(tx.symbol, []).append((qty, avg))
        if tx.type == tx.type.SELL:
            # match sells against buys FIFO-style
            sell_qty = tx.quantity
            while sell_qty > 0 and holdings[tx.symbol]:
                buy_qty, buy_price = holdings[tx.symbol].pop(0)
                matched = min(buy_qty, sell_qty)
                realized += (tx.price - buy_price) * matched
                if buy_qty > matched:
                    holdings[tx.symbol].insert(0, (buy_qty - matched, buy_price))
                sell_qty -= matched

    # unrealized: current market value – cost basis of remaining lots
    total_value = await compute_portfolio_value(db, portfolio_id)
    cost_basis = sum(q * p for sym in holdings for q, p in holdings[sym])
    unrealized = total_value - cost_basis

    return {
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "market_value": total_value
    }
