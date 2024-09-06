from abc import ABC, abstractmethod
import sqlite3

from fastapi import HTTPException, status

from schemas import NewTour, SavedTour


class BaseStorageTour(ABC):
    @abstractmethod
    def create_tour(self, new_tour: NewTour):
        pass

    @abstractmethod
    def get_tour(self, _id: int):
        pass

    @abstractmethod
    def get_tours(self, limit: int = 4):
        pass

    @abstractmethod
    def update_tour_price(self, _id: int, new_price: float):
        pass

    @abstractmethod
    def delete_tour(self, _id: int):
        pass


class StorageSQLite(BaseStorageTour, ABC):

    def _create_table(self):
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                CREATE TABLE IF NOT EXISTS {self.tour_table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    price REAL,
                    cover TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP 
                )
            """
            cursor.execute(query)
            connection.commit()

    def __init__(self, database_name: str):
        self.database_name = database_name
        self.tour_table_name = 'tours'
        self._create_table()

    def create_tour(self, new_product: NewTour) -> SavedTour:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            values = (new_product.title, new_product.description, new_product.price, str(new_product.cover))
            query = f"""
                INSERT INTO {self.tour_table_name} (title, description, price, cover)
                VALUES (?, ?, ?, ?)
            """
            cursor.execute(query, values)
            connection.commit()

        return self._get_latest_tour()

    def _get_latest_tour(self) -> SavedTour:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                SELECT id, title, description, price, cover, created_at
                FROM {self.tour_table_name}
                ORDER BY id DESC
                LIMIT 1
            """
            result: tuple = cursor.execute(query).fetchone()
            connection.commit()
            id, title, description, price, cover, created_at = result
            saved_product = SavedTour(
                id=id, title=title, description=description, price=price, cover=cover, created_at=created_at
            )

            return saved_product

    def get_tour(self, _id: int) -> SavedTour:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                SELECT id, title, description, price, cover, created_at
                FROM {self.tour_table_name}
                WHERE id = {_id}
            """
            result: tuple = cursor.execute(query).fetchone()
            connection.commit()

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=f'Check your entity id, product with {_id=} not found'
                )

            id, title, description, price, cover, created_at = result
            saved_product = SavedTour(
                id=id, title=title, description=description, price=price, cover=cover, created_at=created_at
            )

            return saved_product

    def get_tours(self, limit: int = 10, q: str = '') -> list[SavedTour]:
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                SELECT id, title, description, price, cover, created_at
                FROM {self.tour_table_name}
                WHERE title LIKE '%{q}%' OR description LIKE '%{q}%'
                ORDER BY id DESC
                LIMIT {limit}
            """
            data: list[tuple] = cursor.execute(query).fetchall()
            connection.commit()

        list_of_products = []
        for result in data:
            id, title, description, price, cover, created_at = result
            saved_product = SavedTour(
                id=id, title=title, description=description[:30], price=price, cover=cover, created_at=created_at
            )
            list_of_products.append(saved_product)
        return list_of_products

    def update_tour_price(self, _id: int, new_price: float) -> SavedTour:
        self.get_tour(_id)

        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                        UPDATE {self.tour_table_name}
                        SET
                            price = :Price
                        WHERE id = :Id
            """
            cursor.execute(query, {'Price': new_price, 'Id': _id})
            connection.commit()

        saved_product = self.get_tour(_id)
        return saved_product

    def delete_tour(self, _id: int):
        self.get_tour(_id)
        with sqlite3.connect(self.database_name) as connection:
            cursor = connection.cursor()
            query = f"""
                        DELETE FROM {self.tour_table_name}
                        WHERE id = :Id
            """
            cursor.execute(query, {'Id': _id})
            connection.commit()


storage = StorageSQLite('db_project.sqlite')
