import secrets

# prints a secure random secret key 
# to use as secret key or SECURITY_PASSWORD_SALT
res = secrets.SystemRandom().getrandbits(128)
print(res)
