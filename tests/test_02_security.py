"""
测试2: 安全模块 (密码哈希与JWT)
运行: uv run python tests/test_02_security.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.core.security import hash_password, verify_password, create_access_token, decode_access_token


def test_password_hash():
    print("=== 测试密码哈希 ===")
    plain = "mysecret123"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong", hashed)
    print("[PASS] 密码哈希与验证")
    return True


def test_jwt():
    print("=== 测试JWT令牌 ===")
    token = create_access_token(data={"sub": "42"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "42"
    print(f"[PASS] JWT生成与解析: sub={payload['sub']}")

    invalid = decode_access_token("invalid.token.here")
    assert invalid is None
    print("[PASS] 无效令牌返回None")
    return True


if __name__ == "__main__":
    results = []
    results.append(test_password_hash())
    results.append(test_jwt())
    print(f"\n结果: {sum(results)}/{len(results)} 通过")
