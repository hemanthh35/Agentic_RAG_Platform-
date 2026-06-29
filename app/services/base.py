from typing import Generic, TypeVar
from app.repositories.base import BaseRepository

# Type variable for the associated repository
RepoType = TypeVar("RepoType", bound=BaseRepository)


class BaseService(Generic[RepoType]):
    """Base service class encapsulating business logic.

    Maintains a reference to its primary repository layer object.
    """

    def __init__(self, repository: RepoType):
        """Initializes the service with its primary repository dependency.

        Args:
            repository: An instance of the repository.
        """
        self.repository = repository
