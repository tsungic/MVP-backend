from flask import Flask, request, Response
from flask_cors import CORS
import dbcreds
import mariadb
import json
import secrets

app = Flask(__name__)
CORS(app)


@app.route("/api/users", methods=["GET","POST","PATCH","DELETE"])
def users():
    if request.method =="GET":
        user_id = request.args.get("userId")
        conn = None
        cursor = None 
        users_data = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM users where id =?", [user_id])
                users_data = cursor.fetchall()
            else:
                cursor.execute("SELECT * FROM users")
                users_data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
        if users_data or users_data ==[]:
            users_info =[]
            for user in users_data:
                user_dic={
                    "userId": user[0],
                    "email": user [1],
                    "name": user [3]
                }
                users_info.append(user_dic)
            return Response(json.dumps(users_info, default = str), mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)
    if request.method =="POST":
        conn = None
        cursor = None 
        user_info = request.json
        name = user_info.get("name")
        password = user_info.get("password")
        email = user_info.get("email")
        user_session_id = None
        if email!=None and email !="" and name!=None and name !="" and password!=None and password !="" :
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (email, password, name)  VALUES  (?,?,?)", [email, password, name])
                conn.commit()
                user_id = cursor.lastrowid
                login_token= secrets.token_urlsafe(20)
                cursor.execute("INSERT INTO user_session (user_id, loginToken) VALUES (?,?)", [user_id, login_token])
                conn.commit()
                user_session_id = cursor.lastrowid
            except Exception as e:
                print(e)
            finally:
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                if user_session_id != None:
                    user_dic={
                        "userId": user_id,
                        "email": email,
                        "name": name,
                        "loginToken": login_token
                    }
                    return Response(json.dumps(user_dic, default = str), mimetype="application/json", status=200)
                else:
                    return Response("failure", mimetype="html/text", status=400)
    if request.method == "PATCH":
        user_info = request.json
        conn = None
        cursor = None
        name = user_info.get("name")
        password = user_info.get("password")
        email = user_info.get("email")
        login_token = user_info.get("loginToken")
        user= None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            if email != None and email !="" and login_token != None and login_token !="":
                #get userid based on login token
                cursor.execute("SELECT user_id FROM user_session where loginToken = ?",[login_token])
                user_id = cursor.fetchone()[0]
                #can update user table based on user id
                cursor.execute("UPDATE users SET email = ? where id = ?", [email, user_id])
            if name != None and name !="" and login_token != None and login_token !="":
                cursor.execute("SELECT user_id FROM user_session where loginToken = ?",[login_token])
                user_id = cursor.fetchone()[0]
                cursor.execute("UPDATE users SET name = ? where id = ?", [name, user_id])
            if password != None and password !="" and login_token != None and login_token !="":
                cursor.execute("SELECT user_id FROM user_session where loginToken = ?",[login_token])
                user_id = cursor.fetchone()[0]
                cursor.execute("UPDATE users SET password = ? where id = ?", [password, user_id])
            conn.commit()
            row=cursor.rowcount
            cursor.execute("SELECT * FROM users where id = ?", [user_id])
            user = cursor.fetchone()
        except Exception as e:
            print (e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
            if user != None:
                user_dic={
                    "userId": user[0],
                    "email": user [1],
                    "name": user[3]
                }
                return Response(json.dumps(user_dic, default = str), mimetype="application/json", status=200)
            else:
                return Response("failure", mimetype="html/text", status=400)
    if request.method == "DELETE":
        user_info = request.json
        conn = None
        cursor = None
        password = user_info.get("password")
        login_token = user_info.get("loginToken")
        user= None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM user_session WHERE loginToken = ?",[login_token])
            user_id = cursor.fetchone()[0]
            if password != None and password !="" and login_token != None and login_token !="":
                cursor.execute("DELETE FROM users WHERE id = ?",[user_id])
                conn.commit()
                row=cursor.rowcount
        except Exception as e:
            print (e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
        if user == None:
            return Response("Delete successful", mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)



@app.route("/api/login", methods=["POST", "DELETE"])
def login():
    if request.method == "POST":
        conn = None
        cursor = None 
        users_data = None
        user_info = request.json
        password = user_info.get("password")
        email = user_info.get("email")
        login_rows = None
        user_data = None
        if email !="" and email !=None and password !="" and password !=None:
            try:
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users where email =? AND password =?", [email, password])
                user_data = cursor.fetchone()
                rows = cursor.rowcount
                #to login need user id, can get from fetch one(which hold all user data)
                if (user_data != None):
                    #user id is first row in db-0
                    user_id = user_data[0]
                    login_token = secrets.token_urlsafe(20)
                    cursor.execute("INSERT INTO user_session (user_id, loginToken) VALUES (?,?)",[user_id, login_token])
                    conn.commit()
                    #login_rows check if insertion is done correct
                    login_rows = cursor.rowcount
            except Exception as e:
                print(e)
            finally: 
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                #determine if login is working or not
                if(login_rows != None):
                    #return user date
                    user_dic = {
                        "userId": user_data[0],
                        "email": user_data [1],
                        "name": user_data[3],
                        "loginToken": login_token
                    }
                    return Response(json.dumps(user_dic, default = str), mimetype="application/json", status=200)
                else:
                    return Response("failure", mimetype="html/text", status=400)
    if request.method =="DELETE":
        login_token = request.json.get("loginToken")
        rows = None
        if login_token != None and login_token !="":
            try: 
                conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM user_session where loginToken = ?", [login_token])
                conn.commit()
                rows = cursor.rowcount
            except Exception as e:
                print(e)
            finally:
                if(cursor !=None):
                    cursor.close()
                if(conn != None):
                    conn.rollback()
                    conn.close()
                if (rows == 1):
                    return Response("logout success", mimetype="text/html", status =204)
                else:
                    return Response ("logout failed",  mimetype="text/html", status =404)



                    

@app.route("/api/place", methods=["GET","POST","PATCH","DELETE"])
def place():
    if request.method =="GET":
        place_id = request.args.get("placeId")
        conn = None
        cursor = None 
        place_data = None
        try:
            conn = mariadb .connect(user=dbcreds.user, password=dbcreds.password, host= dbcreds.host, port= dbcreds.port, database= dbcreds.database)
            cursor = conn.cursor()
            if user_id:
                cursor.execute("SELECT * FROM users u INNER JOIN place p ON u.id = p.user_id WHERE u.id = ?", [user_id])
                tweet_data = cursor.fetchall()
            else:
                #if you want all places
                cursor.execute("SELECT * FROM users u INNER JOIN place p ON u.id = p.user_id")
                tweet_data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if(cursor !=None):
                cursor.close()
            if(conn != None):
                conn.rollback()
                conn.close()
                #if there is tweet data or if it is empty
        if place_data or place_data ==[]:
            place_info =[]
            #create for loop
            for tweet in tweet_data:
                tweet_dic={
                    "tweetId": tweet[6],
                    "userId": tweet [0],
                    "username": tweet[5],
                    "content": tweet [8],
                    "createdAt": tweet [9]
                }
                tweet_info.append(tweet_dic)
            return Response(json.dumps(tweet_info, default = str), mimetype="application/json", status=200)
        else:
            return Response("failure", mimetype="html/text", status=400)
