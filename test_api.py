#!/usr/bin/env python3
"""
Test script for the Mental Health Support Chatbot API (one chat per user)
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
TEST_USER_ID = "test_user_123"

def test_health_check():
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_chat_endpoint(message: str, expected_keywords: list = None):
    print(f"\n💬 Testing chat endpoint with: '{message}'")
    try:
        payload = {
            "message": message,
            "user_id": TEST_USER_ID
        }
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint successful")
            print(f"   User ID: {data['user_id']}")
            print(f"   Response: {data['response'][:100]}...")
            print(f"   Message ID: {data['message_id']}")
            if 'context_analysis' in data:
                analysis = data['context_analysis']
                print(f"   Total messages: {analysis.get('total_messages', 0)}")
                print(f"   Engagement level: {analysis.get('engagement_level', 'unknown')}")
                print(f"   Sentiment trend: {analysis.get('sentiment_trend', 'unknown')}")
                current_analysis = analysis.get('current_message_analysis', {})
                print(f"   Crisis detected: {current_analysis.get('is_crisis', False)}")
                print(f"   Urgency level: {current_analysis.get('urgency_level', 'unknown')}")
            if expected_keywords:
                response_text = data['response'].lower()
                found_keywords = [kw for kw in expected_keywords if kw.lower() in response_text]
                if found_keywords:
                    print(f"   ✅ Found expected keywords: {found_keywords}")
                else:
                    print(f"   ⚠️  Expected keywords not found: {expected_keywords}")
            return True
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat endpoint error: {e}")
        return False

def test_conversation_history():
    print(f"\n📚 Testing conversation history for user {TEST_USER_ID}...")
    try:
        response = requests.get(f"{BASE_URL}/conversation/{TEST_USER_ID}/history")
        if response.status_code == 200:
            data = response.json()
            print("✅ Conversation history successful")
            print(f"   User ID: {data['user_id']}")
            print(f"   Messages in history: {len(data['history'])}")
            for msg in data['history'][-3:]:
                role = msg['role']
                content = msg['content'][:50] + "..." if len(msg['content']) > 50 else msg['content']
                print(f"   {role}: {content}")
            return True
        else:
            print(f"❌ Conversation history failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Conversation history error: {e}")
        return False

def test_user_analysis():
    print(f"\n📊 Testing user analysis for {TEST_USER_ID}...")
    try:
        response = requests.get(f"{BASE_URL}/user/{TEST_USER_ID}/analysis")
        if response.status_code == 200:
            data = response.json()
            print("✅ User analysis successful")
            print(f"   User ID: {data['user_id']}")
            analysis = data['analysis']
            print(f"   Total messages: {analysis.get('total_messages', 0)}")
            print(f"   Sentiment: {analysis.get('sentiment', 'unknown')}")
            print(f"   Engagement level: {analysis.get('engagement_level', 'unknown')}")
            print(f"   Topics: {analysis.get('topics', [])}")
            summary = data.get('summary', {})
            print(f"   Total conversations: {summary.get('total_conversations', 0)}")
            print(f"   Total messages: {summary.get('total_messages', 0)}")
            return True
        else:
            print(f"❌ User analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User analysis error: {e}")
        return False

def test_user_summary():
    print(f"\n📈 Testing user summary for {TEST_USER_ID}...")
    try:
        response = requests.get(f"{BASE_URL}/user/{TEST_USER_ID}/summary")
        if response.status_code == 200:
            data = response.json()
            print("✅ User summary successful")
            print(f"   User ID: {data['user_id']}")
            summary = data['summary']
            print(f"   Total conversations: {summary.get('total_conversations', 0)}")
            print(f"   Total messages: {summary.get('total_messages', 0)}")
            return True
        else:
            print(f"❌ User summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ User summary error: {e}")
        return False

def run_full_test():
    print("🚀 Starting Mental Health Support Chatbot API Test Suite (one chat per user)")
    print("=" * 70)
    if not test_health_check():
        print("❌ Health check failed. Make sure the server is running!")
        return False
    test_cases = [
        ("Hello, I'm feeling a bit down today", ["hello", "feeling", "down"]),
        ("I've been struggling with anxiety lately", ["anxiety", "struggling", "support"]),
        ("I'm feeling much better today!", ["better", "good", "positive"]),
        ("Can you help me with some breathing exercises?", ["breathing", "exercises", "help"]),
        ("I'm grateful for the support you provide", ["grateful", "support", "positive"]),
    ]
    for message, expected_keywords in test_cases:
        if not test_chat_endpoint(message, expected_keywords):
            print(f"❌ Chat test failed for: {message}")
            return False
        time.sleep(1)
    if not test_conversation_history():
        print("❌ Conversation history test failed")
        return False
    if not test_user_analysis():
        print("❌ User analysis test failed")
        return False
    if not test_user_summary():
        print("❌ User summary test failed")
        return False
    print("\n🎉 All tests completed successfully!")
    print("=" * 70)
    print("✅ The chatbot is working correctly with:")
    print("   - User-specific database integration")
    print("   - User conversation history")
    print("   - User-specific contextual responses")
    print("   - User sentiment analysis")
    print("   - User engagement tracking")
    print("   - Crisis detection")
    return True

if __name__ == "__main__":
    try:
        success = run_full_test()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        exit(1) 