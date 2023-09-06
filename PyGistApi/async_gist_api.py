import os
from typing import Dict, List, Union
from .base import Requester
from . import errors
from .utils import paste_content


class AsyncGistClient(Requester):
    def __init__(
        self,
        auth_token: str = None,
        timeout: int = 5,
        sleep_time: float = 0.5,
        retries: int = 2,
    ) -> None:
        """
        Initialize a GistClient instance.

        Args:
            auth_token (str, optional): GitHub API token for authentication.
            timeout (int, optional): Request timeout in seconds.
            sleep_time (float, optional): Time to sleep between retries.
            retries (int, optional): Number of retries for failed requests.
        """
        super().__init__(auth_token, timeout, sleep_time, retries)

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(auth_token='{self.auth_token}', "
            f"timeout={self.timeout}, sleep_time={self.sleep_time}, "
            f"retries={self.retries})"
        )

    async def list_gists(
        self, per_page: int = 30, page: int = 1, since: str = ""
    ) -> Dict:
        """
        List Gists from the authenticated user.

        Args:
            per_page (int, optional): Number of Gists per page.
            page (int, optional): Page number to retrieve.
            since (str, optional): Timestamp in ISO 8601 format for filtering Gists.

        Returns:
            Dict: A dictionary containing the list of Gists.

        Raises:
            InvalidArg: If input arguments are invalid.
        """
        if not isinstance(per_page, int) or per_page > 100:
            raise errors.InvalidArg("per_page should be an integer and less than 100")

        if not isinstance(page, int):
            raise errors.InvalidArg("page should be an integer")

        params: Dict[str, Union[int, str]] = {
            "per_page": per_page,
            "page": page,
            "since": since,
        }

        return await self._async_request("GET", params=params)

    async def create_gist(
        self,
        content: Union[str, List[str]],
        file_name: str = None,
        description: str = "",
        public: bool = False,
    ) -> Dict:
        """
        Create a new Gist.

        Args:
            content (Union[str, List[str]]): Content of the Gist as a string or list of file paths.
            file_name (str, optional): Name of the Gist file.
            description (str, optional): Description for the Gist.
            public (bool, optional): If True, the Gist will be public; otherwise, it's private.

        Returns:
            Dict: A dictionary containing the created Gist information.

        Raises:
            InvalidArg: If input arguments are invalid.
            FileNotFoundError: If file(s) specified in content are not found.
        """
        data = {
            "description": description,
            "public": public,
        }

        if not isinstance(content, (str, list)):
            raise errors.InvalidArg(
                "content should be str, list of file paths, or a single file path"
            )

        elif isinstance(content, list) or (
            os.path.isfile(content) if isinstance(content, str) else False
        ):
            file_data = {}
            files = content if isinstance(content, list) else [content]

            for file in files:
                if os.path.isfile(file):
                    name_of_file = os.path.basename(file)
                    with open(file, "r") as f:
                        file_data[name_of_file] = {"content": f.read().strip()}

            if not file_data:
                raise FileNotFoundError("Unable to locate the file(s)")
            data["files"] = file_data

        else:
            data["files"] = {file_name or "untitled.txt": {"content": content}}

        return await self._async_request("POST", data=data)

    async def update_gist(
        self,
        content: str,
        gist_id: str,
        filename_to_update: str,
        description: str = "",
    ) -> Dict:
        """
            Update an existing Gist.

        Args:
            content (str): Content of the Gist as a string.
            gist_id (str): ID of the Gist to update.
            filename_to_update (str): Name of the file within the Gist to update.
            description (str, optional): Description for the Gist.

        Returns:
            Dict: A dictionary containing the updated Gist information.

        Raises:
            InvalidArg: If input arguments are invalid.
            FileNotFoundError: If the specified Gist or file is not found.
        """
        data = {
            "description": description,
        }

        gist = await self.get_gist(gist_id=gist_id)

        if "files" not in gist:
            return {"message": "files not found"}

        if filename_to_update not in gist["files"]:
            return {"message": f"File '{filename_to_update}' not found in the Gist."}

        if not isinstance(content, str):
            raise errors.InvalidArg("content should be str or a file path")

        if os.path.isfile(content):
            with open(content) as f:
                data["files"] = {filename_to_update: {"content": f.read().strip()}}
        else:
            data["files"] = {filename_to_update: {"content": content}}

        return await self._async_request("PATCH", data=data, endpoint=f"/{gist_id}")

    async def delete_gist(self, gist_id: str) -> Dict:
        """
        Delete a specific Gist from GitHub.

        Args:
            gist_id (str): ID of the Gist to delete.

        Returns:
            Dict: A dictionary containing the result of the delete operation, typically indicating success or failure.
        """
        return await self._async_request("DELETE", endpoint=f"/{gist_id}")

    async def public_gists(
        self, per_page: int = 30, page: int = 1, since: str = ""
    ) -> List[Dict]:
        """
        List public Gists from GitHub.

        Args:
            per_page (int, optional): Number of public Gists per page.
            page (int, optional): Page number to retrieve.
            since (str, optional): Timestamp in ISO 8601 format for filtering Gists.

        Returns:
            List[Dict]: A list of dictionaries containing public Gist information.

        Raises:
            InvalidArg: If input arguments are invalid.
        """
        if not isinstance(per_page, int) or per_page > 100:
            raise errors.InvalidArg("per_page should be an integer and less than 100")

        if not isinstance(page, int):
            raise errors.InvalidArg("page should be an integer")

        return await self._async_request("GET", endpoint="/public")

    async def starred_gists(
        self, per_page: int = 30, page: int = 1, since: str = ""
    ) -> List[Dict]:
        """
        List starred Gists from the authenticated user.

        Args:
            per_page (int, optional): Number of starred Gists per page.
            page (int, optional): Page number to retrieve.
            since (str, optional): Timestamp in ISO 8601 format for filtering Gists.

        Returns:
            List[Dict]: A list of dictionaries containing starred Gist information.

        Raises:
            InvalidArg: If input arguments are invalid.
        """
        if not isinstance(per_page, int) or per_page > 100:
            raise errors.InvalidArg("per_page should be an integer and less than 100")

        if not isinstance(page, int):
            raise errors.InvalidArg("page should be an integer")

        return await self._async_request("GET", endpoint="/starred")

    async def get_gist(self, gist_id: str, paste: bool = False) -> Dict:
        """
        Retrieve details of a specific Gist.

        Args:
            gist_id (str): ID of the Gist to retrieve.
            paste (bool, optional): If True, returns the pasted content of the gist in nekobin.com

        Returns:
            Dict: A dictionary containing the details of the requested Gist.
        """
        gist = await self._async_request("GET", endpoint=f"/{gist_id}")
        if not paste:
            return gist
        content = str()
        if "files" in gist:
            for file, codes in gist["files"].items():
                content += f"{'-' * 5}{codes['filename']}{'-' * 5}\n"
                content += codes["content"]
                content += f"{'-' * 5}{codes['filename']}{'-' * 5}\n\n"

        pasted = paste_content(content if paste else "No Content found")
        gist["pasted_url"] = pasted
        return gist

    async def gist_commits(
        self, gist_id: int, per_page: int = 30, page: int = 1
    ) -> List[Dict]:
        """
        Retrieve a list of commits for a specific Gist.

        Args:
            gist_id (int): The ID of the Gist.
            per_page (int, optional): Number of commits per page.
            page (int, optional): Page number to retrieve.

        Returns:
            List[Dict]: A list of dictionaries containing commit details.
        Raises:
            InvalidArg: If input arguments are invalid.
        """
        if not isinstance(per_page, int) or per_page > 100:
            raise errors.InvalidArg("per_page should be an integer and less than 100")

        if not isinstance(page, int):
            raise errors.InvalidArg("page should be an integer")

        return await self._async_request(
            "GET",
            endpoint=f"/{gist_id}/commits",
            params={"per_page": per_page, "page": page},
        )

    async def gist_forks(
        self, gist_id: int, per_page: int = 30, page: int = 1
    ) -> List[Dict]:
        """
        Retrieve a list of forks for a specific Gist.

        Args:
            gist_id (int): The ID of the Gist.
            per_page (int, optional): Number of forks per page.
            page (int, optional): Page number to retrieve.

        Returns:
            List[Dict]: A list of dictionaries containing fork details.
        Raises:
            InvalidArg: If input arguments are invalid.
        """
        if not isinstance(per_page, int) or per_page > 100:
            raise errors.InvalidArg("per_page should be an integer and less than 100")

        if not isinstance(page, int):
            raise errors.InvalidArg("page should be an integer")

        return await self._async_request(
            "GET",
            endpoint=f"/{gist_id}/forks",
            params={"per_page": per_page, "page": page},
        )

    async def fork_gist(self, gist_id: int) -> Dict:
        """
        Fork a Gist.

        Args:
            gist_id (int): The ID of the Gist to fork.

        Returns:
            Dict: A dictionary containing information about the forked Gist.
        """
        return await self._async_request(
            "POST",
            endpoint=f"/{gist_id}/forks",
        )

    async def is_gist_starred(self, gist_id: int) -> Dict:
        """
        Check if a Gist is starred by the authenticated user.

        Args:
            gist_id (int): The ID of the Gist to check.

        Returns:
            Dict: Containing the status code.
        """
        return await self._async_request(
            "GET",
            endpoint=f"/{gist_id}/star",
        )

    async def star_gist(self, gist_id: int) -> Dict:
        """
        Star a Gist.

        Args:
            gist_id (int): The ID of the Gist to star.

        Returns:
            Dict: A dictionary containing information about the starred Gist.
        """
        return await self._async_request(
            "PUT",
            endpoint=f"/{gist_id}/star",
        )

    async def unstar_gist(self, gist_id: int) -> Dict:
        """
        Unstar a Gist.

        Args:
            gist_id (int): The ID of the Gist to unstar.

        Returns:
            Dict: A dictionary containing information about the unstarred Gist.
        """
        return await self._async_request(
            "DELETE",
            endpoint=f"/{gist_id}/star",
        )

    async def gist_revision(self, gist_id: int, sha: str) -> Dict:
        """
        Retrieve details of a specific revision of a Gist.

        Args:
            gist_id (int): The ID of the Gist.
            sha (str): The SHA identifier of the revision.

        Returns:
            Dict: A dictionary containing details of the requested Gist revision.
        """
        return await self._async_request(
            "GET",
            endpoint=f"/{gist_id}/{sha}",
        )
