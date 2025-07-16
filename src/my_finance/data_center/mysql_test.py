# main.py (示例文件)

from mysql_util import get_cursor


def add_new_user(email, password):
    """添加一个新用户"""
    try:
        with get_cursor() as cursor:
            sql = "INSERT INTO `users` (`email`, `password`) VALUES (%s, %s)"
            cursor.execute(sql, (email, password))
            print(f"User '{email}' added successfully.")
            # 注意：事务在 with 代码块成功结束后自动提交
    except Exception as e:
        print(f"Failed to add user: {e}")


def get_user_by_id(user_id):
    """根据ID查询用户"""
    try:
        with get_cursor() as cursor:
            sql = "SELECT id, email FROM `users` WHERE id = %s"
            cursor.execute(sql, (user_id,))
            result = cursor.fetchone()
            return result
    except Exception as e:
        print(f"Failed to get user: {e}")
        return None


if __name__ == '__main__':
    # 示例用法
    add_new_user('pool_user@example.com', 'a_very_secure_password')

    user = get_user_by_id(1)
    if user:
        print("Fetched user:", user)
    else:
        print("User with id=1 not found.")

    # 再次查询，验证连接复用
    user2 = get_user_by_id(2)
    if user2:
        print("Fetched user:", user2)
    else:
        print("User with id=2 not found.")