from app.crud.base import CRUDBase
from app.models.shelf import Shelf
from app.schemas.shelf import ShelfCreate, ShelfUpdate

class CRUDShelf(CRUDBase[Shelf, ShelfCreate, ShelfUpdate]):
    pass

shelf = CRUDShelf(Shelf)
