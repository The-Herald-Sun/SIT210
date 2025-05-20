from .Models import Cow
from .import db

class CowDataAccess:
    def __init__(self):
        self.db = db

    def get_all_cows(self) -> list[Cow]:
        """
        Get all cows from the database.
        """
        return Cow.select()
    
    def get_cow_by_id(self, cow_id: int) -> Cow:
        """
        Get a cow by its ID.
        """
        return Cow.get_or_none(Cow.id == cow_id)
    
    def get_cow_by_tag_id(self, tag_id: str) -> Cow:
        """
        Get a cow by its tag ID.
        """
        return Cow.get_or_none(Cow.tag_id == tag_id)
        
    def add_cow(self, cow: Cow) -> None:
        """
        Add a new cow to the database.
        """
        cow.save()

    def delete_cow(self, cow_id: int) -> None:
        """
        Delete a cow from the database.
        """
        cow = Cow.get(Cow.id == cow_id)
        cow.delete_instance()

    def update_cow(self, cow: Cow, ) -> None:
        """
        Update an existing cow in the database.
        """
        existing_cow = Cow.get_or_none(Cow.id == cow.id)
        if existing_cow is None:
           raise ValueError(f"Cow with id {cow.id} does not exist")
        cow.save()