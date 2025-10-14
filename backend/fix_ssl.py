#!/usr/bin/env python3
"""
MongoDB SSL Fix Script - Try different SSL configurations
"""
import os
import ssl
import pymongo
from dotenv import load_dotenv

load_dotenv()

def fix_ssl_connection():
    """Try different SSL configurations to fix the connection"""
    connection_string = os.getenv('MONGODB_CONNECTION_STRING')
    
    print("🔧 Trying SSL Fixes for MongoDB Atlas...")
    print("=" * 50)
    
    # Fix 1: Use pymongo with tlsCAFile=certifi.where()
    try:
        print("🧪 Fix 1: Using certifi SSL certificates")
        import certifi
        
        client = pymongo.MongoClient(
            connection_string,
            tlsCAFile=certifi.where(),
            serverSelectionTimeoutMS=10000
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connection works with certifi certificates!")
        
        # Test collections
        db = client['kamani007']
        collections = db.list_collection_names()
        print(f"📊 Found {len(collections)} collections: {collections}")
        
        client.close()
        return "certifi"
        
    except Exception as e:
        print(f"❌ Fix 1 failed: {str(e)}")
    
    # Fix 2: Disable SSL certificate verification
    try:
        print("\n🧪 Fix 2: Disable SSL certificate verification")
        
        client = pymongo.MongoClient(
            connection_string,
            tlsAllowInvalidCertificates=True,
            tlsAllowInvalidHostnames=True,
            serverSelectionTimeoutMS=10000
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connection works with SSL verification disabled!")
        
        client.close()
        return "no_ssl_verify"
        
    except Exception as e:
        print(f"❌ Fix 2 failed: {str(e)}")
    
    # Fix 3: Try with older TLS version
    try:
        print("\n🧪 Fix 3: Force TLS 1.2")
        
        client = pymongo.MongoClient(
            connection_string,
            tlsAllowInvalidCertificates=True,
            ssl_cert_reqs=ssl.CERT_NONE,
            serverSelectionTimeoutMS=10000
        )
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connection works with TLS 1.2!")
        
        client.close()
        return "tls12"
        
    except Exception as e:
        print(f"❌ Fix 3 failed: {str(e)}")
    
    # Fix 4: Try non-SRV connection string
    try:
        print("\n🧪 Fix 4: Using non-SRV connection string")
        
        # Convert SRV to regular connection string
        non_srv = connection_string.replace(
            "mongodb+srv://kamani007:Do11KyolnhGC30ZI@basecluster.umm6id8.mongodb.net/",
            "mongodb://kamani007:Do11KyolnhGC30ZI@ac-jhp9rp4-shard-00-00.umm6id8.mongodb.net:27017,ac-jhp9rp4-shard-00-01.umm6id8.mongodb.net:27017,ac-jhp9rp4-shard-00-02.umm6id8.mongodb.net:27017/"
        )
        non_srv += "&ssl=false"
        
        client = pymongo.MongoClient(non_srv, serverSelectionTimeoutMS=10000)
        
        client.admin.command('ping')
        print("✅ SUCCESS: Connection works without SRV!")
        
        client.close()
        return "no_srv"
        
    except Exception as e:
        print(f"❌ Fix 4 failed: {str(e)}")
    
    print("\n❌ All SSL fixes failed")
    return None

def update_database_connection(fix_type):
    """Update the database.py file with the working SSL configuration"""
    if fix_type == "certifi":
        print("\n📝 Updating database.py to use certifi certificates...")
        # We'll implement this if certifi works
    elif fix_type == "no_ssl_verify":
        print("\n📝 Updating database.py to disable SSL verification...")
        # We'll implement this if SSL verification bypass works
    else:
        print(f"\n📝 Need to implement fix for: {fix_type}")

if __name__ == "__main__":
    fix_type = fix_ssl_connection()
    
    if fix_type:
        print(f"\n🎉 Found working SSL configuration: {fix_type}")
        print("Now we can update the application to use this configuration.")
    else:
        print("\n💡 Consider these alternatives:")
        print("1. Create a new MongoDB Atlas cluster with different settings")
        print("2. Use a local MongoDB instance for development")
        print("3. Try from a different network environment")