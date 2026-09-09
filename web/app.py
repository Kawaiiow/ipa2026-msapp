import os
from flask import Flask, request, render_template, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
db_name = os.environ.get("DB_NAME", "network_monitoring")

client = MongoClient(mongo_uri)
mydb = client[db_name]
routers_col = mydb["routers"]
status_col = mydb["interface_status"]  # Collection ที่ Worker บันทึกไว้


@app.route("/")
def main():
    routers = list(routers_col.find())
    return render_template("index.html", data=routers)


@app.route("/router/<ip>")
def router_detail(ip):
    router = routers_col.find_one({"ip": ip})
    records = list(status_col.find({"router_ip": ip}).sort("timestamp", -1).limit(5))

    return render_template("router_detail.html", ip=ip, router=router, records=records)


@app.route("/getrouter/<ip>")
def get_router(ip):
    router = routers_col.find_one({"ip": ip})
    if not router:
        return {"error": "Router not found"}, 404
    router["_id"] = str(router["_id"])
    return router


@app.route("/add", methods=["POST"])
def add_router():
    ip = request.form.get("ip")
    username = request.form.get("username")
    password = request.form.get("password")

    if ip and username and password:
        routers_col.insert_one({"ip": ip, "username": username, "password": password})
    return redirect(url_for("main"))


@app.route("/delete", methods=["POST"])
def delete_router():
    router_id = request.form.get("id")
    if router_id:
        try:
            routers_col.delete_one({"_id": ObjectId(router_id)})
        except Exception:
            pass
    return redirect(url_for("main"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
