from discord.errors import HTTPException
from unittest.mock import Mock, MagicMock


# Helper to create a mock response object for the dummy exception
def create_mock_response_for_class(
    status=400,
    text="Mock Error",
    code=1000,
    method="POST",
    url="https://discord.com/api/v9/",
):
    # Use spec=aiohttp.ClientResponse for a more realistic mock if needed
    mock_resp = Mock()  # Or Mock(spec=aiohttp.ClientResponse)
    mock_resp.status = status
    mock_resp.method = method
    mock_resp.url = url
    mock_resp.code = code
    mock_resp.text = MagicMock(
        return_value=text
    )  # HTTPException might call .text() or access .text - let's set .text attribute directly in the class constructor for simplicity
    # Add json() method if needed by HTTPException or code handling it
    mock_resp.json = MagicMock()  # Returns a Mock by default, or specify return_value
    return mock_resp


class MockHTTPException(HTTPException):
    """
    A mock HTTPException class that inherits from the real one.
    Passes isinstance(obj, discord.HTTPException).
    """

    def __init__(
        self,
        status=400,
        text="Mock Error",
        code=1000,
        method="GET",
        url="https://discord.com/api/v9/",
    ):
        # The real HTTPException constructor signature is HTTPException(response, text, status)
        # So we create a mock response first
        mock_response = create_mock_response_for_class(status, text, code, method, url)

        # Call the parent constructor with our mock data
        # This sets self.response, self.text, and self.status
        super().__init__(mock_response, text)

        # Optional: Add any other attributes the parent doesn't set but you need
        # self.some_extra_data = "..."

    # __str__ is handled by the parent class based on self.response, self.text, self.status.
    # We don't need to override it unless we want a different format.
    # The parent's __str__ is quite good for this mock.
