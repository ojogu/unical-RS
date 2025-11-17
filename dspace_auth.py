import requests
import urllib3

DSPACE_SERVER_URL = "http://localhost:8080/server"
# USERNAME = "nkangprecious26@gmail.com"
# PASSWORD = "09065011334"

USERNAME = "ojogup@gmail.com"
PASSWORD = "123456789"
def authenticate_to_dspace():
    """
    Authenticates to DSpace REST API using the proper flow.
    """
    # Suppress SSL warnings if using verify=False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    # Create a session to maintain cookies across requests
    session = requests.Session()
    
    # Step 1: Get CSRF token
    csrf_url = f"{DSPACE_SERVER_URL}/api/security/csrf"
    try:
        csrf_response = session.get(csrf_url, verify=False)
        csrf_response.raise_for_status()
        
        csrf_token = csrf_response.headers.get("DSPACE-XSRF-TOKEN")
        print(f"CSRF Token obtained: {csrf_token}")
        print(f"Cookies after CSRF: {session.cookies.get_dict()}")
        
        if not csrf_token:
            print("Error: CSRF token not found in response headers")
            return None, None
        
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining CSRF token: {e}")
        return None, None
    
    # Step 2: Login with credentials using form data
    login_url = f"{DSPACE_SERVER_URL}/api/authn/login"
    headers = {
        "X-XSRF-TOKEN": csrf_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Form data as per DSpace documentation
    data = {
        "user": USERNAME,
        "password": PASSWORD
    }
    
    try:
        login_response = session.post(
            login_url,
            headers=headers,
            data=data,  # Form data, not auth
            verify=False
        )
        login_response.raise_for_status()
        
        print("\n=== Login Successful ===")
        print(f"Status Code: {login_response.status_code}")
        print(f"Response Headers: {dict(login_response.headers)}")
        print(f"Cookies after login: {session.cookies.get_dict()}")
        
        # The JWT token is in the Authorization header
        jwt_token = login_response.headers.get("Authorization")
        if jwt_token:
            print(f"\nJWT Token: {jwt_token}")
            return session, jwt_token
        else:
            print("\nWarning: JWT Token not found in Authorization header")
            print(f"Response body: {login_response.text}")
            return session, None
            
    except requests.exceptions.RequestException as e:
        print(f"\n=== Login Failed ===")
        print(f"Error: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response Headers: {dict(e.response.headers)}")
            print(f"Response Body: {e.response.text}")
            
            # Check WWW-Authenticate header for supported auth methods
            www_auth = e.response.headers.get("WWW-Authenticate")
            if www_auth:
                print(f"\nSupported authentication methods: {www_auth}")
        return None, None

def test_authenticated_request(session, jwt_token):
    """
    Tests an authenticated request to verify the session works.
    """
    status_url = f"{DSPACE_SERVER_URL}/api/authn/status"
    headers = {}
    
    if jwt_token:
        headers["Authorization"] = jwt_token
    
    try:
        response = session.get(status_url, headers=headers, verify=False)
        response.raise_for_status()
        print("\n=== Authentication Status ===")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"\nError checking auth status: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("DSpace Authentication Test")
    print("=" * 50)
    
    session, jwt_token = authenticate_to_dspace()
    
    if session:
        print("\n" + "=" * 50)
        test_authenticated_request(session, jwt_token)
    else:
        print("\nAuthentication failed. Please check:")
        print("1. Your credentials are correct")
        print("2. The account is active in DSpace")
        print("3. You can log in via the web interface with these credentials")