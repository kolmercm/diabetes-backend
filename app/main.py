from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from firebase_admin import credentials, auth, initialize_app
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("service-account.json")
initialize_app(cred)

# CORS Configuration
# origins = [
#     "http://localhost:3000",  # Replace with your frontend's origin
#     "https://yourdomain.com",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = HTTPBearer()


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        id_token = token.credentials
        decoded_token = auth.verify_id_token(id_token)
        
        # Log decoded token for debugging
        logger.info(f"Decoded token for user {decoded_token.get('uid')}: {decoded_token}")
        
        return decoded_token
    except auth.InvalidIdTokenError:
        logger.error("Invalid ID token.")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        raise HTTPException(status_code=403, detail="Insufficient permissions")


@app.get("/protected-route")
def protected_route(current_user: dict = Depends(get_current_user)):
    # Changed: Now accessible to any authenticated user
    return {"message": f"Hello, authenticated user {current_user['uid']}"}

# ... existing routes ...

@app.get("/")
def read_root():
    return {"Hello": "World"}

# Added: Commented code for future admin-only access
# def require_admin(user: dict = Depends(get_current_user)):
#     if not user.get('admin', False):
#         logger.warning(f"User {user['uid']} does not have admin privileges.")
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
#         )
#     return user

# @app.get("/admin-only-route")
# def admin_only_route(current_user: dict = Depends(require_admin)):
#     return {"message": f"Hello, admin {current_user['uid']}"}