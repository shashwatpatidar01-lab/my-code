from pathlib import Path

import qrcode
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models import DiningTable

BASE_URL = "http://localhost:8000/menu"
OUT_DIR = Path("qr_codes")
OUT_DIR.mkdir(exist_ok=True)


def main():
    db: Session = SessionLocal()
    try:
        for table in db.query(DiningTable).all():
            img = qrcode.make(f"{BASE_URL}/{table.qr_token}")
            img.save(OUT_DIR / f"table_{table.id}.png")
            print(f"Generated QR for {table.name}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
