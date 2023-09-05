import httpx

def get_auth_token() -> str:
    from . import auth_token, auth_token_path , errors
    
    """
    Get the authentication token from either a file or a variable.

    Returns:
        str: The authentication token.

    Raises:
        ValueError: If the token has an invalid format.
        AuthenticationError: If the token is not set.
    """
    # Check if the auth token is set via a file path
    if auth_token_path:
        with open(auth_token_path, "rt") as file:
            token = file.read().strip()
            if not token.startswith("ghp_"):
                raise ValueError("Invalid Token Format")
            return token

    # Check if the auth token is set as a variable
    elif auth_token:
        return auth_token

    # No token is set, raise an authentication error
    else:
        raise errors.AuthenticationError(
            "You can set your auth token using PyGistApi.auth_token='your auth token' "
            "or by setting the environment variable: AUTH_TOKEN=<AUTH-TOKEN>"
        )
    



def paste_content(
    content: str,
) -> str:
    """
    Upload content to Nekobin and return the generated URL.
    Args:
        content (str): Content to be uploaded.
    Returns:
        str: URL of the uploaded paste.
    """
    req_url = "https://nekobin.com/api/documents"
    json = {"content": content}
    try:
        response = httpx.post(req_url, json=json)
        response.raise_for_status()
    except httpx.HTTPError as e:
        return f"An error occurred: {e}"

    return f"https://nekobin.com/{response.json()['result']['key']}"
