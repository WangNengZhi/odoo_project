import pymysql




def select_db(db_config, select_sql):
    
    """查询"""
    # 建立数据库连接
    db = pymysql.connect(
        host=db_config.get("mysql_ip"),
        port=db_config.get("mysql_port"),
        user=db_config.get("mysql_db_account"),
        passwd=db_config.get("mysql_db_password"),
        db=db_config.get("mysql_db_name"),
    )
    # 通过 cursor() 创建游标对象，并让查询结果以字典格式输出
    cur = db.cursor(cursor=pymysql.cursors.DictCursor)
    # 使用 execute() 执行sql
    cur.execute(select_sql)
    # 使用 fetchall() 获取所有查询结果
    data = cur.fetchall()
    # 关闭游标
    cur.close()
    # 关闭数据库连接
    db.close()

    return data

# select_sql = 'SELECT * FROM user WHERE username="张三"'
# print(select_db(select_sql))