class BuyingExpirationInvalid(Exception):
    """Exception raised for invalid expiration in a buying process."""
    def __init__(self, message="Expiration date is invalid"):
        self.message = message
        super().__init__(self.message)