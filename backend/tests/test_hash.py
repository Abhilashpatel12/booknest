import bcrypt

hash1 = b"$2b$12$F5stnQh/PIUVhG9dqKfgteE2w.Yso/5AhggRcIQz6jBjhc3DdD.ja"

print("Checking password: password")
try:
    print(bcrypt.checkpw(b"password", hash1))
except Exception as e:
    print(e)
    
print("Checking password: password123")
try:
    print(bcrypt.checkpw(b"password123", hash1))
except Exception as e:
    print(e)
    
print("Checking password: Password123")
try:
    print(bcrypt.checkpw(b"Password123", hash1))
except Exception as e:
    print(e)

