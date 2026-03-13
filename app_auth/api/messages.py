class AuthMessages:
    ACTIVATION_SUCCESS = "Account successfully activated."
    LOGIN_SUCCESS = "Login successful"
    LOGOUT_SUCCESS = (
        "Logout successful! All tokens will be deleted. Refresh token is now invalid."
    )
    TOKEN_REFRESH_SUCCESS = "Token refreshed"
    PW_RESET_SENT = "An email has been sent to reset your password."
    PW_RESET_SUCCESS = "Your Password has been successfully reset."

    INVALID_TOKEN = "Invalid or expired token."
    INVALID_PW_LINK = "This password reset link is invalid or has already been used."
    REFRESH_TOKEN_REQUIRED = "Refresh-Token required."
