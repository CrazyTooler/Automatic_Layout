import pymysql

class mysqlCon:
    def getCon(self):
        try:
            conn = pymysql.connect(host="121.196.99.106",port=3306,user="root",password="zzysky123",
            database="textemplate",charset="utf8") 
            return conn
        except Exception as e:
            print("连接数据库失败"+e)
            return e
    #查询所有数据，若查询一个数据则用fetchone函数
    def select(self,sql):
        try:
            con=self.getCon()
            print(con)
            cur=con.cursor()
            count=cur.execute(sql)
            fc=cur.fetchall()
            return fc
        except Exception as e:
            print("Error:%s"%e)
        finally:
            cur.close()
            con.close()
    def insertByParam(self,sql,params):
        try:
            con=self.getCon()
            cur=con.cursor()
            count=cur.execute(sql,params)
            con.commit()
            return count
        except Exception as e:
            con.rollback()
            print("Error:%s"%e)
        finally:
            cur.close()
            con.close()

#sql="insert into pythontest values(%s,%s,%s,now())"  params=(6,'C#','good book') 
