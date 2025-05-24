from sqlalchemy.orm import Session
from app.crud import portfolio as crud_portfolio
from app.services.financial_data_service import FinancialDataService

fd_service = FinancialDataService()

async def compute_portfolio_value(db: Session, portfolio_id: int) -> float:
    positions = crud_portfolio.get_positions(db, portfolio_id)
    total = 0.0
    for pos in positions:
        # 1) Fetch quote asincron
        quote = await fd_service.get_stock_quote(pos.symbol)
        price = float(quote.get("05. price", 0))
        total += price * pos.quantity
    return total
